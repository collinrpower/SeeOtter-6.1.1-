import copy
import json
import time
from enum import Enum
from sahi.prediction import ObjectPrediction
from Utilities.json_convert import JsonConvert
from Utilities.utilities import set_attributes
from version import version


class ValidationState(int, Enum):
    UNVALIDATED = 0
    CORRECT = 1
    INCORRECT = 2
    AMBIGUOUS = 3


@JsonConvert.register
class ObjectPredictionData:
    """
    Represents a single prediction in an image and user validation data
    """

    # Image Info
    latitude = 0
    longitude = 0

    # Prediction Info
    score = 0.0
    xmin = 0
    xmax = 0
    ymin = 0
    ymax = 0
    category_id = -1
    category_name = ""

    # User Input
    validation_state = ValidationState.UNVALIDATED
    validated_dttm = None
    validated_by = ""
    validation_confidence = ""
    notes = ""
    original_prediction_data = None

    prediction_data_attributes = ["score", "xmin", "xmax", "ymin", "ymax", "category_id", "category_name"]

    def __init__(self, prediction: ObjectPrediction = None, image_name=None, is_user_generated=False,
                 created_by=f"SeeOtter (V{version})", **kwargs):
        self.image_name = image_name
        self.created_by = created_by

        # Calculated
        self.overlaps_image = None
        self.almost_overlaps_image = None
        self.transect_overlap_images = []

        self.is_user_generated = is_user_generated
        self.load_values_from_object_prediction(object_prediction=prediction)
        self.__dict__.update(kwargs)
        self.backup_initial_state()

    @property
    def is_validated(self):
        return self.validation_state != ValidationState.UNVALIDATED

    @property
    def is_in_temporal_overlap(self): return self.overlaps_image is not None

    @property
    def is_in_transect_overlap(self): return len(self.transect_overlap_images) > 0

    @property
    def is_near_temporal_overlap(self): return self.almost_overlaps_image is not None

    @property
    def width(self): return self.xmax - self.xmin

    @property
    def height(self): return self.ymax - self.ymin

    @property
    def x(self): return int((self.xmin + self.xmax)/2)

    @property
    def y(self): return int((self.ymin + self.ymax) / 2)

    @property
    def pixel_pos(self):
        return self.x, self.y

    @property
    def pixel_size(self):
        return self.width, self.height

    @property
    def has_been_modified(self):
        if self.original_prediction_data:
            for attr in ObjectPredictionData.prediction_data_attributes:
                if getattr(self, attr) != getattr(self.original_prediction_data, attr):
                    return True
        return False

    def to_json_string(self):
        return JsonConvert.to_json(self)

    def add_transect_overlap_image(self, image_name):
        self.transect_overlap_images.append(image_name)

    @staticmethod
    def from_json_string(data):
        prediction_dict = json.loads(data)
        prediction = ObjectPredictionData()
        set_attributes(prediction, prediction_dict)
        return prediction

    def backup_initial_state(self):
        if self.original_prediction_data:
            raise Exception("Cannot backup initial prediction data. Field is not empty.")
        self.original_prediction_data = copy.deepcopy(self)

    def update(self, **kwargs):
        allowed_attributes = ObjectPredictionData.prediction_data_attributes
        for key in kwargs.keys():
            if not allowed_attributes.__contains__(key):
                raise Exception(f"Invalid field '{key}'. Allowed fields: {allowed_attributes}")
        self.__dict__.update(kwargs)

    def validate(self, validation_state: ValidationState, validated_by="N/A"):
        self.validation_state = validation_state
        self.validated_by = validated_by
        self.validated_dttm = time.localtime()

    def load_values_from_object_prediction(self, object_prediction: ObjectPrediction):
        if object_prediction:
            self.score = object_prediction.score.value
            self.xmin = object_prediction.bbox.minx
            self.xmax = object_prediction.bbox.maxx
            self.ymin = object_prediction.bbox.miny
            self.ymax = object_prediction.bbox.maxy
            self.category_id = object_prediction.category.id
            self.category_name = object_prediction.category.name

    def reset_validation(self):
        self.validation_state = ValidationState.UNVALIDATED
