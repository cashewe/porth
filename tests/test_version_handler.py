import json

import pytest

from porth._errors import RouteVersionNotFoundError
from porth.config_manager.version_handler import RouteKey, VersionHandler


def write_route(directory, name: str) -> None:
    directory.mkdir(parents=True)
    (directory / "route.json").write_text(json.dumps({"name": name}))


def test_discovers_implicit_v1(tmp_path):
    route_directory = tmp_path / "alpha"
    write_route(route_directory, "alpha")

    assert VersionHandler.discover(tmp_path) == {
        RouteKey("alpha", 1): route_directory,
    }


def test_discovers_explicit_versions_without_requiring_v1(tmp_path):
    v2_directory = tmp_path / "alpha" / "v2"
    v4_directory = tmp_path / "alpha" / "v4"
    write_route(v2_directory, "alpha-v2")
    write_route(v4_directory, "alpha-v4")

    assert VersionHandler.discover(tmp_path) == {
        RouteKey("alpha", 2): v2_directory,
        RouteKey("alpha", 4): v4_directory,
    }


def test_rejects_mixed_implicit_and_explicit_versions(tmp_path):
    write_route(tmp_path / "alpha", "implicit-alpha")
    write_route(tmp_path / "alpha" / "v2", "alpha-v2")

    with pytest.raises(ValueError, match="mixes implicit and explicit"):
        VersionHandler.discover(tmp_path)


@pytest.mark.parametrize("directory_name", ["v0", "v01", "V2", "v2-beta"])
def test_rejects_invalid_explicit_version_directories(tmp_path, directory_name):
    write_route(tmp_path / "alpha" / directory_name, "alpha")

    with pytest.raises(ValueError, match="must match"):
        VersionHandler.discover(tmp_path)


def test_unversioned_resolution_selects_highest_available_version():
    versions = VersionHandler(
        [RouteKey("alpha", 2), RouteKey("alpha", 4), RouteKey("beta", 1)]
    )

    assert versions.resolve("alpha") == RouteKey("alpha", 4)
    assert versions.resolve("beta") == RouteKey("beta", 1)


def test_missing_version_error_lists_every_available_version():
    versions = VersionHandler([RouteKey("alpha", 2), RouteKey("alpha", 4)])

    with pytest.raises(RouteVersionNotFoundError) as captured:
        versions.resolve("alpha", 3)

    assert captured.value.route == "alpha"
    assert captured.value.requested_version == 3
    assert captured.value.available_versions == [2, 4]
