import shutil
from unittest import TestCase
from os.path import *
from SurveyEntities.survey_image import SurveyImage
from UnitTests.unit_test_helpers import *


class TestSurveyImage(TestCase):

    def test_constructor_inits_values(self):
        src_image = test_image_paths[0]
        test_load_gps_dir = create_new_test_dir("TestConstructor")
        img_path = shutil.copy2(src=src_image, dst=test_load_gps_dir)
        survey_image = SurveyImage(img_path)
        self.assertEqual(img_path, survey_image.file_path)
        self.assertEqual(59.47921111111111, survey_image.latitude)
        self.assertEqual(-151.65691944444444, survey_image.longitude)
        self.assertEqual(219, survey_image.altitude)
        self.assertEqual(8688, survey_image.resolution_x)
        self.assertEqual(5792, survey_image.resolution_y)
        self.assertFalse(survey_image.has_been_preprocessed)
        self.assertFalse(survey_image.has_been_processed)

    def test_rename_image(self):
        src_image = test_image_paths[0]
        original_image_name = os.path.basename(src_image)
        new_image_name = "9_999_99_999.jpg"
        test_rename_dir = create_new_test_dir("TestRenameImage")
        original_image_path = normpath(join(test_rename_dir, original_image_name))
        new_image_path = normpath(join(test_rename_dir, new_image_name))
        self.assertFalse(os.path.exists(original_image_path))
        shutil.copy2(src=src_image, dst=test_rename_dir)
        self.assertTrue(os.path.exists(original_image_path))
        survey_image = SurveyImage(original_image_path)
        self.assertEqual(normpath(survey_image.file_path), original_image_path)
        survey_image.rename_image(new_image_name)
        self.assertEqual(survey_image.file_path, new_image_path)
        self.assertEqual(survey_image.file_name, new_image_name)
        self.assertTrue(exists(new_image_path))
        self.assertFalse(exists(original_image_path))
