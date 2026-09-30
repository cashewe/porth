# Routes

This is where you can define your routes for the service - either in the repo, or as an additional layer on the service image.

each route will need:

- its own directory, which becomes the route name
- a `route.json`, containing a valid camau configuration json
- a `tasks.py` file, defining a dictionary, 'tasks', containing async callers that map to routing tasks names
- [OPTIONAL] a `schema.json` file, defining the schema for route to validate incoming messages with.

## Versions

A route with no version directories is implicitly version 1:

```text
routes/example-2/route.json
```

As soon as a route has an explicit version, every version of that route must be
explicit:

```text
routes/example-1/v1/route.json
routes/example-1/v2/route.json
```

Explicit versions must be positive major versions named `v1`, `v2`, and so on.
They do not need to be consecutive or start at v1. Mixing an implicit v1 with
an explicit version is rejected during startup.

Call a specific version through `/route/{route}/v{version}`. Omitting the
version calls the highest available version, so consumers that require a stable
contract should always use an explicit version.

