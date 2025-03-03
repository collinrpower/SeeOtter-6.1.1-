import folium
from typing import Optional
from Calibration.temporal_calibration import TemporalCalibration
from Processing.survey_processing import *


def get_color_camera_mapping(survey):
    if survey.camera_system is not None:
        cameras = survey.camera_system.cameras
        return {camera: MAP_COLORS[idx] for idx, camera in enumerate(cameras)}


class MapGenerator:
    """
    Generates folium maps for a survey
    """
    @classmethod
    @property
    def config(cls) -> SeeOtterConfig:
        return SeeOtterConfig.instance()

    @classmethod
    def survey_map(cls, survey: Survey, performance_mode=False) -> Optional[folium.Map]:
        if survey.has_no_images:
            print("No images in project. Skipping map generation.")
            return
        MapGenerator.print_generating_map()
        map_location = cls.get_map_coordinates(survey)
        survey_map = folium.Map(location=map_location, zoom_start=15)
        color_camera_mapping = get_color_camera_mapping(survey)
        for image in survey.images:
            color = color_camera_mapping[image.camera]
            if not performance_mode:
                MapGenerator.get_image_projection_polygon(image=image, color=color).add_to(survey_map)
            if not performance_mode or image.camera == survey.camera_system.cameras[0]:
                MapGenerator.get_camera_marker(image=image, color=color).add_to(survey_map)

        min_coords, max_coords = survey.get_min_max_coordinate_bounds()
        min_lat = min_coords[0]
        min_lon = min_coords[1]
        even = True
        for row in range(10):
            lat = min_lat + row * cls.config.IMAGE_COORDINATE_CHUNKING_DEGREES_LAT
            for col in range(10):
                lon = min_lon + col * cls.config.IMAGE_COORDINATE_CHUNKING_DEGREES_LON
                color = 'blue' if even else 'red'
                even = not even
                folium.Polygon(((lat, lon),
                                (lat, lon + cls.config.IMAGE_COORDINATE_CHUNKING_DEGREES_LON),
                                (lat + cls.config.IMAGE_COORDINATE_CHUNKING_DEGREES_LAT,
                                 lon + cls.config.IMAGE_COORDINATE_CHUNKING_DEGREES_LON),
                                (lat + cls.config.IMAGE_COORDINATE_CHUNKING_DEGREES_LAT, lon)),
                               color=color,
                               fill_opacity=.1).add_to(survey_map)

        return survey_map

    @classmethod
    def survey_otter_map(cls, survey: Survey, performance_mode=False) -> Optional[folium.Map]:
        if survey.has_no_images:
            print("No images in project. Skipping map generation.")
            return None
        MapGenerator.print_generating_map()
        map_location = cls.get_map_coordinates(survey)
        survey_map = folium.Map(location=map_location, zoom_start=15)
        for image in survey.images:
            predictions = filter_predictions(image.predictions)
            if performance_mode and len(predictions) == 0:
                continue
            otter_count = len(predictions)
            color = cls.otter_count_to_color(otter_count=otter_count)
            cls.get_image_projection_polygon(image=image, color=color).add_to(survey_map)
            for prediction in predictions:
                # marker_color = cls.prediction_overlap_type_to_color(prediction)
                marker = cls.get_otter_marker(image, prediction, color)
                marker.add_to(survey_map)

        return survey_map

    @classmethod
    def survey_transect_map(cls, survey: Survey, performance_mode=False) -> Optional[folium.Map]:
        if survey.has_no_images:
            print("No images in project. Skipping map generation.")
            return None
        MapGenerator.print_generating_map()
        map_location = cls.get_map_coordinates(survey)
        survey_map = folium.Map(location=map_location, zoom_start=11)
        for image in survey.images:
            is_on_transect = image.transect_id is not None
            marker_color = "green" if is_on_transect else "red"
            MapGenerator.get_camera_marker(image, color=marker_color).add_to(survey_map)
        for transect_bounds in MapGenerator.get_transect_bounds_projection(survey):
            transect_bounds.add_to(survey_map)
        return survey_map

    @classmethod
    def temporal_calibration_map(cls, calibration: TemporalCalibration) -> Optional[folium.Map]:
        calibration.calculate_error()
        calibration_map = folium.Map(location=calibration.calibration_points[0].image1.coordinates, zoom_start=12)
        for i, image in enumerate(calibration.images):
            color = MAP_COLORS[i % len(MAP_COLORS)]
            cls.get_image_projection_polygon(image=image, color=color).add_to(calibration_map)
            cls.get_camera_marker(image=image, color="black").add_to(calibration_map)
            point_error = []
            for point_data in calibration.calibration_points:
                if point_data.image1 == image:
                    point_error.append((point_data.point1, point_data.error))
                if point_data.image2 == image:
                    point_error.append((point_data.point2, point_data.error))
            for point, error in point_error:
                coordinates = get_coordinates_at_pixel(image, point[0], point[1])

                folium.Marker(coordinates,
                              popup=f"{image.file_name}\r\n"
                                    f"{coordinates}\r\n"
                                    f"Pixel: {point}\r\n"
                                    f"Heading: {image.direction:.2f}\r\n"
                                    f"Error: {int(error)}m",
                              icon=folium.Icon(color=color)).add_to(calibration_map)

        return calibration_map

    @staticmethod
    def print_generating_map():
        print(f"Generating Map...")

    @staticmethod
    def get_map_coordinates(survey: Survey):
        for image in survey.images:
            if image.coordinates_valid:
                return image.coordinates

    @staticmethod
    def otter_count_to_color(otter_count):
        color = 'white'
        if otter_count >= 9:
            color = 'darkred'
        elif otter_count >= 7:
            color = 'red'
        elif otter_count >= 5:
            color = 'orange'
        elif otter_count >= 3:
            color = 'green'
        elif otter_count >= 1:
            color = 'blue'
        return color

    @staticmethod
    def prediction_overlap_type_to_color(prediction: ObjectPredictionData):
        marker_color = 'red'
        if prediction.is_in_transect_overlap:
            marker_color = 'blue'
        elif prediction.is_in_temporal_overlap:
            marker_color = 'green'
        elif prediction.is_near_temporal_overlap:
            marker_color = 'orange'
        return marker_color

    @staticmethod
    def get_image_projection_polygon(image: SurveyImage, color='blue'):
        return folium.Polygon(get_coordinate_bounds(image),
                              color=color,
                              fill=True,
                              fill_color=color,
                              fill_opacity=MAP_IMAGE_PROJECTION_OPACITY)

    @staticmethod
    def get_camera_marker(image: SurveyImage, color='blue'):
        return folium.Marker(image.coordinates,
                             popup=f"Camera Location\r\n"
                                   f"{image.file_name}\r\n"
                                   f"{image.latitude}, "
                                   f"{image.longitude}\r\n"
                                   f"Altitude: {image.altitude}\r\n"
                                   f"Heading: {int(image.direction)}\r\n"
                                   f"Transect: {image.transect_id}",
                             icon=folium.Icon(color=color))

    @staticmethod
    def get_otter_marker(image, prediction, color):
        return folium.Marker(location=(prediction.latitude, prediction.longitude),
                             icon=folium.Icon(color=color),
                             popup=f"{image.file_name}\r\n"
                                   f"Overlaps: {prediction.overlaps_image}\r\n"
                                   f"Almost Overlaps: {prediction.almost_overlaps_image}\r\n"
                                   f"Transect Overlaps: {prediction.transect_overlap_images}\r\n"
                                   f"Confidence: {prediction.score}\r\n"
                                   f"Image Location: ({prediction.x}, {prediction.y})")

    @staticmethod
    def get_transect_bounds_projection(survey: Survey):
        transect_bounds = []
        for transect in survey.transects:
            for transect_line in transect.lines:
                coords = transect_line.get_transect_line_coordinate_bounds()
                transect_bounds.append(folium.Polygon(coords,
                                                      popup=f"Transect {transect.transect_id}",
                                                      fill=True,
                                                      fill_color="green",
                                                      fill_opacity=MAP_IMAGE_PROJECTION_OPACITY))
        return transect_bounds

    @staticmethod
    def get_transect_lines(survey: Survey):
        return [folium.PolyLine([transect.point1, transect.point2], color="red") for transect in survey.transects]
