from os.path import join

from Config.serializable_config_base import SerializableConfigBase
from Utilities.json_convert import JsonConvert
from Utilities.utilities import get_root_path
from config import SEE_OTTER_CONFIG_FILE


@JsonConvert.register
class SeeOtterConfig(SerializableConfigBase):
    """
    Serializable config for OtterChecker
    """

    _instance = None
    _default = None

    def __init__(self, **kwargs):

        # Execution
        self.REQUIRE_GPS = False
        self.FAIL_ON_MISSING_EXIF_FIELD = False
        self.MIN_DISTANCE_FOR_DIRECTION_CALCULATION = 10
        self.MAX_DISTANCE_FOR_DIRECTION_CALCULATION = 400
        self.NEAR_TEMPORAL_ZONE_TOLERANCE = 1.5  # 1 - No tolerance, 2 - Twice area of original image projection
        self.IMAGE_COORDINATE_CHUNKING_DEGREES_LAT = .007
        self.IMAGE_COORDINATE_CHUNKING_DEGREES_LON = .011

        # Predictions
        self.MAX_PREDICTION_RETRIES = 2
        self.PREDICTION_CONFIDENCE_CUTOFF = .05
        self.OTTER_CATEGORY_NAME = 'o'
        self.PREDICTION_IMAGE_SIZE = 8688
        self.SLICE_PREDICTED_IMAGES = False
        self.BACKUP_SURVEY_ON_PREDICTIONS_COMPLETE = True
        self.PREDICTION_AUTOSAVE_BATCH_SIZE = 100  # Number of predictions between autosave (-1 to disable)

        # Transects
        self.TRANSECT_LATERAL_TOLERANCE = 200
        self.TRANSECT_BEARING_TOLERANCE = 20
        self.MAX_OFF_TRANSECT_IMAGE_GAP = 30  # Max number of consecutive images that can be taken off transect and get "filled in"
        self.MIN_ON_TRANSECT_ALTITUDE_FT = 200
        self.MAX_ON_TRANSECT_ALTITUDE_FT = 1200

    @classmethod
    def instance(cls):
        if cls._instance is None:
            SeeOtterConfig().load()
        return cls._instance

    def get_file_path(self):
        return join(get_root_path(SEE_OTTER_CONFIG_FILE))

    def load(self, path=None):
        config = super().load(path)
        SeeOtterConfig._instance = config
        return config