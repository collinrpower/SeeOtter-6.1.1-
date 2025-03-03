import asyncio
import copy
import csv
import math
import os
import shutil
import subprocess
import sys
import kivy
from time import sleep

import numpy
import pathlib
from os.path import exists, join, realpath
from datetime import datetime
from pathlib import Path


class PromptUserNotification:

    callback = None
    response = None

    @staticmethod
    def raise_prompt(message):
        PromptUserNotification.callback(message)

    @staticmethod
    def respond(response, *args, **kwargs):
        PromptUserNotification.response = response

    @staticmethod
    def wait_for_response() -> bool:
        print("Waiting for response")
        while PromptUserNotification.response is None:
            sleep(.1)
        response = bool(copy.deepcopy(PromptUserNotification.response))
        PromptUserNotification.response = None
        return response


def set_attributes(obj, attributes: dict):
    for name, value in attributes.items():
        if hasattr(obj, name):
            setattr(obj, name, value)
        else:
            print(f"Warning: No attribute found matching '{name}'")


def open_explorer(path):
    subprocess.Popen(f'explorer /select,"{realpath(path)}"')


def get_root_path(path=None):
    root = pathlib.Path(__file__).parent.parent.resolve()
    if path:
        return realpath(join(root, path))
    else:
        return root


def get_drive_root():
    return os.path.abspath(os.sep)


def format_percent_str(norm_value=None, current=None, max=None, no_decimals=False):
    if norm_value is not None:
        percent = norm_value * 100
    elif current is not None and max is not None:
        if max == 0:
            return ""
        percent = (current/max) * 100
    else:
        return "Format Error"
    if percent < 0 or percent > 100:
        return f"Invalid percent progress: {percent}"
    if no_decimals:
        return f"{percent:.0f}%"
    else:
        return f"{percent:.2f}%"


def class_name(obj):
    if obj is None:
        return "None"
    else:
        return str(type(obj).__name__)


def write_csv(header, rows, file_path):
    with open(file_path, 'w', newline='') as csvfile:
        reader = csv.writer(csvfile)
        reader.writerow(header)
        reader.writerows(rows)


def read_csv_dict_list(path):
    with open(path) as csvfile:
        reader = csv.DictReader(csvfile)
        return [row for row in reader]


def loop_iterator(list, start_index, start_at_next=False, direction=1):
    """
    Loop a list starting at a given index.
    :param list: List of objects
    :param start_index: Current index to start at
    :param start_at_next: If true, starts at the next index instead of start_index
    :param direction: 1 -> Forward; 2-> Backward
    :return: An iterable loop.
    """
    if list is None or len(list) == 0:
        return None
    start_index = start_index if not start_at_next else start_index + direction
    index = start_index
    if direction == 1:
        while index < len(list):
            yield list[index]
            index += 1
        index = 0
        while index < start_index:
            yield list[index]
            index += 1
    elif direction == -1:
        while index > -1:
            yield list[index]
            index -= 1
        index = len(list) - 1
        while index > start_index:
            yield list[index]
            index -= 1


def get_rounded_list(list):
    return [round(elem, 2) for elem in list]


def remove_empty_elements(collection):
    [collection.remove(item) for item in collection if item is None]


def index_out_of_range(index, iterable):
    return index < 0 or index >= len(iterable)


def get_datetime_str(format="%m%d%Y-%H%M%S"):
    return datetime.now().strftime(format)


def meters_to_feet(meters):
    return float(meters) * 3.28084


def print_title(text):
    print("\r\n"+ ("=" * 100) + f"\r\n{text}\r\n" + ("=" * 100) + "\r\n")


def add_attr_if_not_exists(obj, name, value=None):
    if not hasattr(obj, name):
        setattr(obj, name, value)


def mkdir_if_not_exists(dir):
    if not exists(dir):
        os.mkdir(dir)


def paths_equal(path1, path2):
    return os.path.normpath(path1) == os.path.normpath(path2)


def rmdir_if_exists(dir):
    if exists(dir):
        shutil.rmtree(dir)


def get_file_name_without_extension(file_path):
    return Path(file_path).stem


def get_normalized_pixel_pos(pos, resolution):
    return pos[0]/resolution[0], pos[1]/resolution[1]


def cartesian_to_compass_bearing(degrees):
    nautical = (degrees * -1) + 90
    if nautical > 180:
        nautical -= 360
    if nautical < -180:
        nautical += 360
    return nautical


def format_compass_bearing(degrees):
    degrees = degrees % 360
    if degrees > 180:
        degrees -= 360
    if degrees < -180:
        degrees += 360
    return degrees


def get_bearing(coord1, coord2):
    lat1, long1 = coord1
    lat2, long2 = coord2
    long_diff = (long2 - long1)
    x = math.cos(math.radians(lat2)) * math.sin(math.radians(long_diff))
    y = math.cos(math.radians(lat1)) * math.sin(math.radians(lat2)) - \
        math.sin(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.cos(math.radians(long_diff))
    bearing = numpy.arctan2(x, y)
    bearing = numpy.degrees(bearing)
    return bearing


def bearing_within_target_threshold(bearing, target, threshold):
    bearing = format_compass_bearing(bearing)
    threshold_low = format_compass_bearing(target - threshold)
    threshold_high = format_compass_bearing(target + threshold)
    if threshold_low <= threshold_high:
        return threshold_low <= bearing <= threshold_high
    else:
        return bearing >= threshold_low or bearing <= threshold_high


def get_loaded_modules():
    return sorted(sys.modules.keys())


def is_kivy_loaded():
    return get_loaded_modules().__contains__("kivy")


def prompt_user(message):
    while True:
        if is_kivy_loaded() and PromptUserNotification.callback:
            PromptUserNotification.raise_prompt(message)
            #PromptUserNotification.respond(False)
            response = PromptUserNotification.wait_for_response()
            print(f"Recieved response: {response}")
            return response
        else:
            response = input(message + "\n")
            if response.upper() == 'Y':
                return True
            elif response.upper() == 'N':
                return False
            else:
                print(f"Invalid Response: {response}")
