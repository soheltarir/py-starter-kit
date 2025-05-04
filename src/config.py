from typing import Literal, Optional

from pydantic import BaseModel, IPvAnyAddress
from pydantic_settings import BaseSettings, SettingsConfigDict


class ServiceConfig(BaseModel):
    name: str = "py_starter_kit"
    namespace: Optional[str] = None
    version: str = "0.1.0"


class MongoDBSettings(BaseModel):
    uri: Optional[str] = "mongodb://localhost:27017/"
    database: Optional[str] = "test_db"


class RestServerSettings(BaseModel):
    host: Optional[IPvAnyAddress] = "0.0.0.0"
    port: Optional[int] = 5000


class CelerySettings(BaseModel):
    broker: Optional[str] = None
    result_backend: Optional[str] = None


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_nested_delimiter="__",
        env_file=".env",
        env_file_encoding="utf-8",
        validate_assignment=False,
    )

    service: ServiceConfig = ServiceConfig()
    environment: Literal["production", "staging", "development"] = "development"
    log_level: Literal["debug", "info", "warning", "error", "critical"] = "info"
    mongo: Optional[MongoDBSettings] = MongoDBSettings()
    rest_server: Optional[RestServerSettings] = RestServerSettings()
    celery: Optional[CelerySettings] = CelerySettings()
