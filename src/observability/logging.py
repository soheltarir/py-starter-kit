import json
import logging
import sys
from typing import Callable, Literal, Optional, List, Any

import structlog
from asgi_correlation_id import correlation_id
from dependency_injector import resources
from dependency_injector.resources import T
from structlog.testing import LogCapture
from structlog.typing import WrappedLogger, EventDict, Processor


LOG_LEVEL_MAP: dict[str, Any] = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
}


class StructuredAppLogRenderer:
    def __init__(
        self,
        service_name: str,
        env: Literal["production", "staging", "development"],
        serializer: Callable = json.dumps,
        service_namespace: Optional[str] = None,
        service_version: Optional[str] = None,
    ):
        self._dumps = serializer
        self._service_name = service_name
        self._env = env
        self._service_namespace = service_namespace
        self._service_version = service_version

    def __call__(
        self, logger: WrappedLogger, name: str, event_dict: EventDict
    ) -> str | bytes:
        timestamp, level = event_dict.pop("timestamp"), event_dict.pop("level")
        body = event_dict.pop("event")
        log_data = {
            "timestamp": int(timestamp),
            "severity_text": level,
            "body": body,
            "resource": {
                "service": {
                    "name": self._service_name,
                    "namespace": self._service_namespace,
                    "version": self._service_version,
                },
                "environment": {"name": self._env},
            },
            "attributes": event_dict,
        }
        return self._dumps(log_data)


def add_correlation(
    _: logging.Logger, __: str, event_dict: dict[str, Any]
) -> dict[str, Any]:
    """Add request id to log a message."""
    if request_id := correlation_id.get():
        event_dict["request_id"] = request_id
    return event_dict


class AppLogger(resources.Resource):
    def __init__(self):
        self._log_level = None
        self._environment = None
        self._service_version = None
        self._service_namespace = None
        self._service_name = None

        # Base Processors
        self._base_processors: List[Processor] = [
            add_correlation,
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.TimeStamper(utc=True),
        ]

    def _get_final_processors(self) -> List[Processor]:
        if self._environment == "production":
            processors = [
                structlog.processors.dict_tracebacks,
                StructuredAppLogRenderer(
                    self._service_name,
                    self._environment,
                    service_namespace=self._service_namespace,
                    service_version=self._service_version,
                ),
            ]
        else:
            processors = [
                structlog.dev.ConsoleRenderer(
                    exception_formatter=structlog.dev.better_traceback
                )
            ]
        return processors

    def _setup_structlog(self):
        structlog.configure(
            processors=self._base_processors + self._get_final_processors(),
            wrapper_class=structlog.make_filtering_bound_logger(self._log_level),
            context_class=dict,
            logger_factory=structlog.PrintLoggerFactory(),
            cache_logger_on_first_use=True,
        )

    def _setup_stdlib_log(self):
        formatter = structlog.stdlib.ProcessorFormatter(
            foreign_pre_chain=self._base_processors,
            processors=[structlog.stdlib.ProcessorFormatter.remove_processors_meta]
            + self._get_final_processors(),
        )

        handler = logging.StreamHandler(stream=sys.stdout)
        handler.setFormatter(formatter)

        for logger_name in logging.root.manager.loggerDict.keys():
            override_logger = logging.getLogger(logger_name)
            override_logger.handlers = []
            override_logger.propagate = True
            override_logger.addHandler(handler)
            override_logger.setLevel(self._log_level)

    def init(
        self,
        service_name: str,
        log_level: str,
        environment: str,
        service_namespace: Optional[str] = None,
        service_version: Optional[str] = None,
        # Below is just used for testing
        log_output: Optional[LogCapture] = None,
    ):
        # Initialisation
        self._service_name = service_name
        self._service_namespace = service_namespace
        self._service_version = service_version
        self._environment = environment
        self._log_level = LOG_LEVEL_MAP[log_level]

        self._setup_structlog()
        self._setup_stdlib_log()

    def shutdown(self, resource: Optional[T]) -> None:
        pass


__all__ = ["AppLogger"]
