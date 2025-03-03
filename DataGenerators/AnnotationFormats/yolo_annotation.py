from DataGenerators.AnnotationFormats.annotation_format import AnnotationFormat
from DataGenerators.annotation_generator import ImagePredictions
from Utilities.utilities import get_file_name_without_extension, get_normalized_pixel_pos


class YoloAnnotation(AnnotationFormat):

    @property
    def name(self):
        return "YOLOv5"

    def get_output_file_name(self, survey_image):
        file_name = get_file_name_without_extension(survey_image.file_path)
        return file_name + ".txt"

    def generate_file_content(self, image_predictions: ImagePredictions):
        lines = []
        survey_image, predictions = image_predictions
        for prediction in predictions:
            x, y = get_normalized_pixel_pos(prediction.pixel_pos, survey_image.resolution)
            width, height = get_normalized_pixel_pos(prediction.pixel_size, survey_image.resolution)
            lines.append(f"{prediction.category_id} {x} {y} {width} {height}")

        return lines