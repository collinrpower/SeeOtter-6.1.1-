import simplekml
from simplekml import Style

from DataGenerators.map_generator import MapGenerator
from Processing.survey_image_processing import get_coordinate_bounds
from SurveyEntities.survey import Survey

# Color Format: aabbggrr
kml_map_colors = ['550000ff', '55ff0000', '550099ff', '559900ff']

transect_poly_style = Style()
transect_poly_style.polystyle.color = '66ffffff'
transect_poly_style.linestyle.color = '6600ffff'

on_transect_point_style = Style()
on_transect_point_style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/pushpin/grn-pushpin.png'
on_transect_point_style.iconstyle.scale = .5

off_transect_point_style = Style()
off_transect_point_style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/pushpin/red-pushpin.png'
off_transect_point_style.iconstyle.scale = .5


def get_camera_color_mapping(survey):
    if survey.camera_system is not None:
        cameras = survey.camera_system.cameras
        return {camera: kml_map_colors[idx] for idx, camera in enumerate(cameras)}


def get_camera_style_mapping(survey):
    if survey.camera_system is not None:
        cameras = survey.camera_system.cameras
        camera_style_mapping = {}
        for idx, camera in enumerate(cameras):
            style = Style()
            style.polystyle.color = kml_map_colors[idx]
            camera_style_mapping.update({camera: style})
        return camera_style_mapping


class KmlMapGenerator:

    @classmethod
    def survey_transect_map(cls, survey: Survey, performance_mode=True):
        print("Generating Kml Map...")
        kml_map = simplekml.Kml()
        images = [image for image in survey.images if image.coordinates_valid
                  and (image.camera == survey.camera_system.cameras[0] or performance_mode is False)]

        transect_folder = kml_map.newfolder(name="Transect_Bounds")
        cls.add_transect_bounds_to_map(survey, transect_folder)
        img_marker_folder = kml_map.newfolder(name="Image_Markers")
        cls.add_image_transect_markers_to_map(images=images, kml_map=img_marker_folder)

        if not performance_mode:
            img_projection_folder = kml_map.newfolder(name="Image_Projection")
            cls.add_image_projection_to_map(survey=survey, images=images, kml_map=img_projection_folder)

        return kml_map

    @staticmethod
    def add_image_transect_markers_to_map(images, kml_map):

        for image in images:

            point_coords = (image.longitude, image.latitude)
            new_point = kml_map.newpoint(coords=[point_coords])
            new_point.description = f"{image.file_name}\n" \
                                    f"Location: {image.coordinates}\n" \
                                    f"Altitude: {image.altitude}\n" \
                                    f"Heading:  {int(image.direction)}\n" \
                                    f"Transect: {image.transect_id}\n" \
                                    f"Datetime: {image.datetime_obj}"

            new_point.style = on_transect_point_style if image.transect_id else off_transect_point_style

    @staticmethod
    def add_image_projection_to_map(survey, images, kml_map):
        camera_style_mapping = get_camera_style_mapping(survey)
        for image in images:
            image_bounds = [(coord[1], coord[0]) for coord in get_coordinate_bounds(image)]
            boundary = [*image_bounds, image_bounds[0]]
            image_bounds_poly = kml_map.newpolygon(name=image.file_name, outerboundaryis=boundary)
            image_bounds_poly.style = camera_style_mapping[image.camera]

    @staticmethod
    def add_transect_bounds_to_map(survey: Survey, kml_map):
        for transect in survey.transects:
            for transect_line in transect.lines:
                coords = [(coord[1], coord[0]) for coord in transect_line.get_transect_line_coordinate_bounds()]
                bounds = [*coords, coords[0]]
                transect_poly = kml_map.newpolygon(name=f"Transect {transect.transect_id}", outerboundaryis=bounds)
                transect_poly.style = transect_poly_style
