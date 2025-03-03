import os
import shutil
from os.path import join
from unittest import TestCase
from Camera.waldo_camera_system import WaldoCameraSystem
from Inclinometer.hwt905_inclinometer import Hwt905Inclinometer
from SurveyEntities.survey import Survey
from SurveyEntities.waldo_survey import WaldoSurvey
from UnitTests import unit_test_helpers
from UnitTests.unit_test_helpers import testing_surveys_dir, copy_test_images_to
from config import SURVEY_SAVE_FILE, IMAGE_DIR
from version import version


class TestWaldoSurvey(TestCase):

    def test_new(self):
        new_survey_name = "_TestNewWaldoSurvey"
        survey_path = Survey.get_default_survey_path(new_survey_name)
        if os.path.isdir(survey_path):
            shutil.rmtree(survey_path)
        new_survey = WaldoSurvey.new(new_survey_name)
        self.assertTrue(len(new_survey.images) == 0)
        self.assertTrue(os.path.exists(os.path.join(survey_path, SURVEY_SAVE_FILE)))
        self.assertIsInstance(new_survey.camera_system, WaldoCameraSystem)
        self.assertIsInstance(new_survey.inclinometer, Hwt905Inclinometer)

    def test_create_from_waldo_survey(self):
        # this is tricky to test because of the paths must start at the drive root. todo: find way to test
        pass

    def test_upgrade_survey_as_waldo_survey(self):
        survey_src_name = "V2_Survey"
        new_survey_name = "_TestWaldoSurveyUpgradeProjectVersion"
        survey_path = Survey.get_default_survey_path(new_survey_name)
        survey_src_path = join(testing_surveys_dir, survey_src_name)
        if os.path.isdir(survey_path):
            shutil.rmtree(survey_path)
        shutil.copytree(survey_src_path, survey_path)
        survey_img_path = join(survey_path, IMAGE_DIR)
        copy_test_images_to(survey_img_path)

        old_survey = Survey.load(survey=new_survey_name, quick_load=True, skip_upgrade=True)
        self.assertTrue(old_survey.version.major == 2)
        self.assertIsInstance(old_survey, Survey)

        Survey.upgrade_project_version(survey_name=new_survey_name, survey_type=WaldoSurvey, force=True)
        new_survey = WaldoSurvey.load(survey=new_survey_name)
        self.assertEqual(version, new_survey.version)
        self.assertIsInstance(new_survey, WaldoSurvey)
        self.assertIsInstance(new_survey.camera_system, WaldoCameraSystem)
        self.assertIsInstance(new_survey.inclinometer, Hwt905Inclinometer)

    def test_load_inclinometer_data(self):
        new_survey_name = "_TestLoadWaldoHwt905InclinometerData"
        survey_path = Survey.get_default_survey_path(new_survey_name)
        if os.path.isdir(survey_path):
            shutil.rmtree(survey_path)
        new_survey = WaldoSurvey.new(new_survey_name)
        unit_test_helpers.copy_test_images_to(new_survey.images_dir)
        shutil.copy2(src=r"TestingResources/Files/210318105210.txt",
                     dst=join(new_survey.inclinometer_dir, "210318105210.txt"))
        new_survey.load_new_images()
        inclinometer_data = new_survey.load_inclinometer_data()
        self.assertEqual(4, len(inclinometer_data))
        new_survey.load_and_apply_inclinometer_data(force=True)
        images_with_inclinometer_data = [image for image in new_survey.images if image.inclinometer_data is not None]
        self.assertEqual(6, len(images_with_inclinometer_data))
        img = new_survey.get_image("0_000_00_000.jpg")
        self.assertEqual(10.9094, img.inclinometer_data.angle_x)
