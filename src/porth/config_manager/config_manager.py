import structlog
from camau import Router

from .route_loader import routes
from .schema_loader import schemas
from .task_loader import tasks

logger = structlog.get_logger(__name__)


class ConfigManager:
    def __init__(self):
        self._routes = routes
        self._tasks = tasks
        self.schemas = schemas  # we will validate against this if provided only.
        self.configs = {}

    def load(self):
        for route, config in self._routes.items():
            logger.debug(f"initialising router object for {route}...")
            tasks = self._tasks.get(route)
            self.configs[route] = Router(config, tasks)

    def info(self, route: str | None = None):
        if route is None:
            return [
                {
                    "route": route_name,
                    "tasks": list(tasks),
                    "schema": self.schemas.get(route_name),
                }
                for route_name, tasks in self._tasks.items()
            ]
        return self._routes[route]

    def keys(self):
        return self.configs.keys()

    def __len__(self):
        return len(self.configs)

    def __contains__(self, key):
        return key in self.configs

    def __getitem__(self, key):
        return self.configs[key]


manager = ConfigManager()
manager.load()
