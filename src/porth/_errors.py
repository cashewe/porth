class RouteVersionNotFoundError(LookupError):
    """Raised when a route exists but the requested major version does not."""

    def __init__(
        self,
        route: str,
        requested_version: int,
        available_versions: list[int],
    ) -> None:
        self.route = route
        self.requested_version = requested_version
        self.available_versions = available_versions
        super().__init__(
            f"Version v{requested_version} is not available for route {route!r}"
        )
