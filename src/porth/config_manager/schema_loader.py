import json
from pathlib import Path

import structlog

from ._loader import Loader

logger = structlog.get_logger(__name__)


class Schemas(Loader):
    def load(self):
        """Load schemas from the specified root directory."""
        root_path = Path(self.root)

        logger.info(f"discovering schemas in {root_path}")
        if not root_path.exists():
            return

        self.loaded = {}

        for file in sorted(root_path.rglob("schema.json")):
            with file.open("r", encoding="utf-8") as f:
                route_data = json.load(f)

            self.loaded[file.parent.name] = route_data
            logger.debug(f"loaded schema for {file.parent.name}!")

    def info(self):
        return list(self.loaded)


schemas = Schemas()
