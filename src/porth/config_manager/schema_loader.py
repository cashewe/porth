import json
from pathlib import Path

import structlog

from ._loader import Loader
from .version_handler import VersionHandler

logger = structlog.get_logger(__name__)


class Schemas(Loader):
    def load(self):
        """Load schemas from the specified root directory."""
        root_path = Path(self.root)

        logger.info(f"discovering schemas in {root_path}")
        if not root_path.exists():
            return

        self.loaded = {}

        for key, directory in VersionHandler.discover(root_path).items():
            file = directory / "schema.json"
            if not file.exists():
                continue
            with file.open("r", encoding="utf-8") as f:
                route_data = json.load(f)

            self.loaded[key] = route_data
            logger.debug("loaded schema", route=key.name, version=key.major)

    def info(self):
        return list(self.loaded)


schemas = Schemas()
