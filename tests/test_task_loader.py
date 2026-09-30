from porth.config_manager.task_loader import Tasks
from porth.config_manager.version_handler import RouteKey


def test_tasks_loads_tasks_for_each_route_directory(tmp_path):
    alpha_dir = tmp_path / "example-1"
    beta_dir = tmp_path / "example-2"
    alpha_dir.mkdir()
    beta_dir.mkdir()
    (alpha_dir / "route.json").write_text("{}\n")
    (beta_dir / "route.json").write_text("{}\n")
    (alpha_dir / "tasks.py").write_text("tasks = {'alpha-task': 'alpha-value'}\n")
    (beta_dir / "tasks.py").write_text("tasks = {'beta-task': 'beta-value'}\n")

    tasks = Tasks(root=str(tmp_path))

    assert tasks.loaded == {
        RouteKey("example-1", 1): {"alpha-task": "alpha-value"},
        RouteKey("example-2", 1): {"beta-task": "beta-value"},
    }


def test_tasks_default_root_loads_repo_example_directories():
    tasks = Tasks()

    assert set(tasks.loaded) == {
        RouteKey("example-1", 1),
        RouteKey("example-1", 2),
        RouteKey("example-2", 1),
    }
    assert set(tasks.loaded[RouteKey("example-1", 1)]) == {
        "fraud-checker",
        "policy-checker",
    }
    assert set(tasks.loaded[RouteKey("example-1", 2)]) == {
        "fraud-checker",
        "policy-checker",
    }
    assert set(tasks.loaded[RouteKey("example-2", 1)]) == {
        "stable-predictor",
        "candidate-predictor",
        "batch-predictor",
        "fraud-checker",
        "policy-checker",
        "risk-scorer",
        "risk-aggregator",
        "review-queue",
        "approval-service",
    }
