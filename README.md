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

nice to haves:
- fast mcp option

up next we need:
- write second docker container for wrapping the config
- write some metrics
- fix the fastmcp solution so its actually an established app in the lifetime of the fastapi app
- write versioning system
- add config singleton to core codebase
- write pipeline for deploying core behaviour to dockerhub
- write helm for config files
- write template you can use for cloning the routes bit into your own repo for fast setup
- look for runtime gains if neccessary
etc...
