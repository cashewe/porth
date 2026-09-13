import json
from pathlib import Path

from porth.config_manager.route_loader import Routes


def test_default_root_resolves_to_project_routes_directory():
    routes = Routes()

    assert Path(routes.root).is_absolute()
    assert Path(routes.root).name == "routes"
    assert Path(routes.root).exists()


def test_load_finds_route_json_files_in_child_directories(tmp_path):
    alpha_route = tmp_path / "alpha" / "route.json"
    beta_route = tmp_path / "beta" / "route.json"
    alpha_route.parent.mkdir()
    beta_route.parent.mkdir()
    alpha_route.write_text(json.dumps({"name": "alpha"}))
    beta_route.write_text(json.dumps({"name": "beta"}))

    routes = Routes(root=str(tmp_path))
    routes.load()

    assert routes.loaded == {
        "alpha": {"name": "alpha"},
        "beta": {"name": "beta"},
    }


def test_load_ignores_non_route_json_files_in_directory(tmp_path):
    (tmp_path / "alpha" / "route.json").parent.mkdir()
    (tmp_path / "alpha" / "route.json").write_text(json.dumps({"name": "alpha"}))
    (tmp_path / "beta.json").write_text(json.dumps({"name": "beta"}))
    (tmp_path / "notes.txt").write_text("ignore me")
    (tmp_path / "image.png").write_text("ignore me too")
    (tmp_path / "nested_dir").mkdir()

    routes = Routes(root=str(tmp_path))
    routes.load()

    assert routes.loaded == {"alpha": {"name": "alpha"}}
