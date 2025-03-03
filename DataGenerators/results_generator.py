import csv
from Processing.survey_processing import *
from version import version


class ResultsGenerator:
    """
    Generates csv data output for a survey
    """

    def __init__(self, survey: Survey, min_confidence=RESULTS_CONFIDENCE_CUTOFF):
        self.survey: Survey = survey
        self.min_confidence = min_confidence
        self.headers = []
        self.rows = []

    @staticmethod
    def image_bounds_headers():
        return ['ImageCorner1Lat', 'ImageCorner1Lon', 'ImageCorner2Lat', 'ImageCorner2Lon',
                'ImageCorner3Lat', 'ImageCorner3Lon', 'ImageCorner4Lat', 'ImageCorner4Lon']

    @staticmethod
    def image_info_headers():
        return ['ImageID', 'Datetime', 'FilePath', 'CameraLatitude', 'CameraLongitude', 'CameraAltitude', 'TransectID']

    @staticmethod
    def prediction_data_headers():
        return ['PredictionCategoryName', 'PredictionCategoryID', 'Confidence', 'PredictedLatitude',
                'PredictedLongitude', 'BoxMinX', 'BoxMaxX', 'BoxMinY', 'BoxMaxY', 'IsInTemporalZone',
                'IsNearTemporalZone', 'IsInTransectOverlap', 'InTemporalZoneImageName', 'NearTemporalZoneImageName',
                'TransectOverlapImageName1', 'TransectOverlapImageName2', "ValidationState", "ValidatedBy"]

    @staticmethod
    def inclinometer_data_headers():
        return ['angle_x', 'angle_y', 'angle_z']

    @staticmethod
    def image_bounds_fields(image: SurveyImage):
        image_bounds = get_coordinate_bounds(image)
        return [image_bounds[0][0], image_bounds[0][1], image_bounds[1][0], image_bounds[1][1], image_bounds[2][0],
                image_bounds[2][1], image_bounds[3][0], image_bounds[3][1]]

    @staticmethod
    def image_info_fields(image: SurveyImage):
        return [image.id, image.datetime, image.file_path, image.latitude, image.longitude, image.altitude,
                image.transect_id]

    @staticmethod
    def prediction_data_fields(prediction: ObjectPredictionData = None):
        if prediction:
            num_transect_overlap = len(prediction.transect_overlap_images)
            transect_overlap1 = prediction.transect_overlap_images[0] if num_transect_overlap > 0 else NA
            transect_overlap2 = prediction.transect_overlap_images[1] if num_transect_overlap > 1 else NA

            return [prediction.category_name, prediction.category_id, prediction.score, prediction.latitude,
                    prediction.longitude, prediction.xmin, prediction.xmax, prediction.ymin, prediction.ymax,
                    prediction.is_in_temporal_overlap, prediction.is_near_temporal_overlap,
                    prediction.is_in_transect_overlap, prediction.overlaps_image,
                    prediction.almost_overlaps_image, transect_overlap1, transect_overlap2,
                    ValidationState(prediction.validation_state).name, prediction.validated_by]
        else:
            return [NA for field in range(len(ResultsGenerator.prediction_data_headers()))]

    @staticmethod
    def inclinometer_data_fields(image: SurveyImage):
        inclinometer_data = image.inclinometer_data
        if inclinometer_data:
            return [inclinometer_data.angle_x, inclinometer_data.angle_y, inclinometer_data.angle_z]
        else:
            return [NA for field in range(len(ResultsGenerator.inclinometer_data_headers()))]

    def save(self, file_name):
        results_dir = self.survey.get_relative_path(RESULTS_DIR)
        path = os.path.join(results_dir, file_name)
        if self.survey.has_no_images:
            print("No images in project. Skipping csv results generation.")
        elif self.headers is None or self.rows is None:
            print("No results to save.")
        with open(path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(self.headers)
            writer.writerows(self.rows)
            print(f"Saved results to {path}")

    def all_otters(self):
        self.headers += ResultsGenerator.image_info_headers()
        self.headers += ResultsGenerator.prediction_data_headers()
        self.headers += ResultsGenerator.image_bounds_headers()

        for image in self.survey.images:
            if len(image.predictions) == 0:
                row = []
                if len(image.predictions) == 0:
                    row += ResultsGenerator.image_info_fields(image)
                    row += ResultsGenerator.prediction_data_fields(None)
                    row += ResultsGenerator.image_bounds_fields(image)
                    self.rows.append(row)
            else:
                predictions = filter_predictions(image.predictions, confidence_cutoff=self.min_confidence)
                for prediction in predictions:
                    row = []
                    row += ResultsGenerator.image_info_fields(image)
                    row += ResultsGenerator.prediction_data_fields(prediction)
                    row += ResultsGenerator.image_bounds_fields(image)
                    self.rows.append(row)

        return self

    def distinct_otters(self):
        self.headers += ResultsGenerator.image_info_headers()
        self.headers += ResultsGenerator.prediction_data_headers()
        self.headers += ResultsGenerator.image_bounds_headers()
        distinct_otters = get_distinct_predictions(self.survey)
        distinct_otters = filter_predictions(distinct_otters, confidence_cutoff=self.min_confidence)

        for image in self.survey.images:
            if len(image.predictions) == 0:
                row = []
                if len(image.predictions) == 0:
                    row += ResultsGenerator.image_info_fields(image)
                    row += ResultsGenerator.prediction_data_fields(None)
                    row += ResultsGenerator.image_bounds_fields(image)
                    self.rows.append(row)
            else:
                predictions = [prediction for prediction in image.predictions if prediction in distinct_otters]
                for prediction in predictions:
                    row = []
                    row += ResultsGenerator.image_info_fields(image)
                    row += ResultsGenerator.prediction_data_fields(prediction)
                    row += ResultsGenerator.image_bounds_fields(image)
                    self.rows.append(row)

        return self

    def all_predictions(self):
        self.headers += ResultsGenerator.image_info_headers()
        self.headers += ResultsGenerator.prediction_data_headers()
        self.headers += ResultsGenerator.image_bounds_headers()

        for image in self.survey.images:
            row = []
            if len(image.predictions) == 0:
                row += ResultsGenerator.image_info_fields(image)
                row += ResultsGenerator.prediction_data_fields(None)
                row += ResultsGenerator.image_bounds_fields(image)
                self.rows.append(row)
            else:
                for prediction in image.predictions:
                    row = []
                    row += ResultsGenerator.image_info_fields(image)
                    row += ResultsGenerator.prediction_data_fields(prediction)
                    row += ResultsGenerator.image_bounds_fields(image)
                    self.rows.append(row)

        return self

    def inclinometer_data(self):
        self.headers += ResultsGenerator.image_info_headers()
        self.headers += ResultsGenerator.inclinometer_data_headers()

        for image in self.survey.images:
            row = []
            row += ResultsGenerator.image_info_fields(image)
            row += ResultsGenerator.inclinometer_data_fields(image)
            self.rows.append(row)

        return self

    def distinct_otter_count_by_image(self):
        self.headers += ResultsGenerator.image_info_headers()
        self.headers.append("OtterCount")
        self.headers += ResultsGenerator.image_bounds_headers()

        distinct_otters = get_distinct_predictions(self.survey)
        distinct_otters = filter_predictions(distinct_otters, confidence_cutoff=self.min_confidence)

        for image in self.survey.images:
            row = []
            predictions = [prediction for prediction in image.predictions if distinct_otters.__contains__(prediction)]
            row += ResultsGenerator.image_info_fields(image)
            row.append(len(predictions))
            row += ResultsGenerator.image_bounds_fields(image)
            self.rows.append(row)

        return self

    def validated_predictions(self):
        self.headers += ResultsGenerator.image_info_headers()
        self.headers += ResultsGenerator.prediction_data_headers()
        self.headers += ResultsGenerator.image_bounds_headers()

        for image in self.survey.images:
            validated_predictions = [prediction for prediction in image.predictions if prediction.is_validated]
            for prediction in validated_predictions:
                row = []
                row += ResultsGenerator.image_info_fields(image)
                row += ResultsGenerator.prediction_data_fields(prediction)
                row += ResultsGenerator.image_bounds_fields(image)
                self.rows.append(row)
        return self

    def survey_overview(self):
        predicted_otters = filter_predictions(self.survey.predictions, confidence_cutoff=self.min_confidence)
        distinct_otters = get_distinct_predictions(self.survey)
        distinct_otters = filter_predictions(distinct_otters, confidence_cutoff=self.min_confidence)

        self.headers += ["Survey Name", self.survey.survey_name]
        self.rows.append(["SeeOtter Version", version])
        self.rows.append(["Images", str(self.survey.num_images)])
        self.rows.append(["Processed Images", str(len(self.survey.processed_images))])
        self.rows.append(["All Predictions", str(len(self.survey.predictions))])
        self.rows.append(["Otters Identified", str(len(predicted_otters))])
        self.rows.append(["Distinct Otter Count", str(len(distinct_otters))])

        return self
