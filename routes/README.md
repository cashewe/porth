# Routes

This is where you can define your routes for the service - either in the repo, or as an additional layer on the service image.

each route will need:

- its own directory, which becomes the route name
- a `route.json`, containing a valid camau configuration json
- a `tasks.py` file, defining a dictionary, 'tasks', containing async callers that map to routing tasks names
- [OPTIONAL] a `schema.json` file, defining the schema for route to validate incoming messages with.

