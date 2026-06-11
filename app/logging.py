import logging
from collections.abc import Mapping, MutableMapping
from typing import Any

import structlog


SENSITIVE_KEYS = {"token", "session_token", "authorization", "api_key", "secret_key"}


def redact_sensitive_values(
    _: Any,
    __: str,
    event_dict: MutableMapping[str, Any],
) -> Mapping[str, Any]:
    """Redact known sensitive values from structured logs."""
    for key in list(event_dict):
        if key.lower() in SENSITIVE_KEYS:
            event_dict[key] = "[REDACTED]"
    return event_dict


def configure_logging(log_level: str) -> None:
    """Configure JSON structured logging for the application."""
    logging.basicConfig(level=getattr(logging, log_level.upper(), logging.INFO))
    structlog.configure(
        processors=[
            redact_sensitive_values,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, log_level.upper(), logging.INFO)
        ),
        cache_logger_on_first_use=True,
    )
