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

currently implemented:
- global info
- global health
- fake global ready
- dummied routing endpoint
- route loader / camau wrapper looks like its mostly done to me tbh...

up next we need:
- undummy the routing endpoint
- find a way to map routing endpoints per config as part of init, such that they all get visibly rendered on screen different
- add scaffold things like otel etc...
- write second docker container for wrapping the config
- write pipeline for deploying core behaviour to dockerhub
- write helm for config files
- write template you can use for cloning the routes bit into your own repo for fast setup
- look for runtime gains if neccessary
etc...