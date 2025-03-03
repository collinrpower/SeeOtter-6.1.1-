import logging

from Utilities.utilities import get_root_path, mkdir_if_not_exists
from config import *


def get_handlers():
    formatter = logging.Formatter("%(asctime)s | %(name)s | %(levelname)s | %(message)s")
    mkdir_if_not_exists("Logs")
    file_handler = logging.FileHandler(get_root_path('Logs/see_otter.log'))
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    stream_handler = logging.StreamHandler()

    return [file_handler, stream_handler]


def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    handlers = get_handlers()
    logger.handlers = handlers

    return logger
