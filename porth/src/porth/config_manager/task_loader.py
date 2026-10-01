import importlib.util
from pathlib import Path

import structlog

from ._loader import Loader
from .version_handler import VersionHandler

logger = structlog.get_logger(__name__)


class Tasks(Loader):
    def load(self):
        """Load tasks from each child directory in the routes root."""
        root_path = Path(self.root)

        logger.info(f"discovering configs in {root_path}...")
        self.loaded = {}
        for key, directory in VersionHandler.discover(root_path).items():
            tasks_path = directory / "tasks.py"
            if not tasks_path.exists():
                logger.debug(
                    "route contains no tasks",
                    route=key.name,
                    version=key.major,
                )
                continue  # some users may just have no tasks?

            spec = importlib.util.spec_from_file_location(
                f"porth_tasks_{key.name.replace('-', '_')}_v{key.major}",
                tasks_path,
            )
            if spec is None or spec.loader is None:
                raise ImportError(f"Could not load tasks from {tasks_path}")

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            self.loaded[key] = module.tasks
            logger.debug("loaded tasks", route=key.name, version=key.major)

    def info(self):
        return {key: list(value.keys()) for key, value in self.loaded.items()}


tasks = Tasks()
