from typing import Literal, Optional

from pydantic import BaseModel, IPvAnyAddress
from pydantic_settings import BaseSettings, SettingsConfigDict


class ServiceConfig(BaseModel):
    name: str = "py_starter_kit"
    namespace: Optional[str] = None
    version: str = "0.1.0"


class MongoDBSettings(BaseModel):
    uri: str
    database: str


class RestServerSettings(BaseModel):
    host: Optional[IPvAnyAddress] = '0.0.0.0'
    port: Optional[int] = 5000


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_nested_delimiter='__',
        env_file='.env', env_file_encoding='utf-8',
        validate_assignment=False
    )

    service: ServiceConfig = ServiceConfig()
    environment: Literal["production", "staging", "development"] = "development"
    log_level: Literal["debug", "info", "warning", "error", "critical"] = "info"
    mongo: MongoDBSettings
    rest_server: Optional[RestServerSettings] = RestServerSettings()
