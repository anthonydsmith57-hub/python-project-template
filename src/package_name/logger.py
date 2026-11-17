"""Centralized logging configuration for console and rotating file output."""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s | %(message)s"
DATE_FORMAT = "%Y-%m-%dT%H:%M:%S%z"
MAX_LOG_BYTES = 5 * 1024 * 1024  # 5 MB per log file
BACKUP_COUNT = 5


def setup_logging(log_level: str, log_file_path: Path) -> None:
    """Configure root logging with console and rotating file handlers.

    Args:
        log_level: Minimum severity level (e.g., 'INFO', 'DEBUG').
        log_file_path: Destination path for the rotating log file.
    """
    log_file_path.parent.mkdir(parents=True, exist_ok=True)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level.upper())

    # Prevent duplicate log lines if setup_logging is called more than once
    if root_logger.handlers:
        root_logger.handlers.clear()

    formatter = logging.Formatter(fmt=LOG_FORMAT, datefmt=DATE_FORMAT)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    file_handler = RotatingFileHandler(
        filename=log_file_path,
        maxBytes=MAX_LOG_BYTES,
        backupCount=BACKUP_COUNT,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
