from Processing.predict import run_image_detection
from Processing.survey_processing import pre_processing, post_processing
from select_survey import load_survey

survey = load_survey()
pre_processing(survey)
run_image_detection(survey)
post_processing(survey)
survey.save()
