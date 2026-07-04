import logging
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
LOG_DIR = PROJECT_ROOT / "log"


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
