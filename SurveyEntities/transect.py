from typing import List
import geopy
import re
from geopy.distance import geodesic
from xml.dom.minidom import parse, Node
from shapely.geometry import Polygon, Point
from Config.see_otter_config import SeeOtterConfig
from Utilities.utilities import *
from config import *
from pykml import parser


class TransectLine:

    def __init__(self, point1, point2):
        self.config = SeeOtterConfig.instance()
        self.point1 = point1
        self.point2 = point2
        self.bearing, self.bearing_rev = self.get_transect_line_bearings()
        self.transect_bounds: Polygon = self.get_transect_line_polygon()

    def get_transect_line_bearings(self):
        return get_bearing(self.point1, self.point2), get_bearing(self.point2, self.point1)

    def get_transect_line_polygon(self, lateral_tolerance=None):
        lateral_tolerance = lateral_tolerance or self.config.TRANSECT_LATERAL_TOLERANCE
        transect_tolerance = geopy.distance.distance(meters=lateral_tolerance)
        poly_1 = transect_tolerance.destination(point=self.point1, bearing=format_compass_bearing(self.bearing - 90))
        poly_2 = transect_tolerance.destination(point=self.point1, bearing=format_compass_bearing(self.bearing + 90))
        poly_3 = transect_tolerance.destination(point=self.point2, bearing=format_compass_bearing(self.bearing + 90))
        poly_4 = transect_tolerance.destination(point=self.point2, bearing=format_compass_bearing(self.bearing - 90))
        return Polygon([Point(poly_1.latitude, poly_1.longitude), Point(poly_2.latitude, poly_2.longitude),
                        Point(poly_3.latitude, poly_3.longitude), Point(poly_4.latitude, poly_4.longitude)])

    def get_transect_line_coordinate_bounds(self):
        transect_bounds = self.transect_bounds.exterior.coords.xy
        transect_bounds = list(zip(transect_bounds[0], transect_bounds[1]))
        return transect_bounds[0:4]

    def is_bearing_within_threshold(self, bearing):
        return bearing_within_target_threshold(bearing, self.bearing, self.config.TRANSECT_BEARING_TOLERANCE) or \
               bearing_within_target_threshold(bearing, self.bearing_rev, self.config.TRANSECT_BEARING_TOLERANCE)


class Transect:

    def __init__(self, transect_id, lines, length=None):
        self.transect_id = transect_id
        self.length = length
        if isinstance(lines, TransectLine):
            self.lines = [TransectLine]
        elif isinstance(lines, List):
            self.lines = lines
        else:
            raise Exception("Transect lines must be type of TransectLine, or List[TransectLine]")

    def __repr__(self):
        return f"Transect {self.transect_id}"

    def is_on_transect(self, coordinates, bearing):
        """
        Returns whether the location and direction are within the bounds to be considered "on transect"
        """
        point = Point(coordinates[0], coordinates[1])
        for line in self.lines:
            if point.within(line.transect_bounds) and line.is_bearing_within_threshold(bearing):
                return True
        return False

    def intersects_polygon(self, coordinates):
        target_polygon = Polygon(coordinates)
        for line in self.lines:
            if line.transect_bounds.intersects(target_polygon):
                return True
        return False

    def is_point_within_transect_bounds(self, coordinates):
        """
        Returns whether the location is within the transect bounds
        :param coordinates:
        :return:
        """
        point = Point(coordinates[0], coordinates[1])
        for line in self.lines:
            if point.within(line.transect_bounds):
                return True
        return False

    @staticmethod
    def parse_coordinates(placemark):
        coord_elements = placemark.getElementsByTagName("coordinates")
        coordinates = coord_elements[0].firstChild.nodeValue
        coordinates = coordinates.split(' ')[0:2]
        coords1 = coordinates[0].split(',')
        coords2 = coordinates[1].split(',')
        lat1 = float(coords1[1])
        lon1 = float(coords1[0])
        lat2 = float(coords2[1])
        lon2 = float(coords2[0])
        return (lat1, lon1), (lat2, lon2)

    @staticmethod
    def parse_transect_id(placemark_element):
        transect_id = -1
        simple_data = placemark_element.getElementsByTagName("SimpleData")
        for data in simple_data:
            if data.getAttribute("name") == "TRANSECT":
                transect_id = int(data.firstChild.nodeValue)
        if transect_id == -1:
            raise Exception("Invalid transect id")
        return transect_id

    @staticmethod
    def load_transects_from_kml(path):
        try:
            return Transect.load_transects_with_pykml(path)
        except Exception as ex:
            print(f"Error loading transects with pykml. Error: {ex}. Attempting manual parsing of kml file.")
        try:
            return Transect.load_transects_manual_parsing(path)
        except Exception as ex:
            print(f"Error loading transects from kml file. Error Message: {ex}. Attempting load linnea kml.")
        try:
            return Transect.load_linnea_kml(path)
        except Exception as ex:
            print(f"Error loading linnea kml: {ex}")

    @staticmethod
    def load_transects_manual_parsing(path):
        tree = parse(path)
        placemarks = tree.getElementsByTagName("Placemark")
        transects = []
        for placemark in placemarks:
            coordinates = Transect.parse_coordinates(placemark)
            transect_id = Transect.parse_transect_id(placemark)
            transects.append(Transect(transect_id, TransectLine(coordinates[0], coordinates[1])))
        return transects

    @staticmethod
    def load_transects_with_pykml(path):
        transects = []
        with open(path) as file:
            doc = parser.parse(file)
            root = doc.getroot()
            placemarks = root.findall('.//{http://www.opengis.net/kml/2.2}Placemark')
            for p in placemarks:
                info = p.ExtendedData.SchemaData.findall('.//{http://www.opengis.net/kml/2.2}SimpleData')
                info = {field.attrib["name"]: field.pyval for field in info}
                try:
                    transect_id = int(info["trans_id"])
                except Exception as ex:
                    raise Exception(f"Error parsing kml file. Could not find required field matching 'trans_id'. "
                                    f"Message: {ex}")
                length_km = float(info["length_km"])
                line_coords_re = "\s+(-*\d{2,}.\d{2,}),(-*\d{2,}.\d{2,}),0\s+(-*\d{2,}.\d{2,}),(-*\d{2,}.\d{2,}),0\s+"
                line_strings = p.findall('.//{http://www.opengis.net/kml/2.2}LineString')
                if len(line_strings) == 0:
                    print(f"Warning, could not find any lines for transect: {transect_id}")
                    continue
                transect_lines = []
                for line in line_strings:
                    matches = re.findall(line_coords_re, str(line.coordinates))
                    points = []
                    for match in matches:
                        points.append([(float(match[1])), float(match[0])])
                        points.append([(float(match[3])), float(match[2])])
                    for idx in range(0, len(points) - 1):
                        transect_lines.append(TransectLine(points[idx], points[idx+1]))
                transects.append(Transect(transect_id=transect_id, lines=transect_lines, length=length_km))

        return transects

    @staticmethod
    def load_linnea_kml(path):
        """
        This is terrible, I'm sorry
        """

        def parse_coordinates(coordinate_str):
            coord_re = r"\s+(-\d{3}\.\d+,\d{2}\.\d+,0)"
            matches = re.findall(coord_re, coordinate_str)
            if matches:
                coords = [match.split(",") for match in matches]
                return coords

        mode = 0
        coords = ""
        transects = []

        with open(path) as file:
            for line in file.readlines():
                if line.__contains__(r"<td>trans_id</td>") and mode == 0:
                    mode = 1
                    continue
                if mode == 1:
                    if line.__contains__(r"<td>"):
                        trans_id = line.replace(r"<td>", "").replace(r"</td>", "")
                        mode = 2
                if line.__contains__(r"<coordinates>") and mode == 2:
                    mode = 3
                    continue
                if mode == 3:
                    if line.__contains__(r"</coordinates>"):
                        mode = 4
                    else:
                        coords += line
                if mode == 4:
                    coords = parse_coordinates(coords)
                    lines = []
                    if coords is not None:
                        for idx, point in enumerate(coords):
                            if idx == len(coords) - 1:
                                break
                            point1 = float(coords[idx][1]), float(coords[idx][0])
                            point2 = float(coords[idx+1][1]), float(coords[idx+1][0])
                            lines.append(TransectLine(point1, point2))

                        transect = Transect(int(trans_id), lines=lines)
                        transects.append(transect)
                    mode = 0
                    coords = ""

        return transects


class TransectRangeAssignment:

    def __init__(self, start_img, end_img, transect_id, *args):
        self.start_img = start_img
        self.end_img = end_img
        self.transect_id = None if transect_id == '' else int(transect_id)


class ManualTransectAssignment:

    @staticmethod
    def load(path):
        try:
            if exists(path):
                with open(path, 'r') as csv_file:
                    csv_reader = csv.reader(csv_file, delimiter=',')
                    next(csv_reader)
                    transect_ranges = [TransectRangeAssignment(*row) for row in csv_reader if row != []]
                return transect_ranges
            else:
                print(f"No transect assignment file found. Creating new file at ({path})...")
                ManualTransectAssignment.create_new(path)
        except Exception as ex:
            raise Exception(f"Could not load manual transect assignment file '{path}'. Error: {ex}")

    @staticmethod
    def create_new(path):
        if pathlib.Path(path).suffix == '.csv':
            with open(path, 'w') as csv_file:
                csv_writer = csv.writer(csv_file)
                csv_writer.writerow(["start_img", "end_img", "transect_id"])
            return []
        else:
            raise Exception(f"Invalid file name ({path}). Transect assignment file must be a csv.")
