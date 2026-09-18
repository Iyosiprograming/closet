import logging
from logging.handlers import RotatingFileHandler

import colorlog

from app.Core.paths import ensure_directories, logs_dir


handler = colorlog.StreamHandler()

handler.setFormatter(
    colorlog.ColoredFormatter(
        "%(log_color)s%(asctime)s - %(levelname)s - %(message)s",
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "red,bg_white",
        },
    )
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(handler)


def _add_file_handler(target: logging.Logger) -> None:
    """Also write logs to disk (see app/Core/paths.py for the location).

    Logging must never be the reason the application fails to start, so any
    filesystem problem here is swallowed.
    """
    try:
        ensure_directories()

        file_handler = RotatingFileHandler(
            logs_dir() / "closet-ai.log",
            maxBytes=1_000_000,
            backupCount=3,
            encoding="utf-8",
        )

        # Plain formatter: ANSI colour codes do not belong in a log file.
        file_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
            )
        )

        target.addHandler(file_handler)

    except OSError:
        pass


_add_file_handler(logger)

# The launcher configures the root logger for uvicorn's own logs; keeping this
# logger out of that tree avoids writing the same line to two handlers.
logger.propagate = False