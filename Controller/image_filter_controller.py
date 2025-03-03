from typing import List
from kivy.properties import BooleanProperty
from Controller.image_filter_controller_interface import ImageFilterControllerInterface
from SurveyEntities.object_prediction_data import ObjectPredictionData, ValidationState
from SurveyEntities.survey import Survey
from SurveyEntities.survey_image import SurveyImage


def count_unvalidated_predictions(predictions: List[ObjectPredictionData]):
    return len([prediction for prediction in predictions
                if prediction.validation_state == ValidationState.UNVALIDATED])


def count_validated_predictions(predictions: List[ObjectPredictionData]):
    return len([prediction for prediction in predictions
                if prediction.validation_state != ValidationState.UNVALIDATED])


class ImageFilterController(ImageFilterControllerInterface):
    """
    Filters images and predictions based off current settings.
    """

    def get_filtered_images(self, survey: Survey):
        filtered_images = []
        if not isinstance(survey, Survey):
            return filtered_images
        for image in survey.images:
            predictions = self.get_filtered_predictions(image)
            num_predictions = len(predictions)
            if not self.show_images_with_no_predictions and num_predictions == 0:
                continue
            filtered_images.append(image)

        return filtered_images

    def get_filtered_predictions(self, image: SurveyImage):
        filtered_predictions = []
        if not isinstance(image, SurveyImage):
            return filtered_predictions
        for prediction in image.predictions:
            if prediction.score < self.confidence_cutoff:
                continue
            if prediction.validation_state == ValidationState.UNVALIDATED and not self.show_unvalidated_validations:
                continue
            if prediction.validation_state == ValidationState.CORRECT and not self.show_correct_validations:
                continue
            if prediction.validation_state == ValidationState.INCORRECT and not self.show_incorrect_validations:
                continue
            if prediction.validation_state == ValidationState.AMBIGUOUS and not self.show_ambiguous_validations:
                continue
            filtered_predictions.append(prediction)

        return filtered_predictions
