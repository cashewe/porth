import json
from pathlib import Path

from ._loader import Loader


class Routes(Loader):
    def load(self):
        """Load routes from the specified root directory."""
        root_path = Path(self.root)
        if not root_path.exists():
            return

        self.loaded = {}

        for file in sorted(root_path.rglob("route.json")):
            with file.open("r", encoding="utf-8") as f:
                route_data = json.load(f)

            self.loaded[file.parent.name] = route_data

    def info(self):
        return list(self.loaded.keys())


routes = Routes()
