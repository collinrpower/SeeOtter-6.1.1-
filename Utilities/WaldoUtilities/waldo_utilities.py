import os
import pathlib
import re
from typing import List
from config import WALDO_IMAGE_REGEX, WALDO_DTTM_FILE_REGEX


def is_waldo_file_name(path):
    return re.match(WALDO_DTTM_FILE_REGEX, path) is not None


def is_waldo_image_name(path):
    return re.match(WALDO_IMAGE_REGEX, path) is not None
