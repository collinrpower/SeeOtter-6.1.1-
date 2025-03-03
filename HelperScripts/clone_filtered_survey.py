from pathlib import Path
from Processing.survey_processing import clone_filtered_survey
from SurveyEntities.object_prediction_data import ValidationState
from select_survey import load_survey


survey = load_survey()
include_validation_types = [ValidationState.AMBIGUOUS, ValidationState.CORRECT]
new_dir_name = str(Path(survey.project_path)) + "file_fail"
clone_filtered_survey(survey, include_validation_types, out_dir_name=new_dir_name)
