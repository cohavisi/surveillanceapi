# Surveillance API — Design Specification

## 1. Overview

The Surveillance API is a lightweight Python REST service built with **FastAPI**, **Uvicorn**, and **Pydantic**. It provides foundational endpoints (`/health`, `/hello`) and a structured JSON logging system that adapts to two deployment contexts: **local** development and **Kubernetes (k8s)**.

## 2. Goals

| Goal | Description |
|------|-------------|
| Minimal viable service | Ship a running API with health-check and greeting endpoints. |
| Structured observability | Emit machine-parseable JSON logs from day one. |
| Dual-context logging | Seamlessly switch log enrichment between local dev and k8s without code changes. |
| Clean project layout | Separate concerns into `shared` (cross-cutting) and `api` (route) layers. |

## 3. Project Structure

```
surveillanceapi/
├── doc/
│   └── design_spec.md          # This document
├── src/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app factory + uvicorn entrypoint
│   ├── api/
│   │   ├── __init__.py
│   │   ├── health.py           # GET /health
│   │   └── hello.py            # GET /hello, GET /hello/{name}
│   └── shared/
│       ├── __init__.py
│       ├── config.py           # Pydantic Settings (env-driven)
│       └── logger.py           # Structured JSON logger
├── requirements.txt
└── README.md
```

## 4. API Endpoints

### 4.1 `GET /health`

Returns the current service health status.

**Response model** — `HealthResponse`

| Field | Type | Description |
|-------|------|-------------|
| `status` | `str` | Always `"healthy"` when the service is up. |
| `app_name` | `str` | Application name from settings. |
| `version` | `str` | Application version from settings. |
| `timestamp` | `str` | UTC ISO-8601 timestamp. |

**Example response:**

```json
{
  "status": "healthy",
  "app_name": "surveillanceapi",
  "version": "0.1.0",
  "timestamp": "2026-04-16T12:00:00+00:00"
}
```

### 4.2 `GET /hello`

Returns a generic greeting.

**Response model** — `HelloResponse`

| Field | Type | Description |
|-------|------|-------------|
| `message` | `str` | Greeting string. |

**Example response:**

```json
{
  "message": "Hello from Surveillance API!"
}
```

### 4.3 `GET /hello/{name}`

Returns a personalised greeting.

**Path parameter:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | `str` | Name to greet. |

**Example response:**

```json
{
  "message": "Hello, Alice!"
}
```

## 5. Configuration

All configuration is managed via environment variables, loaded through **pydantic-settings**.

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_APP_NAME` | `surveillanceapi` | Service name. |
| `APP_APP_VERSION` | `0.1.0` | Service version. |
| `APP_HOST` | `0.0.0.0` | Bind address. |
| `APP_PORT` | `8000` | Bind port. |
| `APP_LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR). |
| `APP_LOG_CONTEXT` | `local` | Logging context: `local` or `k8s`. |
| `K8S_NAMESPACE` | `default` | Kubernetes namespace (used when context = k8s). |
| `HOSTNAME` | `unknown` | Pod hostname (auto-set by k8s). |
| `K8S_NODE_NAME` | `unknown` | Node name (exposed via Downward API). |

## 6. Structured JSON Logger

### 6.1 Design

The logger emits one JSON object per log line to `stdout`. A custom `logging.Formatter` serialises each `LogRecord` into JSON, enriching it with context-specific fields.

### 6.2 Contexts

#### Local context

Adds host-level metadata useful during development:

```json
{
  "timestamp": "2026-04-16T12:00:00+00:00",
  "level": "INFO",
  "logger": "src.api.health",
  "message": "Health check called",
  "hostname": "devbox",
  "pid": 12345,
  "environment": "local"
}
```

#### Kubernetes (k8s) context

Adds Kubernetes-specific metadata for cluster observability:

```json
{
  "timestamp": "2026-04-16T12:00:00+00:00",
  "level": "INFO",
  "logger": "src.api.health",
  "message": "Health check called",
  "environment": "k8s",
  "k8s": {
    "namespace": "surveillance",
    "pod": "surveillanceapi-6f8b9c-xz4lq",
    "node": "node-pool-01-abc"
  }
}
```

### 6.3 Extra structured data

Any handler can attach arbitrary data via the `extra` kwarg:

```python
logger.info("Event occurred", extra={"data": {"key": "value"}})
```

This surfaces as a top-level `"data"` field in the JSON output.

## 7. Running the Service

### Local development

```bash
pip install -r requirements.txt
python -m src.main
```

The API is available at `http://localhost:8000`. Swagger docs at `http://localhost:8000/docs`.

### Override log context to k8s (for testing)

```bash
APP_LOG_CONTEXT=k8s python -m src.main
```

## 8. Tech Stack

| Component | Library | Version |
|-----------|---------|---------|
| Web framework | FastAPI | 0.115.x |
| ASGI server | Uvicorn | 0.34.x |
| Data validation | Pydantic | 2.10.x |
| Config management | pydantic-settings | 2.7.x |
| Logging | Python stdlib `logging` | — |
