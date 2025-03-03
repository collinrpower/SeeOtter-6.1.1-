from SurveyEntities.survey import Survey
from SurveyEntities.waldo_survey import WaldoSurvey
from select_survey import get_survey_name, get_survey_image_path, get_survey_path

# Select Survey Type
survey_types = [Survey, WaldoSurvey]
survey_type = survey_types[1]

survey_name = get_survey_name()
image_dir = get_survey_image_path()
survey_path = get_survey_path()
survey = survey_type.new(survey_name=survey_name, survey_path=survey_path, images_dir=image_dir, overwrite=True)
