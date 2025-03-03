from Processing.survey_processing import pre_processing, post_processing
from select_survey import load_survey

survey = load_survey()
pre_processing(survey, force=True)
post_processing(survey)
survey.save()
