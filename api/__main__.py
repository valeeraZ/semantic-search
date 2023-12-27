import logging
import os
import sys

from asgi_correlation_id.context import correlation_id
from loguru import logger
from uvicorn import Config, Server

from api.settings import settings

LOG_LEVEL = logging.getLevelName(settings.log_level.value.upper())
JSON_LOGS = True if os.environ.get("JSON_LOGS", "0") == "1" else False


def correlation_id_filter(record):
    record["correlation_id"] = correlation_id.get()
    return True


class InterceptHandler(logging.Handler):
    def emit(self, record):
        # get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # find caller from where originated the logged message
        frame, depth = sys._getframe(6), 6
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_logging():
    # intercept everything at the root logger
    logging.root.handlers = [InterceptHandler()]
    logging.root.setLevel(LOG_LEVEL)

    # remove every other logger's handlers
    # and propagate to root logger
    for name in logging.root.manager.loggerDict.keys():
        logging.getLogger(name).handlers = []
        logging.getLogger(name).propagate = True

    # configure loguru
    fmt = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <red> {correlation_id} </red> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    logger.remove()
    logger.add(
        sink=sys.stdout, format=fmt, filter=correlation_id_filter, serialize=JSON_LOGS
    )


def main() -> None:
    """Entrypoint of the application."""
    server = Server(
        Config(
            "api.web.application:get_app",
            host=settings.host,
            port=settings.port,
            log_level=settings.log_level.value.lower(),
            reload=settings.reload,
            workers=settings.workers_count,
        )
    )
    setup_logging()
    logger.info("Starting server...")
    server.run()


if __name__ == "__main__":
    main()
