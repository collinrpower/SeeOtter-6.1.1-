import os
from abc import abstractmethod
from enum import Enum
from functools import partial
from kivy.clock import Clock
from kivy.event import EventDispatcher
from kivy.properties import ListProperty, ObjectProperty, NumericProperty, BooleanProperty, StringProperty
from Config.otter_checker_config import OtterCheckerConfig
from Controller.image_filter_controller_interface import ImageFilterControllerInterface
from Controller.survey_controller_base import SurveyControllerBase
from SurveyEntities.object_prediction_data import ValidationState, ObjectPredictionData
from Utilities.utilities import open_explorer, get_root_path
from config import USER_GUIDE_FILE


class OTTER_CHECKER_MODE(Enum):
    DEFAULT = 1
    DRAW_ANNOTATION = 2
    EDIT_ANNOTATION = 3


class SeeOtterState(Enum):
    NO_SURVEY_LOADED = 0
    LOADING_SURVEY = 1
    SURVEY_LOADED = 2
    PRE_PROCESSING = 3
    RUNNING_IMAGE_DETECTION = 4
    POST_PROCESSING = 5
    SAVING_SURVEY = 6
    GENERATING_RESULTS = 7
    RUNNING_COMMAND = 8


class SeeOtterControllerBase(SurveyControllerBase):

    # Data
    images = ListProperty()
    predictions = ListProperty()
    annotation_categories = ListProperty()

    # Indexes
    image_idx = NumericProperty(0)
    prediction_idx = NumericProperty(0)

    # Current Data
    current_image = ObjectProperty(allownone=True)

    current_prediction = ObjectProperty(allownone=True)
    current_annotation_category = StringProperty()
    current_annotation_id = NumericProperty()

    # State
    state = ObjectProperty(defaultvalue=SeeOtterState.NO_SURVEY_LOADED)
    mode = ObjectProperty(OTTER_CHECKER_MODE.DEFAULT)
    has_unsaved_changes = BooleanProperty(False)
    is_loading = BooleanProperty(False)
    validator_mode = BooleanProperty(True)
    gridlines_visible = BooleanProperty(False)
    config: OtterCheckerConfig = None
    snackbar_message = StringProperty()

    # Controllers
    filter_controller = ObjectProperty(allownone=True)
    commands = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def set_snackbar_message(self, message, *args, **kwargs):
        self.snackbar_message = ""
        self.snackbar_message = message

    def set_program_status_message(self, message, *args, **kwargs):
        self.program_status_message = message

    def set_idle_state(self, *args, **kwargs):
        self.state = SeeOtterState.SURVEY_LOADED if self.survey else SeeOtterState.NO_SURVEY_LOADED
        self.program_status_message = ""

    def clear_program_status_message(self, delay=0):
        if delay > 0:
            Clock.schedule_once(self.clear_program_status_message, delay)
        else:
            self.program_status_message = 0

    def refresh_survey(self, *args, **kwargs):
        survey = self.survey
        self.survey = None
        self.survey = survey
        if self.survey and self.survey.has_unsaved_changes is True:
            self.has_unsaved_changes = True

    def open_survey_dir(self, *args):
        self.open_explorer(self.survey.images_dir)

    def open_transects_dir(self, *args):
        self.open_explorer(self.survey.transect_dir)

    def open_inclinometer_dir(self, *args):
        self.open_explorer(self.survey.inclinometer_dir)

    def open_file(self, file_path, *args):
        try:
            os.startfile(file_path)
        except Exception as ex:
            self.set_snackbar_message(message=f"Error opening file ({file_path}): {ex}")

    def open_explorer(self, path, *args):
        try:
            open_explorer(path)
        except Exception as ex:
            self.set_snackbar_message(message=f"Error opening Explorer: {ex}")

    def open_user_guide(self, *args):
        self.open_file(get_root_path(USER_GUIDE_FILE))

    @property
    def draw_mode(self):
        return self.mode == OTTER_CHECKER_MODE.DRAW_ANNOTATION

    @property
    def default_mode(self):
        return self.mode == OTTER_CHECKER_MODE.DEFAULT

    @property
    def edit_mode(self):
        return self.mode == OTTER_CHECKER_MODE.EDIT_ANNOTATION

    @abstractmethod
    def add_prediction(self, image, prediction):
        pass

    @abstractmethod
    def remove_prediction(self, image, prediction):
        pass

    @abstractmethod
    def toggle_draw_mode(self):
        pass

    @abstractmethod
    def set_current_annotation_category(self, annotation_name, annotation_id, *args):
        pass

    @abstractmethod
    def next_image(self):
        pass

    @abstractmethod
    def previous_image(self):
        pass

    @abstractmethod
    def next_prediction(self):
        pass

    @abstractmethod
    def previous_prediction(self):
        pass

    @abstractmethod
    def set_current_image_validation_state(self, validation_state: ValidationState):
        pass

    @abstractmethod
    def tag_selected(self, tag, *args):
        pass

    @abstractmethod
    def set_current_prediction(self, prediction):
        pass

    @abstractmethod
    def save(self, instance, value):
        pass

    def open_new_survey_window(self, *args, **kwargs):
        pass

    def open_otter_checker(self, *args, **kwargs):
        pass
