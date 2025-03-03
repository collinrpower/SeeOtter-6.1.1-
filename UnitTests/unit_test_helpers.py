import os
import shutil
from unittest import TestCase

from SurveyEntities.waldo_survey import WaldoSurvey
from Utilities.utilities import rmdir_if_exists
from os.path import abspath, join, realpath
from config import *
from Utilities.utilities import *
from SurveyEntities.survey import Survey

project_dir = abspath('../')
survey_dir = join(project_dir, SURVEYS_DIR)
testing_resources_dir = 'TestingResources'
testing_files_dir = 'TestingResources/Files'
testing_images_dir = 'TestingResources/Images'
testing_surveys_dir = 'TestingResources/Surveys'
testing_output_dir = 'TestOutput'
test_dir = 'TestDir'

temporal_calibration_file = 'TestingResources/Files/temporal_calibration_points.json'

test_image_paths = [
    realpath(join(testing_images_dir, "0_000_00_000.jpg")),
    realpath(join(testing_images_dir, "0_000_00_001.jpg")),
    realpath(join(testing_images_dir, "0_000_00_002.jpg")),
    realpath(join(testing_images_dir, "0_000_00_003.jpg")),
    realpath(join(testing_images_dir, "0_000_00_004.jpg")),
    realpath(join(testing_images_dir, "1_000_00_000.jpg")),
    realpath(join(testing_images_dir, "1_000_00_001.jpg")),
    realpath(join(testing_images_dir, "1_000_00_002.jpg")),
    realpath(join(testing_images_dir, "1_000_00_003.jpg")),
    realpath(join(testing_images_dir, "1_000_00_004.jpg"))
]


def create_new_test_dir(dir_name):
    path = os.path.join(test_dir, dir_name)
    rmdir_if_exists(path)
    os.mkdir(path)
    return path


def create_empty_survey(survey_name):
    rmdir_if_exists(Survey.get_default_survey_path(survey_name=survey_name))
    return WaldoSurvey.new(survey_name, overwrite=True)


def copy_test_images_to(dst):
    for image in test_image_paths:
        shutil.copy2(src=image, dst=dst)


def delete_all_test_surveys():
    for survey_path in Survey.get_all_survey_dirs():
        if os.path.dirname(survey_path).startswith('_'):
            shutil.rmtree(survey_path)
