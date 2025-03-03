import os
import re
import pathlib
from typing import List

from config import YYYY_REGEX, MM_DD_REGEX


class WaldoSurveyPath:

    drive = None
    location = None
    camera_system = None
    year = None
    month_day = None
    image_subdir = None

    def __init__(self, path=None, ignore_errors=False):
        self.load_from_path(path)
        errors = self.get_validation_errors()
        if errors and ignore_errors is False:
            raise Exception(f"Error parsing WaldoPath. Make sure files are in the drive root and in the format: "
                            f"[DriveLetter:/Location/CameraSystem/YYYY/MM_DD]. Errors: {','.join(errors)}")

    def __str__(self):
        return self.path

    def load_from_path(self, path):
        if not path:
            return
        try:
            path = pathlib.Path(path)
            parts = path.parts
            num_parts = len(parts)
            self.drive = path.drive
            self.location = parts[1]
            self.camera_system = parts[2] if num_parts >= 3 else None
            self.year = parts[3] if num_parts >= 4 else None
            self.month_day = parts[4] if num_parts >= 5 else None

        except Exception as ex:
            print("Error loading waldo survey path: " + str(ex))

    def get_validation_errors(self):
        errors = []
        if self.year and not(re.match(YYYY_REGEX, self.year)):
            errors.append(f"Invalid Year: '{self.year}'")
        if self.year and not(re.match(MM_DD_REGEX, self.month_day)):
            errors.append(f"Invalid MonthDay: '{self.month_day}'")
        return errors

    @property
    def path(self):
        return self.join_path(self.path_parts)

    @property
    def path_parts(self):
        path_parts = []
        for part in [self.drive, self.location, self.camera_system, self.year, self.month_day, self.image_subdir]:
            if part is None:
                return path_parts
            path_parts.append(part)
        return path_parts

    @property
    def month_day_path(self):
        if not self.month_day:
            raise Exception(f"Path does not contain month_day: {self.path}")
        return self.path

    @property
    def year_path(self):
        if not self.year:
            raise Exception(f"Path does not contain year: {self.path}")
        return self.get_partial_path(self.year)

    @property
    def path_level(self):
        last_path = self.path_parts[-1]
        if last_path == self.drive:
            return "drive"
        if last_path == self.location:
            return "location"
        if last_path == self.camera_system:
            return "camera_system"
        if last_path == self.year:
            return "year"
        if last_path == self.month_day:
            return "month_day"
        if last_path == self.image_subdir:
            return "image_subdir"

    @staticmethod
    def join_path(path_parts: List[str]):
        path = '\\'.join(path_parts)
        path = os.path.normpath(path)
        return path

    def get_partial_path(self, path_level):
        if not self.path_parts.__contains__(path_level):
            raise Exception(f"Path does not contain {path_level}")
        parts = []
        for part in self.path_parts:
            parts.append(part)
            if part == path_level:
                return self.join_path(parts)