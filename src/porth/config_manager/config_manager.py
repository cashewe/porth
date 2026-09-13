from camau import Router

from .route_loader import routes
from .task_loader import tasks


class ConfigManager:
    def __init__(self):
        self._routes = routes
        self._tasks = tasks
        self.configs = {}

    def load(self):
        for route, config in self._routes.items():
            tasks = self._tasks.get(route)
            self.configs[route] = Router(config, tasks)

    def info(self):
        return [
            {"route": route, "tasks": list(tasks)}
            for route, tasks in self._tasks.items()
        ]

    def __len__(self):
        return len(self.configs)

    def __contains__(self, key):
        return key in self.configs


manager = ConfigManager()
manager.load()
