import os
import shutil
from pathlib import Path
from unittest import TestCase

from Processing.survey_processing import clone_filtered_survey
from SurveyEntities.object_prediction_data import ObjectPredictionData, ValidationState
from SurveyEntities.survey import Survey
from UnitTests import unit_test_helpers


def count_files_in_dir(path):
    return len([file for file in os.listdir(path)])


class Test(TestCase):

    def test_clone_filtered_survey(self):
        new_survey_name = "_TestCloneFilteredSurvey"
        survey_path = Survey.get_default_survey_path(new_survey_name)
        if os.path.isdir(survey_path):
            shutil.rmtree(survey_path)
        survey = Survey.new(new_survey_name)
        unit_test_helpers.copy_test_images_to(survey.images_dir)
        survey.load_new_images()

        survey.images[0].predictions.append(ObjectPredictionData(validation_state=ValidationState.CORRECT))
        survey.images[0].predictions.append(ObjectPredictionData(validation_state=ValidationState.INCORRECT))
        survey.images[0].predictions.append(ObjectPredictionData(validation_state=ValidationState.UNVALIDATED))
        survey.images[0].predictions.append(ObjectPredictionData(validation_state=ValidationState.AMBIGUOUS))

        survey.images[1].predictions.append(ObjectPredictionData(validation_state=ValidationState.CORRECT))
        survey.images[1].predictions.append(ObjectPredictionData(validation_state=ValidationState.INCORRECT))
        survey.images[1].predictions.append(ObjectPredictionData(validation_state=ValidationState.UNVALIDATED))
        survey.images[1].predictions.append(ObjectPredictionData(validation_state=ValidationState.AMBIGUOUS))

        survey.images[2].predictions.append(ObjectPredictionData(validation_state=ValidationState.INCORRECT))
        survey.images[2].predictions.append(ObjectPredictionData(validation_state=ValidationState.INCORRECT))

        survey.images[3].predictions.append(ObjectPredictionData(validation_state=ValidationState.CORRECT))
        survey.images[3].predictions.append(ObjectPredictionData(validation_state=ValidationState.CORRECT))

        survey.images[4].predictions.append(ObjectPredictionData(validation_state=ValidationState.UNVALIDATED))
        survey.images[4].predictions.append(ObjectPredictionData(validation_state=ValidationState.UNVALIDATED))

        survey.images[5].predictions.append(ObjectPredictionData(validation_state=ValidationState.AMBIGUOUS))
        survey.images[5].predictions.append(ObjectPredictionData(validation_state=ValidationState.AMBIGUOUS))

        clone1_path = clone_filtered_survey(survey, include_validation_types=[ValidationState.CORRECT],
                                            out_dir_name=new_survey_name + "_clone1", force=True)
        clone2_path = clone_filtered_survey(survey, include_validation_types=[ValidationState.INCORRECT],
                                            out_dir_name=new_survey_name + "_clone2", force=True)
        clone3_path = clone_filtered_survey(survey, include_validation_types=[ValidationState.CORRECT,
                                                                              ValidationState.AMBIGUOUS],
                                            out_dir_name=new_survey_name + "_clone3", force=True)

        clone1 = Survey.load(clone1_path)
        clone2 = Survey.load(clone2_path)
        clone3 = Survey.load(clone3_path)

        self.assertEqual(Path(clone1.project_path).name, "_TestCloneFilteredSurvey_clone1")
        self.assertEqual(Path(clone2.project_path).name, "_TestCloneFilteredSurvey_clone2")
        self.assertEqual(Path(clone3.project_path).name, "_TestCloneFilteredSurvey_clone3")

        self.assertEqual(3, len(clone1.images))
        self.assertEqual(3, count_files_in_dir(clone1.images_dir))
        self.assertEqual(0, len([prediction for prediction in clone1.predictions
                                 if prediction.validation_state != ValidationState.CORRECT]))
        self.assertEqual(4, len([prediction for prediction in clone1.predictions
                                 if prediction.validation_state == ValidationState.CORRECT]))

        self.assertEqual(3, len(clone2.images))
        self.assertEqual(3, count_files_in_dir(clone2.images_dir))
        self.assertEqual(0, len([prediction for prediction in clone2.predictions
                                 if prediction.validation_state != ValidationState.INCORRECT]))
        self.assertEqual(4, len([prediction for prediction in clone2.predictions
                                 if prediction.validation_state == ValidationState.INCORRECT]))

        self.assertEqual(4, len(clone3.images))
        self.assertEqual(4, count_files_in_dir(clone3.images_dir))
        self.assertEqual(0, len([prediction for prediction in clone3.predictions
                                 if prediction.validation_state not in [ValidationState.CORRECT,
                                                                        ValidationState.AMBIGUOUS]]))
        self.assertEqual(8, len([prediction for prediction in clone3.predictions
                                 if prediction.validation_state in [ValidationState.CORRECT,
                                                                    ValidationState.AMBIGUOUS]]))
