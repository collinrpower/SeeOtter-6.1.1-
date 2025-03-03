import json
from unittest import TestCase

from SurveyEntities.object_prediction_data import ObjectPredictionData, ValidationState


def get_test_object_prediction_data_json_v2():
    return """{"image_name": "test_img",
                "score": 1,
                "xmin": 2,
                "xmax": 3,
                "ymin": 4,
                "ymax": 5,
                "category_id": 6,
                "category_name": "test_name"}"""


def get_test_object_prediction_data():
    pred = ObjectPredictionData(image_name="test_img",
                                score=1,
                                xmin=2,
                                xmax=3,
                                ymin=4,
                                ymax=5,
                                category_id=6,
                                category_name="test_name",
                                validated_by="")
    return pred


class TestObjectPredictionData(TestCase):

    def test_is_validated(self):
        pred = ObjectPredictionData()
        self.assertFalse(pred.is_validated)
        pred.validation_state = ValidationState.CORRECT
        self.assertTrue(pred.is_validated)

    def test_to_json_string(self):
        prediction = get_test_object_prediction_data()
        prediction_json = prediction.to_json_string()
        prediction_dict = json.loads(prediction_json)
        for attr in vars(prediction):
            if attr == "original_prediction_data":
                continue
            original_val = prediction.__getattribute__(attr)
            json_val = prediction_dict[attr]
            self.assertEqual(original_val, json_val, msg=f"Values not equal. Attribute: '{attr}'. Correct Val: "
                                                         f"'{original_val}'. Actual Val: {json_val}")
            print(attr, json_val)

    def test_from_json_string(self):
        prediction = get_test_object_prediction_data()
        json_string = get_test_object_prediction_data_json_v2()
        loaded_prediction = ObjectPredictionData.from_json_string(json_string)
        for attr in vars(prediction):
            if attr == "original_prediction_data":
                continue
            original_val = prediction.__getattribute__(attr)
            loaded_val = loaded_prediction.__getattribute__(attr)
            self.assertEqual(original_val, loaded_val)
        print(loaded_prediction.validated_by)
        print(loaded_prediction.validation_confidence)

    def test_has_been_modified(self):
        prediction = get_test_object_prediction_data()
        self.assertFalse(prediction.has_been_modified)
        prediction.update(xmin=100)
        self.assertTrue(prediction.has_been_modified)

    def test_update(self):
        prediction = get_test_object_prediction_data()
        prediction.update(score=420, xmin=10, xmax=11, ymin=12, ymax=13, category_id=14,
                          category_name="new_name")
        self.assertEqual(420, prediction.score)
        self.assertEqual(10, prediction.xmin)
        self.assertEqual(11, prediction.xmax)
        self.assertEqual(12, prediction.ymin)
        self.assertEqual(13, prediction.ymax)
        self.assertEqual(14, prediction.category_id)
        self.assertEqual("new_name", prediction.category_name)
        self.assertEqual(1, prediction.original_prediction_data.score)

    def test_update_prediction_values_raises_exception_on_invalid_fields(self):
        prediction = get_test_object_prediction_data()
        with self.assertRaises(Exception) as context:
            prediction.update(longitude=4.20)
        with self.assertRaises(Exception) as context:
            prediction.update(validated_by="Mark")
        with self.assertRaises(Exception) as context:
            prediction.update(image_name="hello.jpeg")
