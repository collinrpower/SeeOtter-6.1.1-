import math
import geopy
from geopy import Point
from geopy.distance import geodesic
from SurveyEntities.object_prediction_data import ObjectPredictionData
from SurveyEntities.survey_image import SurveyImage
from Utilities.custom_exceptions import NoCameraSystemException
from Utilities.spatial_utilities import get_image_rotation_offset, get_vector_ground_collision_point
from Utilities.utilities import cartesian_to_compass_bearing, get_bearing, get_rounded_list


"""
Methods for survey image processing and geo-referencing algorithms
"""


def get_coordinates_at_pixel(image: SurveyImage, x, y, ignore_calibration=False, ignore_inclinometer=False):
    """
    Calculates the coordinates of a location within an image given by pixel coordinates.
    :param image: SurveyImage
    :param x: Pixel x-coordinate
    :param y: Pixel y-coordinate
    :param ignore_inclinometer: Inclinometer data/calibration are ignored
    :param ignore_calibration: All calibrations are ignored, uses default camera orientation
    :return: GPS coordinates of location at pixel
    """
    if image.camera is None:
        raise NoCameraSystemException("Image has no camera assigned. Unable to georeference location.")

    total_rotation = get_total_rotation_for_pixel(image, x, y, ignore_calibration, ignore_inclinometer)
    target_location_offset = get_vector_ground_collision_point(altitude=image.altitude, rotation=total_rotation)
    target_offset_x, target_offset_y = target_location_offset[0], target_location_offset[1]
    meters_from_gps_center = math.sqrt(target_offset_x ** 2 + target_offset_y ** 2)
    angle_from_gps_center = math.degrees(math.atan2(target_offset_y, target_offset_x))
    bearing_from_gps_center = cartesian_to_compass_bearing(angle_from_gps_center)

    photo_coordinates = Point(image.latitude, image.longitude)
    distance = geopy.distance.distance(meters=meters_from_gps_center)
    calculated_coordinates = distance.destination(point=photo_coordinates, bearing=bearing_from_gps_center)

    return calculated_coordinates.latitude, calculated_coordinates.longitude


def get_total_rotation_for_pixel(image: SurveyImage, x, y, ignore_calibration=False, ignore_inclinometer=False):
    """
    Calculates the total rotation required to rotate a vertical vector (ie: camera pointed
    straight down), to point towards a pixel in an image. This factors in the pixel location
    in the image, camera orientation, inclinometer data, and camera calibration.

    :param image: Survey Image
    :param x: Pixel x-coordinate
    :param y: Pixel y-coordinate
    :param ignore_inclinometer: Inclinometer data/calibration are ignored
    :param ignore_calibration: All calibrations are ignored, uses default camera orientation
    :return: Rotation required to "point camera" at pixel
    """
    camera_orientation = image.get_camera_orientation(ignore_calibration=ignore_calibration,
                                                      ignore_inclinometer=ignore_inclinometer)
    image_rotation = get_image_rotation_offset(resolution=image.resolution,
                                               hfov=camera_orientation.hfov,
                                               pixel_coords=(x, y))
    plane_rotation = [0, 0, image.direction]
    return [img + cam + pln for img, cam, pln in zip(image_rotation, camera_orientation.get_rotation(), plane_rotation)]


def calculate_predicted_object_coordinates(image: SurveyImage):
    for prediction in image.predictions:
        prediction.latitude, prediction.longitude = \
            get_coordinates_at_pixel(image, prediction.x, prediction.y)


def get_bearing_between_images(image1: SurveyImage, image2: SurveyImage):
    return get_bearing(image1.coordinates, image2.coordinates)


def get_distance_between_images(image1: SurveyImage, image2: SurveyImage):
    return geodesic(image1.coordinates, image2.coordinates).m


def get_prediction_dimensions(image, prediction: ObjectPredictionData):
    top_left = get_coordinates_at_pixel(image, prediction.xmin, prediction.ymin)
    top_right = get_coordinates_at_pixel(image, prediction.xmax, prediction.ymin)
    bottom_right = get_coordinates_at_pixel(image, prediction.xmax, prediction.ymax)
    width = get_distance_between_coordinates(top_left, top_right)
    height = get_distance_between_coordinates(top_right, bottom_right)
    return width, height


def get_distance_between_coordinates(coord1, coord2):
    return geodesic(coord1, coord2).m


def images_from_same_camera(img1: SurveyImage, img2: SurveyImage):
    return img1.camera.name == img2.camera.name


def get_coordinate_bounds(image):
    return (get_coordinates_at_pixel(image, 0, 0),
            get_coordinates_at_pixel(image, image.resolution_x, 0),
            get_coordinates_at_pixel(image, image.resolution_x, image.resolution_y),
            get_coordinates_at_pixel(image, 0, image.resolution_y))


def get_scaled_coordinate_bounds(image, scale):
    original_altitude = image.altitude
    image.altitude *= scale
    image_bounds = get_coordinate_bounds(image)
    image.altitude = original_altitude
    return image_bounds


def calculate_bearing_from_neighbor_images(image, previous, next):
    if next is None:
        return get_bearing_between_images(previous, image)
    elif previous is None:
        return get_bearing_between_images(image, next)
    else:
        distance_to_previous = get_distance_between_images(image, previous)
        distance_to_next = get_distance_between_images(image, next)
        previous_is_valid = SurveyImage.is_valid_distance_to_neighbor_image(distance_to_previous) \
                            and images_from_same_camera(image, previous)
        next_is_valid = SurveyImage.is_valid_distance_to_neighbor_image(distance_to_next) \
                        and images_from_same_camera(image, next)
        if previous_is_valid and next_is_valid:
            return (get_bearing_between_images(previous, image) + get_bearing_between_images(image, next)) / 2
        elif previous_is_valid:
            return get_bearing_between_images(previous, image)
        elif next_is_valid:
            return get_bearing_between_images(image, next)
        else:
            print(f"Warning. No images within a valid distance for distance calculation of {image}.\r\n"
                  f" - Previous: {distance_to_previous}m, ({previous})\r\n"
                  f" - Next: {distance_to_next}m, ({next})\r\n")
            if distance_to_next < distance_to_previous:
                return get_bearing_between_images(image, next)
            else:
                return get_bearing_between_images(previous, image)
