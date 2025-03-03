import os
import pathlib
from unittest import TestCase
from Utilities.WaldoUtilities.waldo_survey_path import WaldoSurveyPath
from Utilities.WaldoUtilities.waldo_utilities import is_waldo_file_name


class TestWaldoSurveyPath(TestCase):

    def test_parse_path(self):
        path = "G:\\Cook_Inlet\\Waldo\\2022\\04_11"
        waldo_path = WaldoSurveyPath(path)
        self.assertEqual("G:", waldo_path.drive)
        self.assertEqual("Cook_Inlet", waldo_path.location)
        self.assertEqual("Waldo", waldo_path.camera_system)
        self.assertEqual("2022", waldo_path.year)
        self.assertEqual("04_11", waldo_path.month_day)

        path = "G:\\Cook_Inlet\\"
        waldo_path = WaldoSurveyPath(path)
        self.assertEqual("G:", waldo_path.drive)
        self.assertEqual("Cook_Inlet", waldo_path.location)
        self.assertEqual(None, waldo_path.camera_system)
        self.assertEqual(None, waldo_path.year)
        self.assertEqual(None, waldo_path.month_day)

    def test_path(self):
        waldo_path = WaldoSurveyPath()
        waldo_path.drive = "C:"
        waldo_path.location = "Cook_Inlet"
        waldo_path.camera_system = "Waldo"
        waldo_path.year = "2022"
        waldo_path.month_day = "12_13"
        self.assertEqual("C:\\Cook_Inlet\\Waldo\\2022\\12_13", waldo_path.path)

    def test_year_path(self):
        waldo_path = WaldoSurveyPath("G:\\Cook_Inlet\\Waldo\\2022\\04_11")
        self.assertEqual(os.path.normpath("G:\\Cook_Inlet\\Waldo\\2022"), waldo_path.year_path)
        waldo_path = WaldoSurveyPath("G:/Cook_Inlet/Waldo/2022/04_11")
        self.assertEqual(os.path.normpath("G:\\Cook_Inlet\\Waldo\\2022"), waldo_path.year_path)
        waldo_path = WaldoSurveyPath("G:\\Cook_Inlet\\Waldo\\")
        with self.assertRaises(Exception):
            year = waldo_path.year_path

    def test_join_path(self):
        path = WaldoSurveyPath.join_path(["C:\\"])
        self.assertEqual("C:\\", path)
        parent_path = pathlib.Path(__file__).parent.absolute()
        path_parts = parent_path.parts
        path = WaldoSurveyPath.join_path(list(path_parts))
        self.assertEqual(str(parent_path), path)

    def test_is_waldo_file_name(self):
        self.assertTrue(is_waldo_file_name("20220413_02292"))
        self.assertTrue(is_waldo_file_name("20220413_02292.log"))
        self.assertTrue(is_waldo_file_name("G:\\Cook_Inlet\\Waldo\\2022\\04_13\\20220413_02292"))
        self.assertTrue(is_waldo_file_name("G:/Cook_Inlet/Waldo/2022/04_13/20220413_02292"))
        self.assertTrue(is_waldo_file_name("G:\\Cook_Inlet\\Waldo\\2022\\04_13\\20220413_02292.pilot.log"))

    def test_path_not_on_drive_root(self):
        invalid_path = r"C:\Users\ewetherington\Documents\SoutheastSamples\Waldo\2022\05_22"
        with self.assertRaises(Exception) as context:
            path = WaldoSurveyPath(invalid_path)
