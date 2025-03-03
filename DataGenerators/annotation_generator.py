from os import path
from typing import List
from DataGenerators.AnnotationFormats.annotation_format import AnnotationFormat
from SurveyEntities.object_prediction_data import ValidationState
from SurveyEntities.survey import Survey
from Utilities.custom_datatypes import ImagePredictions
from Utilities.utilities import *
from config import ANNOTATIONS_DIR, RESULTS_CONFIDENCE_CUTOFF


class AnnotationGenerator:

    def __init__(self, survey: Survey,
                 annotation_format: AnnotationFormat,
                 confidence_cutoff=RESULTS_CONFIDENCE_CUTOFF):
        self.survey = survey
        self.annotation_format = annotation_format
        self.confidence_cutoff = confidence_cutoff

    @property
    def annotations_dir(self):
        return self.survey.get_relative_path(ANNOTATIONS_DIR)

    @property
    def output_dir(self):
        return path.join(self.annotations_dir, self.annotation_format.name)

    def clear_output_dir(self):
        rmdir_if_exists(self.output_dir)
        os.mkdir(self.output_dir)

    def create_new_output_subdir(self, dir_name):
        dir_path = path.join(self.output_dir, dir_name)
        rmdir_if_exists(dir_path)
        mkdir_if_not_exists(dir_path)
        return dir_path

    def create_annotation_dir(self):
        mkdir_if_not_exists(self.annotations_dir)
        rmdir_if_exists(self.output_dir)
        mkdir_if_not_exists(self.output_dir)
        for validation_status in ValidationState.list():
            validation_dir = path.join(self.output_dir, validation_status)
            rmdir_if_exists(validation_dir)
            mkdir_if_not_exists(validation_dir)

    def get_image_predictions_of_validation_state(self, validation_state: ValidationState) -> List[ImagePredictions]:
        image_predictions = []
        for image in self.survey.images:
            predictions = [prediction for prediction in image.predictions
                           if prediction.validation_state == validation_state]
            if len(predictions) > 0:
                image_predictions.append(ImagePredictions(image, predictions))

        return image_predictions

    def output_annotations_to_dir(self, dst, image_predictions: List[ImagePredictions]):
        for image_prediction in image_predictions:
            file_name = self.annotation_format.get_output_file_name(image_prediction.image)
            file_path = path.join(dst, file_name)
            content = self.annotation_format.generate_file_content(image_prediction)
            with open(file_path, 'w') as f:
                f.write("\n".join(content))

    def filter_image_predictions_by_confidence_range(self, image_predictions, min, max):
        filtered_image_predictions = []
        for image, predictions in image_predictions:
            predictions = [p for p in predictions if min < p.score <= max]
            if len(predictions) > 0:
                filtered_image_predictions.append(ImagePredictions(image, predictions))
        return filtered_image_predictions

    def generate(self):
        print(f"Generating annotations at '{self.output_dir}'")
        self.clear_output_dir()
        for validation in ValidationState:
            image_predictions = self.get_image_predictions_of_validation_state(validation_state=validation)
            if len(image_predictions) == 0:
                continue
            if validation in [ValidationState.INCORRECT]:
                for confidence_rng in [(0, .5), (.5, .7), (.7, .9), (.9, 1)]:
                    min_conf, max_conf = confidence_rng
                    filtered_image_predictions = self.filter_image_predictions_by_confidence_range(image_predictions,
                                                                                                   min_conf, max_conf)
                    dir_name = f"{validation.name}_{str(min_conf).replace('.', 'p')}-{str(max_conf).replace('.', 'p')}"
                    validation_state_dir = self.create_new_output_subdir(dir_name=dir_name)
                    self.output_annotations_to_dir(validation_state_dir, filtered_image_predictions)
            validation_state_dir = self.create_new_output_subdir(dir_name=validation.name)
            self.output_annotations_to_dir(validation_state_dir, image_predictions)
