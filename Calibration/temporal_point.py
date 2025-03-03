from typing import Tuple, List
from geopy.distance import geodesic

from Calibration.calibration_point import CalibrationPoint
from Processing.survey_image_processing import get_coordinates_at_pixel
from Utilities.json_convert import JsonConvert
from SurveyEntities.survey import Survey


@JsonConvert.register
class TemporalPoint:
    """
    Two points representing the same geographic point on different images
    used to calibrate a camera system's orientation.
    """
    def __init__(self, image1=None, point1: Tuple[int, int] = None, image2=None, point2: Tuple[int, int] = None):
        self.image1 = image1
        self.point1 = point1
        self.image2 = image2
        self.point2 = point2

    def __str__(self):
        return f"Temporal Calibration Point: img1='{self.image1}', point1={self.point1}, img2='{self.image2}', " \
               f"point2={self.point2}"


@JsonConvert.register
class TemporalPoints:
    def __init__(self, points: List[TemporalPoint] = None):
        self.points = points


class TemporalCalibrationPoint(CalibrationPoint):
    """
    Associates a Temporal point to survey image objects for use in calibration.
    """

    def __init__(self, survey: Survey, point: TemporalPoint):
        self.image1 = survey.get_image(point.image1)
        self.image2 = survey.get_image(point.image2)
        self.point1 = point.point1
        self.point2 = point.point2
        self.error = -1

        if self.image1 is None or self.image2 is None:
            raise Exception(f"Error finding images ({point.image1, point.image2}) in survey ({survey.survey_name})")

    def get_error(self, ignore_inclinometer=True):
        coords1 = get_coordinates_at_pixel(self.image1, self.point1[0], self.point1[1],
                                           ignore_inclinometer=ignore_inclinometer)
        coords2 = get_coordinates_at_pixel(self.image2, self.point2[0], self.point2[1],
                                           ignore_inclinometer=ignore_inclinometer)
        error = geodesic(coords1, coords2).m
        self.error = error
        return error
