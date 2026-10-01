from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from ..settings import settings


class Loader(ABC):
    def __init__(self, root: str | Path | None = None):
        root_path = Path(root) if root is not None else settings.routes_dir
        if not root_path.is_absolute():
            root_path = Path.cwd() / root_path

        self.root = str(root_path)
        self.loaded = {}
        if root_path.exists():
            self.load()

    @abstractmethod
    def load(self) -> None:
        """Load routes from the specified root directory."""
        ...

    @abstractmethod
    def info(self) -> Any:
        """Get information about the loaded values."""
        ...

    def __len__(self):
        return len(self.loaded)

    def __getitem__(self, key):
        return self.loaded[key]

    def __contains__(self, key):
        return key in self.loaded

    def __str__(self):
        return f"Loader(root={self.root}, loaded={list(self.loaded.keys())})"

    def keys(self):
        return self.loaded.keys()

    def values(self):
        return self.loaded.values()

    def items(self):
        return self.loaded.items()

    def get(self, key, default=None):
        return self.loaded.get(key, default)
