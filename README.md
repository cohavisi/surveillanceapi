# Surveillance API

A lightweight REST API service built with **FastAPI**, **Uvicorn**, and **Pydantic**. Provides health-check and greeting endpoints with structured JSON logging that supports both local development and Kubernetes deployment contexts.

## Project Structure

```
src/
├── Dockerfile
├── main.py
├── api/
│   ├── health.py          # GET /health
│   └── hello.py           # GET /hello, GET /hello/{name}
└── shared/
    ├── config/
    │   └── settings.py    # Pydantic-based configuration
    └── logging/
        └── logger.py      # Structured JSON logger
```

## Endpoints

| Method | Path           | Description              |
|--------|----------------|--------------------------|
| GET    | `/health`      | Service health check     |
| GET    | `/hello`       | Generic greeting         |
| GET    | `/hello/{name}`| Personalised greeting    |
| GET    | `/docs`        | Swagger UI (auto-generated) |

## Running Locally

```bash
pip install -r requirements.txt
python -m src.main
```

The API will be available at `http://localhost:8000`.

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_HOST` | `0.0.0.0` | Bind address |
| `APP_PORT` | `8000` | Bind port |
| `APP_LOG_LEVEL` | `INFO` | Log level (DEBUG, INFO, WARNING, ERROR) |
| `APP_LOG_CONTEXT` | `local` | Log context: `local` or `k8s` |

To test with the Kubernetes logging context locally:

```bash
APP_LOG_CONTEXT=k8s python -m src.main
```

## Running with Docker

### Build

```bash
docker build -f src/Dockerfile -t surveillanceapi .
```

### Run

```bash
docker run -p 8000:8000 surveillanceapi
```

Override settings via environment variables:

```bash
docker run -p 8000:8000 \
  -e APP_LOG_LEVEL=DEBUG \
  -e APP_LOG_CONTEXT=k8s \
  surveillanceapi
```
