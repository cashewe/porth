import structlog
from camau import Router

from .route_loader import routes
from .schema_loader import schemas
from .task_loader import tasks
from .version_handler import RouteKey, VersionHandler

logger = structlog.get_logger(__name__)


class ConfigManager:
    def __init__(self):
        self._routes = routes
        self._tasks = tasks
        self.schemas = schemas  # we will validate against this if provided only.
        self.configs: dict[RouteKey, Router] = {}
        self._versions = VersionHandler()

    def load(self):
        self.configs = {}
        for key, config in self._routes.items():
            logger.debug(
                "initialising router object",
                route=key.name,
                version=key.major,
            )
            route_tasks = self._tasks.get(key)
            self.configs[key] = Router(config, route_tasks)
        self._versions = VersionHandler(self.configs)

    def info(self, route: str | None = None, version: int | None = None):
        if route is None:
            return [
                {
                    "route": key.name,
                    "version": key.major,
                    "tasks": list(self._tasks.get(key, {})),
                    "schema": self.schemas.get(key),
                }
                for key in sorted(self.configs)
            ]
        key = self.resolve(route, version)
        return self._routes[key]

    def resolve(self, route: str, version: int | None = None) -> RouteKey:
        return self._versions.resolve(route, version)

    def router(self, route: str, version: int | None = None) -> Router:
        return self.configs[self.resolve(route, version)]

    def schema(self, route: str, version: int | None = None):
        return self.schemas.get(self.resolve(route, version))

    def available_versions(self, route: str) -> list[int]:
        return self._versions.available(route)

    def keys(self):
        return self._versions.routes()

    def __len__(self):
        return len(self.configs)

    def __contains__(self, key):
        if isinstance(key, RouteKey):
            return key in self.configs
        return self._versions.contains(key)

    def __getitem__(self, key):
        if isinstance(key, RouteKey):
            return self.configs[key]
        return self.router(key)


manager = ConfigManager()
manager.load()
