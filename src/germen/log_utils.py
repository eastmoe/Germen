import logging
from pathlib import Path

from .app_config import PROJECT_ROOT

LOG_DIR = PROJECT_ROOT / "log"
LOG_DIR.mkdir(parents=True, exist_ok=True)


def get_logger(name: str, file_name: str) -> logging.Logger:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    if not any(
        isinstance(handler, logging.FileHandler)
        and Path(handler.baseFilename).name == file_name
        for handler in logger.handlers
    ):
        handler = logging.FileHandler(LOG_DIR / file_name, encoding="utf-8")
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s"
            )
        )
        logger.addHandler(handler)
    return logger
