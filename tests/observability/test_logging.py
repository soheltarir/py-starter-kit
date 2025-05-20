import json

import structlog

from src.observability.logging import AppLogger

SERVICE_NAME = "test_service"
LOG_LEVEL = "info"
ENVIRONMENT = "development"
SERVICE_NAMESPACE = "test"
SERVICE_VERSION = "1.0.0"


def test_init_production(capsys):
    AppLogger(
        service_name=SERVICE_NAME,
        log_level=LOG_LEVEL,
        environment="production",
        service_namespace=SERVICE_NAMESPACE,
        service_version=SERVICE_VERSION,
    )

    # Assert
    logger = structlog.get_logger()
    logger.info("test message", extra_field="extra_value")
    captured = capsys.readouterr()

    log_data = json.loads(captured.out)
    assert log_data["severity_text"] == "info"
    assert log_data["body"] == "test message"
    assert log_data["attributes"]["extra_field"] == "extra_value"
    assert log_data["resource"]["service"]["name"] == SERVICE_NAME
    assert log_data["resource"]["service"]["namespace"] == SERVICE_NAMESPACE
    assert log_data["resource"]["service"]["version"] == SERVICE_VERSION
    assert log_data["resource"]["environment"]["name"] == "production"


def test_init_development(capsys):
    # Setup
    service_name = "test_service"
    log_level = "debug"
    environment = "development"

    # Execute
    AppLogger(
        service_name=service_name,
        log_level=log_level,
        environment=environment,
        service_namespace=SERVICE_NAMESPACE,
        service_version=SERVICE_VERSION,
    )

    # Assert
    logger = structlog.get_logger()
    logger.debug("test message", extra_field="extra_value")
    captured = capsys.readouterr()
    log_entry = captured.out

    # In development, the log should be console-formatted
    assert isinstance(log_entry, str)
    assert "test message" in log_entry
    assert "extra_field" in log_entry
