from unittest import TestCase

from UnitTests.unit_test_helpers import test_image_paths, testing_output_dir
from Utilities.WaldoUtilities.waldo_survey_converter import WaldoSurveyConverter


class TestWaldoSurveyConverter(TestCase):

    def test_get_waldo_directories(self):
        pass

    def test_get_path_mapping(self):
        img_paths = [[test_image_paths[1], test_image_paths[6]], [test_image_paths[2], test_image_paths[7]]]
        mapping = WaldoSurveyConverter.get_path_mapping(paths=img_paths, image_out_dir=testing_output_dir)
        self.assertEqual(4, len(mapping.keys()))
        self.assertFalse(test_image_paths[1].__contains__("TestOutput"))
        self.assertTrue(mapping[test_image_paths[1]].__contains__("\\UnitTests\\TestOutput\\1_000_00_000.jpg"))
