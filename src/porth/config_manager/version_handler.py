import re
from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from .._errors import RouteVersionNotFoundError

VERSION_DIRECTORY = re.compile(r"v(?P<major>[1-9][0-9]*)")


@dataclass(frozen=True, order=True)
class RouteKey:
    """The stable identity of a configured route."""

    name: str
    major: int


class VersionHandler:
    """Discover and resolve the major versions available for each route."""

    def __init__(self, keys: Iterable[RouteKey] = ()) -> None:
        versions: dict[str, list[int]] = defaultdict(list)
        for key in keys:
            versions[key.name].append(key.major)
        self._versions = {
            route: tuple(sorted(route_versions))
            for route, route_versions in versions.items()
        }

    @staticmethod
    def discover(root: str | Path) -> dict[RouteKey, Path]:
        """Find valid route directories and enforce layout invariants."""
        root_path = Path(root)
        discovered: dict[RouteKey, Path] = {}
        layout_styles: dict[str, set[str]] = defaultdict(set)

        if not root_path.exists():
            return discovered

        for config_path in sorted(root_path.rglob("route.json")):
            directory = config_path.parent
            relative = directory.relative_to(root_path)

            if len(relative.parts) == 1:
                route_name = relative.parts[0]
                major = 1
                style = "implicit"
            elif len(relative.parts) == 2:
                route_name, version_directory = relative.parts
                match = VERSION_DIRECTORY.fullmatch(version_directory)
                if match is None:
                    raise ValueError(
                        "Versioned route directories must match v[1-9][0-9]*: "
                        f"{directory}"
                    )
                major = int(match.group("major"))
                style = "explicit"
            else:
                raise ValueError(
                    "Routes must use <route>/ or <route>/v<major>/ directories: "
                    f"{directory}"
                )

            layout_styles[route_name].add(style)
            key = RouteKey(route_name, major)
            if key in discovered:
                raise ValueError(
                    f"Route {route_name!r} defines major version {major} more than once"
                )
            discovered[key] = directory

        for route_name, styles in layout_styles.items():
            if len(styles) > 1:
                raise ValueError(
                    f"Route {route_name!r} mixes implicit and explicit versions; "
                    "move v1 into an explicit v1 directory"
                )

        return discovered

    def routes(self) -> tuple[str, ...]:
        return tuple(sorted(self._versions))

    def contains(self, route: str) -> bool:
        return route in self._versions

    def available(self, route: str) -> list[int]:
        return list(self._versions.get(route, ()))

    def resolve(self, route: str, version: int | None = None) -> RouteKey:
        available = self.available(route)
        if not available:
            raise KeyError(route)

        if version is None:
            version = available[-1]
        elif version not in available:
            raise RouteVersionNotFoundError(route, version, available)

        return RouteKey(route, version)
