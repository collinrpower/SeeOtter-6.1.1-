from SurveyEntities.waldo_survey import WaldoSurvey
from select_survey import *

# Select Survey Type
survey_types = [Survey, WaldoSurvey]
survey_type = survey_types[1]

Survey.upgrade_project_version(survey_name=get_survey_name(),
                               survey_path=get_survey_path(),
                               images_dir=get_survey_image_path(),
                               survey_type=survey_type,
                               force=True)
