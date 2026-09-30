import json
from pathlib import Path

import structlog

from ._loader import Loader
from .version_handler import VersionHandler

logger = structlog.get_logger(__name__)


class Routes(Loader):
    def load(self):
        """Load routes from the specified root directory."""
        root_path = Path(self.root)

        logger.info(f"discovering route configs in {root_path}")
        if not root_path.exists():
            return

        self.loaded = {}

        for key, directory in VersionHandler.discover(root_path).items():
            file = directory / "route.json"
            with file.open("r", encoding="utf-8") as f:
                route_data = json.load(f)

            self.loaded[key] = route_data
            logger.debug(
                "loaded routing config",
                route=key.name,
                version=key.major,
            )

    def info(self):
        return list(self.loaded)


routes = Routes()
