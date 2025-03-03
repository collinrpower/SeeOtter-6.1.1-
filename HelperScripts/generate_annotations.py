from DataGenerators.AnnotationFormats.yolo_annotation import YoloAnnotation
from DataGenerators.annotation_generator import AnnotationGenerator
from select_survey import load_survey

survey = load_survey()
annotation_generator = AnnotationGenerator(survey, YoloAnnotation())
annotation_generator.generate()
