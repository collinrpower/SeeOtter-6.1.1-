import os
from functools import partial
from kivy.clock import Clock
from Config.otter_checker_config import OtterCheckerConfig
from Controller.see_otter_controller_base import SeeOtterControllerBase, OTTER_CHECKER_MODE, \
    SeeOtterState
from Controller.image_filter_controller import ImageFilterController
from Controller.survey_command_controller import SurveyCommandController
from SurveyEntities.object_prediction_data import ObjectPredictionData, ValidationState
from SurveyEntities.survey import Survey
from SurveyEntities.survey_image import SurveyImage
from Utilities.utilities import index_out_of_range, loop_iterator, open_explorer, get_root_path
from View.Popups.clone_filtered_survey_popup import CloneFilteredSurveyPopup
from View.Widgets.pannable_image import PannableImage
from View.Windows.see_otter_window_base import SeeOtterWindowBase
from config import USER_GUIDE_FILE


class SeeOtterController(SeeOtterControllerBase):
    """
    Main controller for OtterChecker. Manages state and interactions between view and survey entities.
    """

    window = None

    def __init__(self, window: SeeOtterWindowBase, survey: Survey = None):
        super().__init__()
        self.load_config()
        self.filter_controller = ImageFilterController(apply_filter_callback=self.apply_image_filters)
        self.survey = survey
        self.window = window
        self.commands = SurveyCommandController(controller=self)

    def load_config(self):
        SeeOtterController.config = OtterCheckerConfig().load()

    def on_survey(self, *args):
        self.images = self.filter_controller.get_filtered_images(self.survey)
        if self.survey:
            self.state = SeeOtterState.SURVEY_LOADED
            self.set_annotation_categories()
            self.set_current_image(index=0)
        else:
            self.state = SeeOtterState.NO_SURVEY_LOADED
            self.annotation_categories = []

    @property
    def image_panel(self):
        return self.window.otter_checker_screen.image_panel

    @property
    def processed_images(self):
        return self.survey.processed_images

    def add_prediction(self, image: SurveyImage, prediction: ObjectPredictionData):
        self.has_unsaved_changes = True
        image.predictions.append(prediction)
        self.predictions.append(prediction)
        self.image_panel.redraw_annotations()

    def remove_prediction(self, image, prediction):
        self.has_unsaved_changes = True
        image.predictions.remove(prediction)
        self.predictions.remove(prediction)
        self.image_panel.redraw_annotations()

    def toggle_draw_mode(self):
        self.mode = OTTER_CHECKER_MODE.DRAW_ANNOTATION if not self.draw_mode else OTTER_CHECKER_MODE.DEFAULT
        print(f"Toggle Draw Mode: {self.draw_mode}")

    def set_current_annotation_category(self, annotation_name, annotation_id, *args):
        print(f"Set current category: {annotation_name}, {annotation_id}")
        self.current_annotation_category = annotation_name
        self.current_annotation_id = annotation_id

    def next_image(self, *kwargs):
        print("Next Image")
        if len(self.images) > 1:
            self.image_idx = self.image_idx + 1 if self.image_idx < len(self.images) - 1 else 0
            self.current_image = self.images[self.image_idx]
            self.predictions = self.filter_controller.get_filtered_predictions(self.current_image)
            self.prediction_idx = 0
            self.current_prediction = self.predictions[self.prediction_idx] if self.predictions else None

    def previous_image(self, *kwargs):
        print("Previous Image")
        if len(self.images) > 1:
            self.image_idx = self.image_idx - 1 if self.image_idx > 0 else len(self.images) - 1
            self.current_image = self.images[self.image_idx]
            self.predictions = self.filter_controller.get_filtered_predictions(self.current_image)
            self.prediction_idx = len(self.predictions) - 1
            self.current_prediction = self.predictions[self.prediction_idx] if self.predictions else None

    def next_prediction(self, *kwargs):
        self.prediction_idx += 1
        if index_out_of_range(self.prediction_idx, self.predictions):
            self.select_next_image_with_predictions(direction=1)
        else:
            self.update_current_prediction(self.predictions[self.prediction_idx])

    def previous_prediction(self, *kwargs):
        self.prediction_idx -= 1
        if index_out_of_range(self.prediction_idx, self.predictions):
            self.select_next_image_with_predictions(direction=-1)
        else:
            self.update_current_prediction(self.predictions[self.prediction_idx])

    def select_next_image_with_predictions(self, direction=1):
        for image in loop_iterator(self.images, self.image_idx, start_at_next=True, direction=direction):
            filtered_predictions = self.filter_controller.get_filtered_predictions(image)
            if len(filtered_predictions) > 0:
                self.set_current_image(image=image)
                self.prediction_idx = 0 if direction == 1 else len(filtered_predictions) - 1
                self.predictions = filtered_predictions
                self.current_prediction = self.predictions[self.prediction_idx]
                return

    def update_current_prediction(self, prediction):
        self.current_prediction = prediction

    def set_current_image_validation_state(self, validation_state, confidence=None):
        if not self.current_prediction:
            print("Warning: Tried to validate non-existant prediction")
            return
        self.current_prediction.validate(validation_state=validation_state, validated_by=self.config.VALIDATOR_NAME)
        if confidence:
            self.current_prediction.score = confidence
        self.image_panel.select_prediction(None)
        self.image_panel.redraw_annotations()
        Clock.schedule_once(self.next_prediction, self.config.POST_VALIDATION_DELAY)

    def set_default_image(self):
        self.image_idx = 0
        self.current_image = PannableImage.background_image

    def get_unvalidated_predictions(self):
        return [prediction for prediction in self.predictions
                if prediction.validation_state == ValidationState.UNVALIDATED]

    def tag_selected(self, *args):
        self.has_unsaved_changes = True
        tag = args[1]
        self.current_image.tags.apply_tag(tag)

    def set_current_prediction(self, prediction):
        if prediction is not self.current_prediction:
            if not self.predictions.__contains__(prediction):
                print("Warning: Cannot select prediction not contained in current predictions.")
            else:
                self.prediction_idx = self.predictions.index(prediction)
                self.current_prediction = prediction

    def set_current_image(self, image=None, index=None):
        if not image and not index:
            self.set_default_image()
        if image and index:
            raise ValueError("Must supply either index or image to set current image, not both.")
        elif index is not None:
            if index + 1 <= len(self.images):
                self.image_idx = index
                new_image = self.images[index]
                self.current_image = new_image
            else:
                print("Current image index out of range")
        elif image is not None:
            self.image_idx = self.images.index(image)
            self.current_image = image
        else:
            raise Exception(f"Cannot set current image to type: {type(image)}")

    def apply_image_filters(self):
        print("img filter")
        self.image_idx = 0
        self.prediction_idx = 0

        self.images = self.filter_controller.get_filtered_images(self.survey)
        if self.images:
            self.image_idx = self.get_closest_image_index()
            self.set_current_image(index=self.image_idx)
        else:
            self.set_default_image()

        self.predictions = self.filter_controller.get_filtered_predictions(self.current_image)
        if self.predictions:
            Clock.schedule_once(lambda x: self.set_current_prediction(self.predictions[self.prediction_idx]), .75)
        else:
            self.current_prediction = None

    def get_closest_image_index(self):
        """
        Updates image_idx to reflect actual index of current image. If images does not contain current
        image, set image_idx to the next closest image.
        """
        new_image_idx = 0
        if self.images.__contains__(self.current_image):
            new_image_idx = self.images.index(self.current_image)
        elif isinstance(self.current_image, SurveyImage):
            previous_image_id = self.current_image.id
            image_ids_to_search = [image.id for image in self.images if image.id < previous_image_id]
            if image_ids_to_search:
                closest_id = max(image_ids_to_search)
                new_image = next(image for image in self.images if image.id == closest_id)
                new_image_idx = self.images.index(new_image)
        else:
            new_image_idx = 0
        return new_image_idx

    def set_annotation_categories(self):
        category_set = set([(prediction.category_name, prediction.category_id)
                            for prediction in self.survey.predictions])
        categories = list(category_set)
        category_names = [category[0] for category in categories]

        for default_category, default_id in self.config.ANNOTATION_CATEGORIES:
            if not category_names.__contains__(default_category):
                categories.append((default_category, default_id))

        self.annotation_categories = categories
        self.set_default_annotation_category()

    def set_default_annotation_category(self):
        if len(self.annotation_categories) > 0:
            default = self.annotation_categories[0]
            self.set_current_annotation_category(default[0], default[1])
        else:
            self.set_current_annotation_category("None", -1)

    def open_clone_filtered_survey_popup(self, *args):
        popup = CloneFilteredSurveyPopup(command_controller=self.commands, controller=self)
        popup.open()

    def validate_current_selection(self, validation_state, *args):
        self.has_unsaved_changes = True
        self.set_current_image_validation_state(validation_state)

    def save(self, update_status_message=True, *args):
        if update_status_message:
            self.program_status_message = "Saving Survey..."
            Clock.schedule_once(partial(self.save, False))
            return
        self.survey.save()
        self.has_unsaved_changes = False
        self.program_status_message = ""
        self.set_snackbar_message(f"Saved survey: {self.survey.survey_name}")

    def load_survey(self, survey, update_status_message=True, *args):
        self.commands.load_survey(survey=survey)
