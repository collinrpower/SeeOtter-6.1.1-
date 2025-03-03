from abc import abstractmethod
from Utilities.custom_datatypes import ImagePredictions


class AnnotationFormat:

    @property
    @abstractmethod
    def name(self):
        pass

    @abstractmethod
    def get_output_file_name(self, survey_image):
        pass

    @abstractmethod
    def generate_file_content(self, image_predictions: ImagePredictions):
        pass
