import json

import pytest
import structlog

from src.observability.logging import AppLogger


@pytest.fixture
def app_logger():
    return AppLogger()


def test_init_production(app_logger, capsys):
    # Setup
    service_name = "test_service"
    log_level = "info"
    environment = "production"
    service_namespace = "test"
    service_version = "1.0.0"

    # Execute
    app_logger.init(
        service_name=service_name,
        log_level=log_level,
        environment=environment,
        service_namespace=service_namespace,
        service_version=service_version,
    )

    # Assert
    logger = structlog.stdlib.get_logger()
    logger.info("test message", extra_field="extra_value")
    captured = capsys.readouterr()

    log_data = json.loads(captured.out)
    assert log_data["severity_text"] == "info"
    assert log_data["body"] == "test message"
    assert log_data["attributes"]["extra_field"] == "extra_value"
    assert log_data["resource"]["service"]["name"] == service_name
    assert log_data["resource"]["service"]["namespace"] == service_namespace
    assert log_data["resource"]["service"]["version"] == service_version
    assert log_data["resource"]["environment"]["name"] == environment


def test_init_development(app_logger, capsys):
    # Setup
    service_name = "test_service"
    log_level = "debug"
    environment = "development"

    # Execute
    app_logger.init(
        service_name=service_name,
        log_level=log_level,
        environment=environment
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
