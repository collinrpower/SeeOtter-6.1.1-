from os.path import exists, join
from Config.serializable_config_base import SerializableConfigBase
from SurveyEntities.object_prediction_data import ValidationState
from Utilities.json_convert import JsonConvert
from Utilities.utilities import get_root_path
from config import OTTER_CHECKER_CONFIG_FILE


@JsonConvert.register
class OtterCheckerConfig(SerializableConfigBase):
    """
    Serializable config for OtterChecker
    """

    _instance = None
    _default = None

    def __init__(self, **kwargs):

        # Default Filter Settings
        self.MIN_CONFIDENCE = .4
        self.SHOW_IMAGES_WITH_NO_PREDICTIONS = False
        self.OTTER_CHECKER_SHOW_CORRECT_VALIDATIONS = True
        self.OTTER_CHECKER_SHOW_INCORRECT_VALIDATIONS = True
        self.OTTER_CHECKER_SHOW_AMBIGUOUS_VALIDATIONS = True
        self.OTTER_CHECKER_SHOW_UNVALIDATED_VALIDATIONS = True

        # Behavior
        self.NEXT_PREDICTION_TRANSITION_TIME = .15
        self.POST_VALIDATION_DELAY = .2
        self.DEFAULT_ZOOM = 5
        self.TOOLTIP_DELAY = 1.0
        self.GRID_COLUMNS = 4
        self.GRID_ROWS = 4

        # Validation Settings
        self.VALIDATOR_MODE = True
        self.VALIDATOR_NAME = None

        # Style
        self.ACCENT_COLOR = "Orange"
        self.BUTTON_FONT_SIZE = 24
        self.LEFT_PANEL_WIDTH = 340
        self.BUTTON_BACKGROUND_COLOR = (.2, .2, .22, 1)
        self.GRIDLINE_COLOR = (.9, .9, .9, 1)

        # Validation Colors
        self.ANNOTATION_UNVALIDATED_COLOR = [.4, .4, .4, 1]
        self.ANNOTATION_CORRECT_COLOR = [.05, .8, .05, 1]
        self.ANNOTATION_INCORRECT_COLOR = [1, 0, 0, 1]
        self.ANNOTATION_AMBIGUOUS_COLOR = [.3, .6, .9, 1]
        self.ANNOTATION_SELECTED_COLOR = [.9, .9, 0, 1]

        self.IMAGE_TAGS = [
            "Whitecaps",
            "Glacial Water",
            "Kelp",
            "Land",
            "Fisheries",
            "Overexposed",
            "Underexposed",
            "Blurry",
            "Grainy",
            'Cool',
            'Potential Missed',
            "Birds"
        ]

        self.ANNOTATION_CATEGORIES = [
            ("o", 0),
            ("p", 1),
            ("b", 2),
            ("seal", 3),
            ('sl', 4),
            ('porp', 5)
        ]

        self.__dict__.update(kwargs)

    def get_validation_color(self, validation_state: ValidationState):
        if validation_state == ValidationState.UNVALIDATED:
            return self.ANNOTATION_UNVALIDATED_COLOR
        if validation_state == ValidationState.CORRECT:
            return self.ANNOTATION_CORRECT_COLOR
        if validation_state == ValidationState.INCORRECT:
            return self.ANNOTATION_INCORRECT_COLOR
        if validation_state == ValidationState.AMBIGUOUS:
            return self.ANNOTATION_AMBIGUOUS_COLOR

    def get_file_path(self):
        return join(get_root_path(OTTER_CHECKER_CONFIG_FILE))

    def load(self, path=None):
        config = super().load(path)
        OtterCheckerConfig._instance = config
        return config
