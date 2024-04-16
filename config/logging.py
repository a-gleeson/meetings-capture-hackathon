import logging
import sys

from config.settings import LOG_LEVEL


def setup_logging():
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(formatter)

    def get_logger(name):
        logger = logging.getLogger(name)
        logger.setLevel(logging.getLevelName(LOG_LEVEL))
        if not logger.handlers:
            logger.addHandler(stdout_handler)

        logger.propagate = False

        return logger

    return get_logger
