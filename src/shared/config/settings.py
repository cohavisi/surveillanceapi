from pydantic_settings import BaseSettings
from pydantic import Field
from enum import Enum


class LogContext(str, Enum):
    LOCAL = "local"
    K8S = "k8s"


class Settings(BaseSettings):
    app_name: str = "surveillanceapi"
    app_version: str = "0.1.0"
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "INFO"
    log_context: LogContext = LogContext.LOCAL
    log_color: bool = True

    # K8s-specific fields (populated via env vars in k8s)
    k8s_namespace: str = Field(default="default", alias="K8S_NAMESPACE")
    k8s_pod_name: str = Field(default="unknown", alias="HOSTNAME")
    k8s_node_name: str = Field(default="unknown", alias="K8S_NODE_NAME")

    model_config = {"env_prefix": "APP_", "populate_by_name": True}


settings = Settings()
