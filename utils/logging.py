import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
import os
from datetime import datetime


class CustomLogger:
    def __init__(self, name: str = "TrackML"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)

        self._setup_formatters()
        self._setup_handlers()

    def _setup_formatters(self):
        self.console_formatter = logging.Formatter("%(levelname)s - %(message)s")

        self.file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    def _setup_handlers(self):
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(self.console_formatter)

        current_date = datetime.now().strftime("%Y-%m-%d")
        file_handler = RotatingFileHandler(
            self.log_dir / f"trackml_{current_date}.log",
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(self.file_formatter)

        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)

    def debug(self, message: str, *args, **kwargs):
        self.logger.debug(message, *args, **kwargs)

    def info(self, message: str, *args, **kwargs):
        self.logger.info(message, *args, **kwargs)

    def warning(self, message: str, *args, **kwargs):
        self.logger.warning(message, *args, **kwargs)

    def error(self, message: str, *args, **kwargs):
        self.logger.error(message, *args, **kwargs)

    def critical(self, message: str, *args, **kwargs):
        self.logger.critical(message, *args, **kwargs)

    def exception(self, message: str, *args, exc_info=True, **kwargs):
        self.logger.exception(message, *args, exc_info=exc_info, **kwargs)


logger = CustomLogger()


def get_logger(name: str = "TrackML") -> CustomLogger:
    return CustomLogger(name)
