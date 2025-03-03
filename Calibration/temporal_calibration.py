from Calibration.calibration import Calibration, CalibrationSettings
from Calibration.test_calibration_points import points_4cm_KBay_80k_SWNE, points_temporal_testing
from Camera.camera_calibration import CameraCalibration
from SurveyEntities.survey import Survey
from SurveyEntities.survey_image import *
from Utilities.json_convert import JsonConvert
from Utilities.utilities import *
from Calibration.temporal_point import TemporalPoint, TemporalCalibrationPoint, TemporalPoints


class TemporalCalibration(Calibration):

    def __init__(self, survey, temporal_points: List[TemporalPoint] = None):
        super().__init__(survey)
        self.calibration_points = []
        self.images = []
        self.temporal_points = self.load_calibration_points(calibration_points=temporal_points)
        self.init_points()
        self.validate_camera_types_match()

    @property
    def images_with_inclinometer_data(self):
        return [image for image in self.images if image.has_inclinometer_data]

    def init_points(self):
        self.calibration_points: List[TemporalCalibrationPoint] = self.create_temporal_point_data()
        self.images: List[SurveyImage] = list(set(
            [point.image1 for point in self.calibration_points] + [point.image2 for point in self.calibration_points]))

    def calculate_error(self, calibration_points=None, ignore_inclinometer=True):
        total_error = 0
        for point in self.calibration_points:
            total_error += point.get_error(ignore_inclinometer=ignore_inclinometer)
        avg_error = total_error / len(self.calibration_points)
        return avg_error

    def create_temporal_point_data(self):
        # if self.temporal_points is None:
        #     raise Exception("Error loading calibration, no calibration points file found.")
        return [TemporalCalibrationPoint(self.survey, point) for point in self.temporal_points]

    def get_calibration_points_file_name(self):
        return TEMPORAL_CALIBRATION_POINTS_FILE

    def save_calibration_points(self):
        if len(self.temporal_points) == 0:
            print("No temporal points to save.")
        JsonConvert.to_file(TemporalPoints(self.temporal_points), self.calibration_points_path)

    def contains_point(self, point):
        for current_point in self.temporal_points:
            if current_point.image1 == point.image1 and current_point.image2 == point.image2 \
                    and current_point.point1[0] == point.point1[0] and current_point.point2[0] == point.point2[0]:
                return True
        return False

    def add_calibration_points(self, *points):
        for point in points:
            if not isinstance(point, TemporalPoint):
                raise Exception("Added points must be TemporalPoint or list of TemporalPoints.")
            if not self.contains_point(point):
                self.temporal_points.append(point)
        self.init_points()

    def validate_camera_types_match(self):
        for point in self.calibration_points:
            if point.image1.camera.name != point.image2.camera.name:
                raise Exception("Temporal calibration points must both be same camera type."
                                f"{point.image1.file_path}: {point.image1.camera.name}"
                                f"{point.image2.file_path}: {point.image2.camera.name}")

    def can_run_calibration(self) -> bool:
        if len(self.images) == 0:
            print("No images to use for calibration. Exiting...")
            return False
        if len(self.temporal_points) == 0:
            print("No temporal points to use for calibration. Exiting...")
            return False
        return True

    def can_run_inclinometer_calibration(self) -> bool:
        num_images = len(self.images)
        num_inc_images = len(self.images_with_inclinometer_data)
        if num_inc_images == 0:
            print("No images containing inclinometer data. Skipping inclinometer calibration.")
            return False
        if num_inc_images == num_images:
            return True
        if num_inc_images < num_images:
            response = prompt_user(f"Warning. Not all images have inclinometer data ({num_inc_images}/{num_images}).\n"
                                   f"Would you like to run inclinometer calibration anyway? [Y/N]\n")
            if response is False:
                print("Skipping inclinometer calibration.")
            return response

    def run_calibration(self, calibration_settings: CalibrationSettings):
        print_title(f"Running calibration for survey '{self.survey.survey_name}' using "
                    f"{len(self.temporal_points)} calibration points.")
        self.run_default_calibration(calibration_settings)
        self.run_inclinometer_calibration(calibration_settings)

    def run_default_calibration(self, calibration_settings):
        if self.can_run_calibration() is False:
            return
        print_title(f"Starting default calibration.")
        calibration_settings.calibrate_inclinometer = False
        results = self.get_best_calibration(calibration_points=self.calibration_points,
                                            calibration_settings=calibration_settings,
                                            cameras=self.survey.camera_system.cameras)
        self.apply_calibration_to_cameras(camera_calibration=results.best_calibration, calibrate_inclinometer=False)

    def run_inclinometer_calibration(self, calibration_settings):
        if self.can_run_inclinometer_calibration() is False:
            return
        print_title(f"Starting inclinometer calibration.")
        calibration_settings.calibrate_inclinometer = True
        results = self.get_best_calibration(calibration_points=self.calibration_points,
                                            calibration_settings=calibration_settings,
                                            cameras=self.survey.camera_system.cameras)
        self.apply_calibration_to_cameras(camera_calibration=results.best_calibration, calibrate_inclinometer=True)


# todo: remove me, this is for testing
def alter_inclinometer(images: List[SurveyImage], swap_xy=False, inv_x=False, inv_y=False):
    for image in images:
        if image.inclinometer_data is None:
            raise Exception("No inclinometer data")
        if swap_xy:
            x = image.inclinometer_data.angle_x
            y = image.inclinometer_data.angle_y
            image.inclinometer_data.angle_x = y
            image.inclinometer_data.angle_y = x
        if inv_x:
            image.inclinometer_data.angle_x *= -1
        if inv_y:
            image.inclinometer_data.angle_y *= -1


# TODO: Set to -1 while not testing
mode = -1

if mode != -1:
    survey = Survey.load(r"F:\SeeOtterTestSurveys\TemporalTesting\savefile.json")
    # temporal_points = TemporalPoints(points_temporal_testing)
    tt = TemporalCalibration(survey=survey)  # , temporal_points=points_temporal_testing)
    calibration_settings = CalibrationSettings.medium()

    if mode == 0:
        tt.save_calibration_points()
    elif mode == 1:
        tt.run_calibration(calibration_settings=calibration_settings)
    elif mode == 2:
        tt.save_calibration_points()

    print("Calibration Complete!")
