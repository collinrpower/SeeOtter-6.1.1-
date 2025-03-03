from Processing.survey_processing import vote_ambiguous_validations
from select_survey import load_survey

survey = load_survey()
vote_ambiguous_validations(survey)
