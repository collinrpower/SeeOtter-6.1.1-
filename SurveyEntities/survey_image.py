import copy
import datetime
import os.path
import exifread
import re
from typing import List

from Config.see_otter_config import SeeOtterConfig
from SurveyEntities.image_metadata import ImageMetadata
from SurveyEntities.image_tag import ImageTag
from SurveyEntities.tag_manager import TagManager
from Utilities.utilities import meters_to_feet
from config import *
from sahi.prediction import PredictionResult
from GPSPhoto import gpsphoto
from SurveyEntities.object_prediction_data import ObjectPredictionData, ValidationState


class SurveyImage(object):
    """
    Represents a single image for a survey and associated data:
      - Image path
      - Image metadata
      - Prediction data
    """

    def __init__(self, file_path, file_name=None, latitude=None, longitude=None, altitude=None, exif_tags=None,
                 datetime=None, direction=0, num_otters=0, predictions=None, has_been_processed=False,
                 has_been_preprocessed=False):

        # Photo Metadata
        predictions = predictions or []
        self.id = -1
        self.file_path = file_path
        self.file_name = file_name or os.path.basename(file_path)
        self.latitude, self.longitude, self.altitude = self.load_gps_data()
        self.metadata = ImageMetadata(self.file_path)

        # Calculated Fields
        self.direction = direction
        self.num_otters = num_otters
        self.predictions: List[ObjectPredictionData] = predictions

        # Data
        self.camera = None
        self.inclinometer_data = None
        self.transect_id = None

        # State
        self.excluded = False
        self.has_been_preprocessed = has_been_preprocessed
        self.has_been_processed = has_been_processed
        self.flags = []

        # User Input
        self.notes = ""
        self.tags = TagManager()

    def __repr__(self):
        return self.file_name

    @classmethod
    @property
    def config(cls) -> SeeOtterConfig:
        return SeeOtterConfig.instance()

    @property
    def has_inclinometer_data(self):
        return self.inclinometer_data is not None

    @property
    def datetime(self):
        return self.metadata.datetime

    @property
    def datetime_obj(self):
        try:
            return datetime.datetime.strptime(self.datetime, "%Y:%m:%d %H:%M:%S")
        except Exception as ex:
            print(f"Error converting datetime string to object: {ex}")
            return None

    @property
    def resolution(self):
        return self.resolution_x, self.resolution_y

    @property
    def resolution_x(self):
        return self.metadata.resolution_x

    @property
    def resolution_y(self):
        return self.metadata.resolution_y

    @property
    def center_pixel(self):
        return self.resolution_x/2, self.resolution_y/2

    @property
    def altitude_ft(self):
        return int(meters_to_feet(self.altitude))

    @property
    def coordinates(self):
        return self.latitude, self.longitude

    @property
    def coordinates_valid(self):
        return self.latitude != 0 and self.longitude != 0

    @property
    def unvalidated_predictions(self):
        return [prediction for prediction in self.predictions
                if prediction.validation_state == ValidationState.UNVALIDATED]

    @property
    def parent_dir(self):
        return os.path.dirname(self.file_path)

    @staticmethod
    def is_valid_distance_to_neighbor_image(distance):
        return SurveyImage.config.MIN_DISTANCE_FOR_DIRECTION_CALCULATION <= distance <= \
               SurveyImage.config.MAX_DISTANCE_FOR_DIRECTION_CALCULATION

    def get_camera_orientation(self, ignore_calibration=False, ignore_inclinometer=False):
        if self.camera is None:
            return None
        elif ignore_calibration:
            return self.camera.orientation
        elif ignore_inclinometer:
            return self.camera.get_calibrated_orientation(inclinometer_data=None)
        else:
            return self.camera.get_calibrated_orientation(inclinometer_data=self.inclinometer_data)

    def reload_metadata(self):
        self.metadata = ImageMetadata(self.file_path)

    def rename_image(self, file_name):
        new_file_path = os.path.normpath(os.path.join(self.parent_dir, file_name))
        os.rename(self.file_path, new_file_path)
        self.file_path = new_file_path
        self.file_name = file_name or os.path.basename(self.file_path)

    def update_file_path(self, file_path):
        if not os.path.exists(file_path):
            raise FileExistsError(f"Error updating survey image file path. File does not exist: '{file_path}'")
        self.file_path = file_path
        self.file_name = os.path.basename(file_path)

    def reset_validations(self):
        for prediction in self.predictions:
            prediction.reset_validation()

    def set_prediction_results(self, prediction: PredictionResult):
        self.has_been_processed = True
        self.predictions = [ObjectPredictionData(p, self.file_name) for p in prediction.object_prediction_list]
        self.num_otters = sum(1 for i in prediction.object_prediction_list
                              if i.score.value > SurveyImage.config.PREDICTION_CONFIDENCE_CUTOFF)

    def load_gps_data(self):
        try:
            gps_data = gpsphoto.getGPSData(self.file_path)
            lat = gps_data['Latitude']
            lon = gps_data['Longitude']
            alt = gps_data['Altitude']
            return lat, lon, alt
        except KeyError as ke:
            msg = f"Error occurred while reading GPS data for ({self.file_path}). "
            if self.config.REQUIRE_GPS:
                print(msg)
                raise ke
            else:
                msg += "Ignoring error due to config Setting: 'REQUIRE_GPS = False'"
                print(msg)
                return 0, 0, 0
