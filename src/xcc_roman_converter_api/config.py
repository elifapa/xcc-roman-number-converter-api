from datetime import datetime
import logging
import structlog

PG_POST_TABLE = "post_responses_log"
PG_SCHEMA = "api"

PYTHON_TO_POSTGRES_DTYPES = {
    int: "BIGINT",
    float: "DOUBLE PRECISION",
    str: "TEXT",
    bool: "BOOLEAN",
    bytes: "BYTEA",
    datetime: "TIMESTAMP",
    type(None): "TEXT",  # Default for None/null values
}


## Logging configuration with structlog
def configure_logging():
    """
    Configures structlog for structured logging.
    """
    logging.basicConfig(
        format="%(message)s",
        level=logging.INFO,
    )

    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.stdlib.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            # structlog.processors.JSONRenderer(),
            structlog.dev.ConsoleRenderer(colors=True),  # Prettify logs with colors
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
