from SurveyEntities.survey import Survey
from SurveyEntities.waldo_survey import WaldoSurvey

image_day = r"D:\Southeast\Waldo\2022\06_14"
survey = WaldoSurvey.create_from_waldo_survey(image_day)
print(survey)
