import importlib.util
from pathlib import Path

import structlog

from ._loader import Loader

logger = structlog.get_logger(__name__)


class Tasks(Loader):
    def load(self):
        """Load tasks from each child directory in the routes root."""
        root_path = Path(self.root)

        logger.info(f"discovering configs in {root_path}...")
        for child in sorted(root_path.iterdir()):
            if not child.is_dir():
                continue

            tasks_path = child / "tasks.py"
            if not tasks_path.exists():
                logger.debug(f"directory {child} contains no tasks!")
                continue  # some users may just have no tasks?

            spec = importlib.util.spec_from_file_location(
                f"porth_tasks_{child.name}",
                tasks_path,
            )
            if spec is None or spec.loader is None:
                raise ImportError(f"Could not load tasks from {tasks_path}")

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            self.loaded[child.name] = module.tasks
            logger.debug(f"successfully loaded tasks for {child}")

    def info(self):
        return {key: list(value.keys()) for key, value in self.loaded.items()}


tasks = Tasks()
