from abc import abstractmethod
from kivy.event import EventDispatcher
from kivy.properties import BoundedNumericProperty, BooleanProperty
from Config.otter_checker_config import OtterCheckerConfig
from SurveyEntities.survey import Survey
from SurveyEntities.survey_image import SurveyImage


class ImageFilterControllerInterface(EventDispatcher):

    settings_changed = BooleanProperty(False)

    confidence_cutoff = BoundedNumericProperty(OtterCheckerConfig.instance().MIN_CONFIDENCE, min=0, max=1)
    show_images_with_no_predictions = BooleanProperty(OtterCheckerConfig.instance().SHOW_IMAGES_WITH_NO_PREDICTIONS)

    show_correct_validations = BooleanProperty(OtterCheckerConfig.instance().OTTER_CHECKER_SHOW_CORRECT_VALIDATIONS)
    show_incorrect_validations = BooleanProperty(OtterCheckerConfig.instance().OTTER_CHECKER_SHOW_INCORRECT_VALIDATIONS)
    show_ambiguous_validations = BooleanProperty(OtterCheckerConfig.instance().OTTER_CHECKER_SHOW_AMBIGUOUS_VALIDATIONS)
    show_unvalidated_validations = BooleanProperty(OtterCheckerConfig.instance().OTTER_CHECKER_SHOW_UNVALIDATED_VALIDATIONS)

    def __init__(self, apply_filter_callback, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_filter = apply_filter_callback
        self.bind_properties_update()

    def bind_properties_update(self):
        self.bind(confidence_cutoff=self.on_filter_settings_changed)
        self.bind(show_images_with_no_predictions=self.on_filter_settings_changed)
        self.bind(show_correct_validations=self.on_filter_settings_changed)
        self.bind(show_incorrect_validations=self.on_filter_settings_changed)
        self.bind(show_ambiguous_validations=self.on_filter_settings_changed)
        self.bind(show_unvalidated_validations=self.on_filter_settings_changed)

    def on_filter_settings_changed(self, instance, value):
        self.settings_changed = True

    @abstractmethod
    def get_filtered_images(self, survey: Survey):
        pass

    @abstractmethod
    def get_filtered_predictions(self, image: SurveyImage):
        pass
