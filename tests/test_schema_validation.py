import asyncio
import json
from copy import deepcopy
from pathlib import Path

import pytest
from camau import Assessor, Router, RoutingSelectionError
from camau.types import JsonObject
from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError

from porth.config_manager import manager
from porth.config_manager.schema_loader import Schemas
from porth.config_manager.task_loader import tasks
from porth.config_manager.version_handler import RouteKey
from porth.routes.specified import explain, route

ROUTES_DIRECTORY = Path(__file__).resolve().parents[1] / "routes"

VALID_REQUESTS: dict[str, JsonObject] = {
    "example-1": {
        "transaction": {
            "id": "txn-123",
            "amount": 1_500.0,
            "currency": "GBP",
        },
        "customer": {
            "id": "customer-456",
            "country": "GB",
            "account-age-days": 365,
        },
    },
    "example-2": {
        "request": {"id": "request-123", "channel": "api"},
        "customer": {
            "id": "customer-456",
            "country": "GB",
            "account-age-days": 365,
        },
        "transaction": {"amount": 125.0, "currency": "GBP"},
    },
}

REQUIRED_PATHS = {
    "example-1": [
        ("transaction",),
        ("transaction", "id"),
        ("transaction", "amount"),
        ("transaction", "currency"),
        ("customer",),
        ("customer", "id"),
        ("customer", "country"),
        ("customer", "account-age-days"),
    ],
    "example-2": [
        ("request",),
        ("request", "id"),
        ("request", "channel"),
        ("customer",),
        ("customer", "id"),
        ("customer", "country"),
        ("customer", "account-age-days"),
        ("transaction",),
        ("transaction", "amount"),
        ("transaction", "currency"),
    ],
}

CONFIGURED_ROUTE_KEYS = [
    RouteKey("example-1", 1),
    RouteKey("example-1", 2),
    RouteKey("example-2", 1),
]


def load_route_file(
    route_name: str,
    filename: str,
    version: int | None = None,
) -> JsonObject:
    key = manager.resolve(route_name, version)
    route_directory = ROUTES_DIRECTORY / route_name
    explicit_directory = route_directory / f"v{key.major}"
    if explicit_directory.exists():
        route_directory = explicit_directory
    route_file = route_directory / filename
    return json.loads(route_file.read_text(encoding="utf-8"))


@pytest.mark.parametrize("key", CONFIGURED_ROUTE_KEYS)
def test_example_schema_is_valid_json_schema(key: RouteKey) -> None:
    Draft202012Validator.check_schema(
        load_route_file(key.name, "schema.json", key.major)
    )


@pytest.mark.parametrize("key", CONFIGURED_ROUTE_KEYS)
def test_example_schema_accepts_complete_request(key: RouteKey) -> None:
    validator = Draft202012Validator(
        load_route_file(key.name, "schema.json", key.major)
    )

    validator.validate(VALID_REQUESTS[key.name])


@pytest.mark.parametrize(
    ("key", "missing_path"),
    [(key, path) for key in CONFIGURED_ROUTE_KEYS for path in REQUIRED_PATHS[key.name]],
)
def test_example_schema_rejects_request_missing_required_field(
    key: RouteKey,
    missing_path: tuple[str, ...],
) -> None:
    payload = deepcopy(VALID_REQUESTS[key.name])
    containing_object: JsonObject = payload
    for segment in missing_path[:-1]:
        nested_object = containing_object[segment]
        assert isinstance(nested_object, dict)
        containing_object = nested_object
    del containing_object[missing_path[-1]]

    validator = Draft202012Validator(
        load_route_file(key.name, "schema.json", key.major)
    )

    with pytest.raises(ValidationError):
        validator.validate(payload)


@pytest.mark.parametrize("key", CONFIGURED_ROUTE_KEYS)
def test_route_configuration_passes_camau_assessment(key: RouteKey) -> None:
    assessment = Assessor.assess(load_route_file(key.name, "route.json", key.major))

    assert assessment.valid, assessment.to_text()


@pytest.mark.parametrize("key", CONFIGURED_ROUTE_KEYS)
def test_every_configured_task_is_registered(key: RouteKey) -> None:
    configuration = load_route_file(key.name, "route.json", key.major)
    nodes = configuration["nodes"]
    assert isinstance(nodes, list)
    required_tasks: set[str] = set()
    for node in nodes:
        assert isinstance(node, dict)
        if node.get("type") == "task":
            task_name = node.get("task")
            assert isinstance(task_name, str)
            required_tasks.add(task_name)

    assert set(tasks[key]) == required_tasks


def test_schema_loader_discovers_schema_by_route_directory(tmp_path: Path) -> None:
    schema = {"type": "object", "required": ["message"]}
    route_directory = tmp_path / "messages"
    route_directory.mkdir()
    (route_directory / "route.json").write_text("{}", encoding="utf-8")
    (route_directory / "schema.json").write_text(json.dumps(schema), encoding="utf-8")

    schemas = Schemas(root=tmp_path)

    assert schemas.loaded == {RouteKey("messages", 1): schema}


def test_example_1_runs_fraud_and_policy_checks() -> None:
    result = asyncio.run(route("example-1", VALID_REQUESTS["example-1"]))

    assert result == {
        "fraud": {
            "transaction-id": "txn-123",
            "risk-score": 0.4,
            "requires-review": False,
        },
        "policy": {
            "transaction-id": "txn-123",
            "approved": True,
            "reason": "accepted",
        },
    }


def test_example_1_v1_remains_available_explicitly() -> None:
    result = asyncio.run(route("example-1", VALID_REQUESTS["example-1"], 1))

    assert result["fraud"] == {
        "transaction-id": "txn-123",
        "risk-score": 0.6,
        "requires-review": True,
    }


@pytest.mark.parametrize(
    ("seed", "expected_model", "expected_risk_score"),
    [(0, "stable", 0.2), (1, "candidate", 0.3)],
)
def test_example_2_api_request_is_scored_and_approved(
    seed: int,
    expected_model: str,
    expected_risk_score: float,
) -> None:
    configured_router = Router(
        load_route_file("example-2", "route.json"),
        tasks[RouteKey("example-2", 1)],
        seed=seed,
    )

    result = asyncio.run(configured_router.run(VALID_REQUESTS["example-2"]))

    assert result == {
        "request-id": "request-123",
        "decision": "approved",
        "reviewed": False,
        "model": expected_model,
        "risk-score": expected_risk_score,
    }


def test_example_2_batch_request_is_sent_for_manual_review() -> None:
    payload = deepcopy(VALID_REQUESTS["example-2"])
    request = payload["request"]
    customer = payload["customer"]
    assert isinstance(request, dict)
    assert isinstance(customer, dict)
    request["channel"] = "batch"
    customer["account-age-days"] = 7

    result = asyncio.run(route("example-2", payload))

    assert result == {
        "request-id": "request-123",
        "decision": "manual-review",
        "reviewed": True,
        "model": "batch",
        "risk-score": 0.6,
    }


def test_example_2_rejects_unsupported_currency() -> None:
    payload = deepcopy(VALID_REQUESTS["example-2"])
    transaction = payload["transaction"]
    assert isinstance(transaction, dict)
    transaction["currency"] = "JPY"

    with pytest.raises(RoutingSelectionError, match="aggregate risk exceeds"):
        asyncio.run(route("example-2", payload))


@pytest.mark.parametrize("endpoint", [route, explain])
def test_specified_endpoint_rejects_invalid_request_before_execution(endpoint) -> None:
    payload = deepcopy(VALID_REQUESTS["example-2"])
    request = payload["request"]
    assert isinstance(request, dict)
    request["channel"] = "email"

    with pytest.raises(ValidationError):
        asyncio.run(endpoint("example-2", payload))


@pytest.mark.parametrize("key", CONFIGURED_ROUTE_KEYS)
def test_all_registered_tasks_are_healthy(key: RouteKey) -> None:
    results = asyncio.run(manager[key].healthcheck())

    assert results
    assert all(results.values())
