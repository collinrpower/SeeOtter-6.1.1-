import unit_test_helpers
from unittest import TestCase
from Calibration.calibration import CalibrationResults
from Calibration.temporal_calibration import *
from Calibration.temporal_point import *
from Calibration.calibration_settings import *
from Inclinometer.inclinometer_record import InclinometerRecord
from config import *
from SurveyEntities.survey import Survey


class TestTemporalCalibration(TestCase):

    survey_name = '_TestTemporalCalibration'

    @property
    def minimal_dual_camera_temporal_points(self):
        return [
            TemporalPoint('0_000_00_000.jpg', (1, 2), '0_000_00_001.jpg', (11, 4000)),
            TemporalPoint('1_000_00_000.jpg', (5000, 6), '1_000_00_001.jpg', (5000, 4000))
        ]

    @property
    def minimal_dual_camera_temporal_points2(self):
        return [
            TemporalPoint('0_000_00_002.jpg', (9, 10), '0_000_00_003.jpg', (11, 4000)),
            TemporalPoint('1_000_00_002.jpg', (5000, 14), '1_000_00_003.jpg', (5000, 4000))
        ]

    @property
    def unmatched_type_dual_camera_temporal_points(self):
        return [
            TemporalPoint('0_000_00_002.jpg', (9, 10), '1_000_00_003.jpg', (11, 12)),
            TemporalPoint('1_000_00_002.jpg', (13, 14), '1_000_00_003.jpg', (15, 16))
        ]

    @property
    def temporal_points_match_file(self):
        return [
            TemporalPoint('0_000_00_000.jpg', (1, 2), '0_000_00_001.jpg', (3, 4)),
            TemporalPoint('1_000_00_000.jpg', (5, 6), '1_000_00_001.jpg', (7, 8))
        ]

    @classmethod
    def setUpClass(cls):
        survey = unit_test_helpers.create_empty_survey(cls.survey_name)
        unit_test_helpers.copy_test_images_to(survey.images_dir)
        survey = Survey.load(cls.survey_name)
        survey.save()

    def test_temporal_calibration_constructor(self):
        survey = Survey.load(self.survey_name)
        tc = TemporalCalibration(survey=survey, temporal_points=self.minimal_dual_camera_temporal_points)
        self.assertIsInstance(tc, TemporalCalibration)

    def test_get_calibration_points_file_name(self):
        survey = Survey.load(self.survey_name)
        tc = TemporalCalibration(survey=survey, temporal_points=self.minimal_dual_camera_temporal_points)
        actual = tc.calibration_points_path
        expected = join(Survey.get_default_survey_path(self.survey_name),  "temporal_calibration_points.json")
        self.assertEqual(expected, actual)

    def test_save_calibration_points(self):
        survey = Survey.load(self.survey_name)
        tc = TemporalCalibration(survey=survey, temporal_points=self.minimal_dual_camera_temporal_points)
        tc.save_calibration_points()
        self.assertTrue(os.path.exists(tc.calibration_points_path))

    def test_load_calibration_points(self):
        shutil.copy2(unit_test_helpers.temporal_calibration_file, Survey.get_default_survey_path(survey_name=self.survey_name))
        survey = Survey.load(self.survey_name)
        tc = TemporalCalibration(survey=survey)
        tc.load_calibration_points()
        expected = self.temporal_points_match_file
        actual = tc.temporal_points
        self.assertEqual(len(expected), len(actual))
        for i in range(len(expected)):
            self.assertEqual(expected[i].image1, actual[i].image1)
            self.assertEqual(expected[i].image2, actual[i].image2)
            self.assertEqual(expected[i].point1[0], actual[i].point1[0])
            self.assertEqual(expected[i].point1[1], actual[i].point1[1])
            self.assertEqual(expected[i].point2[0], actual[i].point2[0])
            self.assertEqual(expected[i].point2[1], actual[i].point2[1])

    def test_validate_camera_types_match(self):
        survey = Survey.load(self.survey_name)
        self.assertRaises(Exception, lambda: TemporalCalibration(
            survey=survey, temporal_points=self.unmatched_type_dual_camera_temporal_points))

    def test_run_calibration(self):
        survey = Survey.load(self.survey_name)
        tc = TemporalCalibration(survey=survey, temporal_points=self.minimal_dual_camera_temporal_points)
        tc.run_calibration(calibration_settings=CalibrationSettings.small())
        for camera in survey.camera_system.cameras:
            default_calibration = camera.default_calibration
            self.assertNotEqual(0, default_calibration.angle_x)
            self.assertNotEqual(0, default_calibration.angle_y)
            self.assertNotEqual(0, default_calibration.angle_z)

    def test_run_calibration_with_inclinometer_data(self):
        survey = Survey.load(self.survey_name)
        for image in survey.images:
            image.inclinometer_data = InclinometerRecord(
                datetime=image.datetime,
                angle_x=-10,
                angle_y=20,
                angle_z=5
            )
        tc = TemporalCalibration(survey=survey, temporal_points=self.minimal_dual_camera_temporal_points)
        tc.run_calibration(calibration_settings=CalibrationSettings.small())
        for camera in survey.camera_system.cameras:
            default_calibration = camera.default_calibration
            inclinometer_calibration = camera.inclinometer_calibration
            self.assertNotEqual(0, default_calibration.angle_x)
            self.assertNotEqual(0, default_calibration.angle_y)
            self.assertNotEqual(0, default_calibration.angle_z)
            self.assertNotEqual(0, inclinometer_calibration.angle_x)
            self.assertNotEqual(0, inclinometer_calibration.angle_y)
            self.assertNotEqual(0, inclinometer_calibration.angle_z)
            self.assertNotEqual(default_calibration.angle_x, inclinometer_calibration.angle_x)
            self.assertNotEqual(default_calibration.angle_y, inclinometer_calibration.angle_y)
            self.assertNotEqual(default_calibration.angle_z, inclinometer_calibration.angle_z)
