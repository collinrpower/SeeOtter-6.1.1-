import folium
from copy import deepcopy
from abc import abstractmethod
from Calibration.calibration_point import CalibrationPoint
from Calibration.calibration_settings import *
from Camera.camera import Camera
from SurveyEntities.survey import Survey
from Camera.camera_calibration import *
from Utilities.json_convert import JsonConvert
from Utilities.utilities import print_title
from Processing.survey_image_processing import *
from Processing.survey_processing import *


class CalibrationResults:

    def __init__(self, best_calibration: CameraCalibration, avg_error):
        self.best_calibration = best_calibration
        self.avg_error = avg_error


class Calibration:

    def __init__(self, survey, calibration_points: List[CalibrationPoint] = None):
        self.survey = survey
        self.calibration_points = calibration_points
        calculate_bearing(self.survey)
        if self.survey.has_no_images:
            raise Exception(f"Cannot run calibration on survey ({self.survey.name}) since it contains no images. Images"
                            f"directory: ({self.survey.images_dir})")

    @property
    def calibration_points_path(self):
        return self.survey.get_relative_path(self.get_calibration_points_file_name())

    @abstractmethod
    def add_calibration_points(self, point):
        pass

    @abstractmethod
    def calculate_error(self, calibration_points=None, ignore_inclinometer=True) -> float:
        pass

    @abstractmethod
    def get_calibration_points_file_name(self):
        pass

    @abstractmethod
    def save_calibration_points(self):
        pass

    def load_calibration_points(self, calibration_points=None):
        try:
            if calibration_points is not None:
                return calibration_points
            calibration_points = JsonConvert.from_file(self.calibration_points_path)
            return calibration_points.points
        except FileNotFoundError as fnfe:
            print(f"Could not find calibration points file ({self.calibration_points_path}).")
            return []

    def update_camera_calibration(self, camera_calibration: CameraCalibration):
        self.survey.camera_system.set_calibration(camera_calibration)
        self.survey.save_camera_system()

    def apply_calibration_to_cameras(self, camera_calibration: CameraCalibration, cameras: List[Camera] = None,
                                     calibrate_inclinometer=False):
        if cameras is None:
            cameras = self.survey.camera_system.cameras
        for camera in cameras:
            if calibrate_inclinometer:
                camera.inclinometer_calibration = camera_calibration
            else:
                camera.default_calibration = camera_calibration

    @staticmethod
    def camera_calibration_iterator(calibration_settings: CalibrationSettings):
        min_calibration, max_calibration, calibration_increment = calibration_settings.get()
        current_calibration = deepcopy(min_calibration)
        
        while current_calibration.angle_x <= max_calibration.angle_x:
            current_calibration.angle_y = min_calibration.angle_y
            while current_calibration.angle_y <= max_calibration.angle_y:
                current_calibration.angle_z = min_calibration.angle_z
                while current_calibration.angle_z <= max_calibration.angle_z:
                    current_calibration.hfov = min_calibration.hfov
                    while current_calibration.hfov <= max_calibration.hfov:
                        yield current_calibration
                        current_calibration.hfov += calibration_increment.hfov
                    current_calibration.angle_z += calibration_increment.angle_z
                current_calibration.angle_y += calibration_increment.angle_y
            current_calibration.angle_x += calibration_increment.angle_x

    def get_best_calibration(self, calibration_points: List[CalibrationPoint],
                             calibration_settings: CalibrationSettings, cameras: List[Camera]):
        best_calibration = None
        best_avg_error = -1
        ignore_inclinometer = not calibration_settings.calibrate_inclinometer

        for calibration in self.camera_calibration_iterator(calibration_settings=calibration_settings):
            # todo: optimize this to where it doesn't update every camera
            self.apply_calibration_to_cameras(cameras=cameras, camera_calibration=calibration,
                                              calibrate_inclinometer=calibration_settings.calibrate_inclinometer)
            avg_error = self.calculate_error(calibration_points, ignore_inclinometer=ignore_inclinometer)
            if avg_error < best_avg_error or best_avg_error == -1:
                best_avg_error = avg_error
                best_calibration = deepcopy(calibration)
                print(f"New Best Found. Error: {avg_error} ({calibration})")

        print_title(f"Best Calibration. Error: {best_avg_error} ({best_calibration})")

        return CalibrationResults(best_calibration, best_avg_error)
