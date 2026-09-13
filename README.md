# porth
configurable gateway service API

welsh - meaning 'gateway'

ok so:

- dockerise and sent to dockerhub
- include suggested helm chart for deploying you configs in the repo
- for every config, we want:
  - /score hits the route
  - /info returns the config
  - /readyz for can we hit the various requirements...
- use the cli tools for deployment pipelines
- include instructions for wrapping the core image with new registered tasks.
- use camau as the routing logic

- fast mcp option