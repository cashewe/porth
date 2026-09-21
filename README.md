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
- routing endpoint
- route loader / camau wrapper looks like its mostly done to me tbh...

up next we need:
- structured errors
- write second docker container for wrapping the config
- write pipeline for deploying core behaviour to dockerhub
- write helm for config files
- write template you can use for cloning the routes bit into your own repo for fast setup
- look for runtime gains if neccessary
etc...

## Local tracing with Jaeger

The local observability stack uses Jaeger 2.21 as an ephemeral trace backend:

- `localhost:4317` accepts OTLP traces over gRPC from Porth.
- `http://localhost:16686` serves the Jaeger query UI.
- Trace data is held in memory and is lost when the container is removed.
- Both ports bind only to the local machine; they are not exposed on the LAN.

Start Jaeger before starting the API:

```shell
make observability-up
make run
```

If `make` is unavailable, use the underlying commands:

```shell
docker compose up -d jaeger
uv run fastapi dev src/porth/app.py --reload
```

Send a request and let Porth generate the correlation ID:

```powershell
curl.exe -i http://localhost:8000/info
```

The response includes an `X-Correlation-ID` header. The request logs contain
that same `correlation_id`, plus the OpenTelemetry `trace_id` and `span_id`.

To choose the correlation ID yourself in PowerShell:

```powershell
$correlationId = [guid]::NewGuid().ToString()
Invoke-WebRequest http://localhost:8000/info `
  -Headers @{ "X-Correlation-ID" = $correlationId }
```

Open `http://localhost:16686` and:

1. Select `porth` in the **Service** list.
2. Select an operation or leave **Operation** as `all`.
3. To find one request, enter
   `porth.correlation_id=<the X-Correlation-ID value>` in **Tags**.
4. Select **Find Traces**, then open the result to inspect its spans, timings,
   HTTP attributes, status, and `porth.correlation_id` tag.
5. Compare the trace ID in Jaeger with the `trace_id` in the JSON request log.

The SDK batches spans, so a new trace can take a few seconds to appear.

Jaeger accepts traces but does not store OpenTelemetry metrics. Porth therefore
creates its meter provider without a network exporter by default. To send
metrics to a separate OTLP-compatible backend, set
`OTEL_EXPORTER_OTLP_METRICS_ENDPOINT` to that backend's gRPC endpoint.

Useful lifecycle commands:

```shell
make observability-logs
make observability-down
```
