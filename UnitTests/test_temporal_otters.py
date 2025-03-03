import copy
from unittest import TestCase
from Processing.survey_processing import *
from SurveyEntities.object_prediction_data import ObjectPredictionData
from UnitTests import unit_test_helpers
from SurveyEntities.survey import Survey
from DataGenerators.map_generator import MapGenerator


def config(cls) -> SeeOtterConfig:
    return SeeOtterConfig.instance()


class TestTemporalDetection(TestCase):

    survey_name = '_TestTemporalDetection'

    @classmethod
    def setUpClass(cls):
        survey = unit_test_helpers.create_empty_survey(cls.survey_name)
        unit_test_helpers.copy_test_images_to(survey.images_dir)
        survey = Survey.load(cls.survey_name)
        calculate_bearing(survey)
        MapGenerator.survey_map(survey).save(survey.map_file_path)
        survey.save()

    def test_empty_survey_has_no_predictions(self):
        survey = Survey.load(self.survey_name)
        predictions = [prediction for image in survey.images for prediction in image.predictions]
        self.assertEqual(0, len(predictions))

    def test_get_predictions_in_temporal_zone_returns_predictions_in_temporal_zone(self):
        survey = Survey.load(self.survey_name)

        test_prediction_top1 = ObjectPredictionData()
        test_prediction_top1.score = 1
        test_prediction_top1.xmin = 3000
        test_prediction_top1.xmax = 3100
        test_prediction_top1.ymin = 50
        test_prediction_top1.ymax = 100

        test_prediction_top2 = ObjectPredictionData()
        test_prediction_top2.score = 1
        test_prediction_top2.xmin = 250
        test_prediction_top2.xmax = 300
        test_prediction_top2.ymin = 0
        test_prediction_top2.ymax = 10

        test_prediction_bottom_1 = ObjectPredictionData()
        test_prediction_bottom_1.score = 1
        test_prediction_bottom_1.xmin = 3000
        test_prediction_bottom_1.xmax = 3100
        test_prediction_bottom_1.ymin = 5650
        test_prediction_bottom_1.ymax = 5700

        test_prediction_bottom_2 = ObjectPredictionData()
        test_prediction_bottom_2.score = 1
        test_prediction_bottom_2.xmin = 250
        test_prediction_bottom_2.xmax = 300
        test_prediction_bottom_2.ymin = 5650
        test_prediction_bottom_2.ymax = 5700

        survey.get_image('0_000_00_000.jpg').predictions.append(copy.deepcopy(test_prediction_top1))
        survey.get_image('0_000_00_000.jpg').predictions.append(copy.deepcopy(test_prediction_top2))
        survey.get_image('1_000_00_000.jpg').predictions.append(copy.deepcopy(test_prediction_top1))
        survey.get_image('1_000_00_000.jpg').predictions.append(copy.deepcopy(test_prediction_top2))

        survey.get_image('0_000_00_001.jpg').predictions.append(copy.deepcopy(test_prediction_bottom_1))
        survey.get_image('0_000_00_001.jpg').predictions.append(copy.deepcopy(test_prediction_bottom_2))
        survey.get_image('1_000_00_001.jpg').predictions.append(copy.deepcopy(test_prediction_bottom_1))
        survey.get_image('1_000_00_001.jpg').predictions.append(copy.deepcopy(test_prediction_bottom_2))

        survey.get_image('0_000_00_002.jpg').predictions.append(copy.deepcopy(test_prediction_top1))
        survey.get_image('0_000_00_002.jpg').predictions.append(copy.deepcopy(test_prediction_top2))
        survey.get_image('1_000_00_002.jpg').predictions.append(copy.deepcopy(test_prediction_top1))
        survey.get_image('1_000_00_002.jpg').predictions.append(copy.deepcopy(test_prediction_top2))

        survey.get_image('0_000_00_003.jpg').predictions.append(copy.deepcopy(test_prediction_top1))
        survey.get_image('0_000_00_003.jpg').predictions.append(copy.deepcopy(test_prediction_top2))
        survey.get_image('1_000_00_003.jpg').predictions.append(copy.deepcopy(test_prediction_top1))
        survey.get_image('1_000_00_003.jpg').predictions.append(copy.deepcopy(test_prediction_top2))

        survey.get_image('0_000_00_003.jpg').predictions.append(copy.deepcopy(test_prediction_bottom_1))
        survey.get_image('0_000_00_003.jpg').predictions.append(copy.deepcopy(test_prediction_bottom_2))
        survey.get_image('1_000_00_003.jpg').predictions.append(copy.deepcopy(test_prediction_bottom_1))
        survey.get_image('1_000_00_003.jpg').predictions.append(copy.deepcopy(test_prediction_bottom_2))

        for image in survey.images:
            for prediction in image.predictions:
                prediction.image_name = image.file_path

        pre_processing(survey)
        post_processing(survey)

        temporal_predictions = survey.get_predictions_in_temporal_zone()
        #MapGenerator.survey_otter_map(survey).save(survey.otter_map_file_path)

        self.assertEqual(20, len(temporal_predictions))

    def test_get_predictions_in_temporal_zone_doesnt_return_predictions_not_in_temporal_zone(self):
        survey = Survey.load(self.survey_name)

        test_prediction_top1 = ObjectPredictionData()
        test_prediction_top1.score = 1
        test_prediction_top1.xmin = 3000
        test_prediction_top1.xmax = 3100
        test_prediction_top1.ymin = 50
        test_prediction_top1.ymax = 100

        test_prediction_top2 = ObjectPredictionData()
        test_prediction_top2.score = 1
        test_prediction_top2.xmin = 250
        test_prediction_top2.xmax = 300
        test_prediction_top2.ymin = 0
        test_prediction_top2.ymax = 10

        test_prediction_bottom_1 = ObjectPredictionData()
        test_prediction_bottom_1.score = 1
        test_prediction_bottom_1.xmin = 3000
        test_prediction_bottom_1.xmax = 3100
        test_prediction_bottom_1.ymin = 5650
        test_prediction_bottom_1.ymax = 5700

        test_prediction_bottom_2 = ObjectPredictionData()
        test_prediction_bottom_2.score = 1
        test_prediction_bottom_2.xmin = 250
        test_prediction_bottom_2.xmax = 300
        test_prediction_bottom_2.ymin = 5650
        test_prediction_bottom_2.ymax = 5700

        survey.get_image('0_000_00_000.jpg').predictions.append(copy.deepcopy(test_prediction_bottom_1))
        survey.get_image('0_000_00_000.jpg').predictions.append(copy.deepcopy(test_prediction_bottom_2))
        survey.get_image('1_000_00_000.jpg').predictions.append(copy.deepcopy(test_prediction_bottom_1))
        survey.get_image('1_000_00_000.jpg').predictions.append(copy.deepcopy(test_prediction_bottom_2))

        survey.get_image('0_000_00_001.jpg').predictions.append(copy.deepcopy(test_prediction_top1))
        survey.get_image('0_000_00_001.jpg').predictions.append(copy.deepcopy(test_prediction_top2))
        survey.get_image('1_000_00_001.jpg').predictions.append(copy.deepcopy(test_prediction_top1))
        survey.get_image('1_000_00_001.jpg').predictions.append(copy.deepcopy(test_prediction_top2))

        survey.get_image('0_000_00_002.jpg').predictions.append(copy.deepcopy(test_prediction_bottom_1))
        survey.get_image('0_000_00_002.jpg').predictions.append(copy.deepcopy(test_prediction_bottom_2))
        survey.get_image('1_000_00_002.jpg').predictions.append(copy.deepcopy(test_prediction_bottom_1))
        survey.get_image('1_000_00_002.jpg').predictions.append(copy.deepcopy(test_prediction_bottom_2))

        survey.get_image('0_000_00_004.jpg').predictions.append(copy.deepcopy(test_prediction_top1))
        survey.get_image('0_000_00_004.jpg').predictions.append(copy.deepcopy(test_prediction_top2))
        survey.get_image('1_000_00_004.jpg').predictions.append(copy.deepcopy(test_prediction_top1))
        survey.get_image('1_000_00_004.jpg').predictions.append(copy.deepcopy(test_prediction_top2))

        for image in survey.images:
            for prediction in image.predictions:
                prediction.image_name = image.file_path

        pre_processing(survey)
        post_processing(survey)

        temporal_predictions = survey.get_predictions_in_temporal_zone()
        #MapGenerator.survey_otter_map(survey).save(survey.otter_map_file_path)

        self.assertEqual(0, len(temporal_predictions))

    def test_get_predictions_in_temporal_zone_doesnt_return_predictions_not_in_temporal_zone_all_node(self):
        survey = Survey.load(self.survey_name)

        test_prediction_top1 = ObjectPredictionData()
        test_prediction_top1.score = 1
        test_prediction_top1.xmin = 3000
        test_prediction_top1.xmax = 3100
        test_prediction_top1.ymin = 50
        test_prediction_top1.ymax = 100

        test_prediction_top2 = ObjectPredictionData()
        test_prediction_top2.score = 1
        test_prediction_top2.xmin = 250
        test_prediction_top2.xmax = 300
        test_prediction_top2.ymin = 0
        test_prediction_top2.ymax = 10

        test_prediction_bottom_1 = ObjectPredictionData()
        test_prediction_bottom_1.score = 1
        test_prediction_bottom_1.xmin = 3000
        test_prediction_bottom_1.xmax = 3100
        test_prediction_bottom_1.ymin = 5650
        test_prediction_bottom_1.ymax = 5700

        test_prediction_bottom_2 = ObjectPredictionData()
        test_prediction_bottom_2.score = 1
        test_prediction_bottom_2.xmin = 250
        test_prediction_bottom_2.xmax = 300
        test_prediction_bottom_2.ymin = 5650
        test_prediction_bottom_2.ymax = 5700

        survey.get_image('0_000_00_000.jpg').predictions.append(copy.deepcopy(test_prediction_top1))
        survey.get_image('0_000_00_000.jpg').predictions.append(copy.deepcopy(test_prediction_top2))
        survey.get_image('1_000_00_000.jpg').predictions.append(copy.deepcopy(test_prediction_top1))
        survey.get_image('1_000_00_000.jpg').predictions.append(copy.deepcopy(test_prediction_top2))

        survey.get_image('0_000_00_000.jpg').predictions.append(copy.deepcopy(test_prediction_bottom_1))
        survey.get_image('0_000_00_000.jpg').predictions.append(copy.deepcopy(test_prediction_bottom_2))
        survey.get_image('1_000_00_000.jpg').predictions.append(copy.deepcopy(test_prediction_bottom_1))
        survey.get_image('1_000_00_000.jpg').predictions.append(copy.deepcopy(test_prediction_bottom_2))

        survey.get_image('0_000_00_001.jpg').predictions.append(copy.deepcopy(test_prediction_top1))
        survey.get_image('0_000_00_001.jpg').predictions.append(copy.deepcopy(test_prediction_top2))
        survey.get_image('1_000_00_001.jpg').predictions.append(copy.deepcopy(test_prediction_top1))
        survey.get_image('1_000_00_001.jpg').predictions.append(copy.deepcopy(test_prediction_top2))

        survey.get_image('0_000_00_002.jpg').predictions.append(copy.deepcopy(test_prediction_bottom_1))
        survey.get_image('0_000_00_002.jpg').predictions.append(copy.deepcopy(test_prediction_bottom_2))
        survey.get_image('1_000_00_002.jpg').predictions.append(copy.deepcopy(test_prediction_bottom_1))
        survey.get_image('1_000_00_002.jpg').predictions.append(copy.deepcopy(test_prediction_bottom_2))

        survey.get_image('0_000_00_004.jpg').predictions.append(copy.deepcopy(test_prediction_top1))
        survey.get_image('0_000_00_004.jpg').predictions.append(copy.deepcopy(test_prediction_top2))
        survey.get_image('1_000_00_004.jpg').predictions.append(copy.deepcopy(test_prediction_top1))
        survey.get_image('1_000_00_004.jpg').predictions.append(copy.deepcopy(test_prediction_top2))

        survey.get_image('0_000_00_003.jpg').predictions.append(copy.deepcopy(test_prediction_top1))
        survey.get_image('0_000_00_003.jpg').predictions.append(copy.deepcopy(test_prediction_top2))
        survey.get_image('1_000_00_003.jpg').predictions.append(copy.deepcopy(test_prediction_top1))
        survey.get_image('1_000_00_003.jpg').predictions.append(copy.deepcopy(test_prediction_top2))

        survey.get_image('0_000_00_003.jpg').predictions.append(copy.deepcopy(test_prediction_bottom_1))
        survey.get_image('0_000_00_003.jpg').predictions.append(copy.deepcopy(test_prediction_bottom_2))
        survey.get_image('1_000_00_003.jpg').predictions.append(copy.deepcopy(test_prediction_bottom_1))
        survey.get_image('1_000_00_003.jpg').predictions.append(copy.deepcopy(test_prediction_bottom_2))

        for image in survey.images:
            for prediction in image.predictions:
                prediction.image_name = image.file_path

        pre_processing(survey)
        post_processing(survey)

        temporal_predictions = survey.get_predictions_in_temporal_zone()
        #MapGenerator.survey_otter_map(survey).save(survey.otter_map_file_path)

        self.assertEqual(12, len(temporal_predictions))
