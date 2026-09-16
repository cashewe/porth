import json
from pathlib import Path

import structlog

from ._loader import Loader


logger = structlog.get_logger(__name__)


class Routes(Loader):
    def load(self):
        """Load routes from the specified root directory."""
        root_path = Path(self.root)

        logger.info(f"discovering route configs in {root_path}")
        if not root_path.exists():
            return

        self.loaded = {}

        for file in sorted(root_path.rglob("route.json")):
            with file.open("r", encoding="utf-8") as f:
                route_data = json.load(f)

            self.loaded[file.parent.name] = route_data
            logger.debug(f"loaded routing config for {file.parent.name}!")

    def info(self):
        return list(self.loaded)


routes = Routes()
