from porth.config_manager.task_loader import Tasks


def test_tasks_loads_tasks_for_each_route_directory(tmp_path):
    alpha_dir = tmp_path / "example-1"
    beta_dir = tmp_path / "example-2"
    alpha_dir.mkdir()
    beta_dir.mkdir()
    (alpha_dir / "tasks.py").write_text("tasks = {'alpha-task': 'alpha-value'}\n")
    (beta_dir / "tasks.py").write_text("tasks = {'beta-task': 'beta-value'}\n")

    tasks = Tasks(root=str(tmp_path))

    assert tasks.loaded == {
        "example-1": {"alpha-task": "alpha-value"},
        "example-2": {"beta-task": "beta-value"},
    }


def test_tasks_default_root_loads_repo_example_directories():
    tasks = Tasks()

    assert set(tasks.loaded) == {"example-1", "example-2"}
    assert set(tasks.loaded["example-1"]) == {
        "fraud-checker",
        "policy-checker",
    }
    assert set(tasks.loaded["example-2"]) == {
        "stable-predictor",
        "candidate-predictor",
        "fraud-checker",
        "policy-checker",
        "risk-scorer",
        "review-queue",
        "approval-service",
    }
