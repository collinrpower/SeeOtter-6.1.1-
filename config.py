from Utilities.kivy_keycodes import *


# Results
NA = "N/A"
RESULTS_CONFIDENCE_CUTOFF = 0

# MapGenerator
MAP_COLORS = ['red', 'blue', 'green', 'purple', 'orange', 'pink', 'gray']
MAP_IMAGE_PROJECTION_OPACITY = .1
MAP_PREDICTION_CONFIDENCE_CUTOFF = .5

# Formatting
PROGRESS_BAR_LABEL_PADDING = 40
NEWLINE = "\r\n"

# Directories
SURVEYS_DIR = 'Surveys'
IMAGE_DIR = 'Images'
BACKUP_DIR = 'Backup'
TRANSECT_DIR = 'Transects'
ANNOTATIONS_DIR = 'Annotations'
MODEL_WEIGHTS_DIR = 'ModelWeights'
INCLINOMETER_DATA_DIR = 'InclinometerData'
RESULTS_DIR = 'Results'
AMBIGUOUS_VOTE_DIR = f"{RESULTS_DIR}/AmbiguousVote"

# Files
IMAGE_EXT = '.JPG'
USER_GUIDE_FILE = "SeeOtterUserGuide.docx"
OTTER_CHECKER_CONFIG_FILE = 'otter_checker_config.json'
SEE_OTTER_CONFIG_FILE = 'see_otter_config.json'
CSV_OUTPUT_FILENAME = 'results.csv'
SURVEY_SAVE_FILE = 'savefile.json'
CAMERA_SYSTEM_FILE = 'camera_system.json'
PREDICTIONS_BACKUP_FILE = 'prediction_data.json'
TRANSECT_ASSIGNMENT_FILE = 'transect_assignment.csv'
TEMPORAL_CALIBRATION_POINTS_FILE = 'temporal_calibration_points.json'
LOCATION_CALIBRATION_POINTS_FILE = 'location_calibration_points.json'
DEFAULT_MODEL_WEIGHTS_FILE = 'best.pt'


CREATE_SURVEY_DIRS = [IMAGE_DIR,
                      BACKUP_DIR,
                      TRANSECT_DIR,
                      INCLINOMETER_DATA_DIR,
                      ANNOTATIONS_DIR,
                      RESULTS_DIR,
                      AMBIGUOUS_VOTE_DIR]

KEEP_WHEN_OVERWRITING_PROJECT = [IMAGE_DIR,
                                 BACKUP_DIR,
                                 TRANSECT_DIR,
                                 INCLINOMETER_DATA_DIR,
                                 PREDICTIONS_BACKUP_FILE,
                                 TEMPORAL_CALIBRATION_POINTS_FILE,
                                 LOCATION_CALIBRATION_POINTS_FILE]

EXCLUDE_FROM_BACKUP = [IMAGE_DIR, BACKUP_DIR]

# Camera
WALDO_HORIZONTAL_FOV = 39.6

# Regex
WALDO_LEFT_CAMERA_REGEX = r"(1)_([0-9]{3})_([0-9]{2,3})_([0-9]{3,4})\.(jpg|JPG)$"
WALDO_RIGHT_CAMERA_REGEX = r"(0)_([0-9]{3})_([0-9]{2,3})_([0-9]{3,4})\.(jpg|JPG)$"
WALDO_IMAGE_REGEX = r"([0-9])_([0-9]{3})_([0-9]{2,3})_([0-9]{3,4})\.(jpg|JPG)$"
WALDO_CORRUPTED_IMAGE_REGEX = r"([0-9])_([0-9]{3})_([0-9]{2,3})_([0-9]{3,4})\.(jpg|JPG).+$"
WALDO_DTTM_FILE_REGEX = "(.*)([0-9]{4})([0-9]{2})([0-9]{2})_([0-9]{5})"
HWT905_INCLINOMETER_FILE_REGEX = r"(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2}).txt"
YYYY_REGEX = r"^(19|20|21)\d{2}$"
MM_DD_REGEX = r"^((0\d)|(1[012]))_\d{2}$"

# EXIF Tags
EXIF_CAMERA_MAKE = 'Image Make'
EXIF_CAMERA_MODEL = 'Image Model'
EXIF_DATETIME = "Image DateTime"
EXIF_DATETIME_ORIGINAL = "EXIF DateTimeOriginal"
EXIF_IMAGE_ORIENTATION = 'Image Orientation'
EXIF_IMAGE_WIDTH = "EXIF ExifImageWidth"
EXIF_IMAGE_HEIGHT = "EXIF ExifImageLength"
EXIF_ISO = 'EXIF ISOSpeedRatings'
EXIF_FSTOP = 'EXIF FNumber'
EXIF_EXPOSURE = 'EXIF ExposureTime'
EXIF_FOCAL_LENGTH = 'EXIF FocalLength'

# GUI
PANEL_SPACING = 10
PANEL_PADDING = 10
THEME_ORANGE = (1, .6, 0, 1)


class KeyBinding:

    EDIT_ANNOTATIONS = KeyCode.L_CTRL
    TOGGLE_DRAW_MODE = KeyCode.D

    NEXT_IMAGE = KeyCode.UP
    PREVIOUS_IMAGE = KeyCode.DOWN
    NEXT_PREDICTION = KeyCode.RIGHT
    PREVIOUS_PREDICTION = KeyCode.LEFT
    PAN_TO_SELECTED_PREDICTION = KeyCode.SPACE
    DELETE_PREDICTION = KeyCode.DELETE
    HIDE_ANNOTATIONS = KeyCode.L_SHIFT

    VALIDATE_CORRECT = KeyCode.Q
    VALIDATE_INCORRECT = KeyCode.W
    VALIDATE_AMBIGUOUS = KeyCode.E
