import os
from os.path import exists

from Utilities.utilities import print_title
from config import TEMPORAL_CALIBRATION_POINTS_FILE
from select_survey import load_survey

survey = load_survey()

calibration_points_path = survey.get_relative_path(TEMPORAL_CALIBRATION_POINTS_FILE)
if exists(calibration_points_path):
    os.remove(calibration_points_path)
    print_title(f"Removed calibration points.")
else:
    print_title(f"Cannot remove calibration points. No saved calibration points file at: \n'{calibration_points_path}'")
