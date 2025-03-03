from SurveyEntities.waldo_survey import WaldoSurvey
from select_survey import *

# Select Survey Type
survey_types = [Survey, WaldoSurvey]
survey_type = survey_types[1]

survey_name = get_survey_name()
survey_image_path = get_survey_image_path()
survey_path = get_survey_path()
print("Creating new survey: " + survey_name)
survey = survey_type.new(survey_name=survey_name, survey_path=survey_path, images_dir=survey_image_path)
print("Finished creating new survey: " + survey_name)
