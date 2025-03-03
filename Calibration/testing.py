from folium import folium
from SurveyEntities.survey import *
from SurveyEntities.survey_image import *
from geopy.distance import geodesic


class CoordPrediction:
    already_projected_images = []

    def __init__(self, img: SurveyImage, x, y, lat, long, description):
        self.img = img
        self.x = x
        self.y = y
        self.lat = lat
        self.long = long
        self.predicted_lat = 0
        self.predicted_long = 0
        self.error = -1
        self.description = description

    def process(self):
        self.calculate_coordinates()
        self.calculate_error()

    def calculate_coordinates(self):
        self.predicted_lat, self.predicted_long = self.img.get_coordinates_at_pixel(self.x, self.y)

    def calculate_error(self):
        c1 = (self.lat, self.long)
        c2 = (self.predicted_lat, self.predicted_long)
        self.error = geodesic(c1, c2).m

    def add_map_nodes(self, map: folium.map):
        folium.Marker([self.lat, self.long],
                      popup=f"{self.description} \r\n"
                            f"{self.img.file_name}\r\n"
                            f"{self.lat}, {self.long}",
                      icon=folium.Icon(color='green')).add_to(map)
        folium.Marker([self.predicted_lat, self.predicted_long],
                      popup=f"{self.description} \r\n"
                            f"{self.img.file_name}\r\n"
                            f"{self.predicted_lat}, {self.predicted_long}\r\n"
                            f"Error: {int(self.error)}m",
                      icon=folium.Icon(color='red')).add_to(map)
        folium.Marker([self.img.latitude, self.img.longitude],
                      popup=f"Camera Location \r\n"
                            f"{self.img.file_name}\r\n"
                            f"{self.img.latitude}, {self.img.longitude}",
                      icon=folium.Icon(color='blue')).add_to(map)

    def add_map_image_projection(self, map: folium.map):
        w, h = 8688, 5792
        if CoordPrediction.already_projected_images.__contains__(self.img.file_name):
            return
        else:
            CoordPrediction.already_projected_images.append(self.img.file_name)
            top_left = self.img.get_coordinates_at_pixel(0, 0)
            top_right = self.img.get_coordinates_at_pixel(w, 0)
            bottom_left = self.img.get_coordinates_at_pixel(0, h)
            bottom_right = self.img.get_coordinates_at_pixel(w, h)
            projection = folium.Polygon([top_left, top_right, bottom_right, bottom_left],
                                        color='blue',
                                        fill=True,
                                        fill_color='orange',
                                        fill_opacity=.1)
            projection.add_to(map)


def make_map():
    survey, nodes = get_test_nodes()
    map = folium.Map(location=[nodes[0].lat, nodes[0].long], zoom_start=17)
    for node in nodes:
        node.process()
        node.add_map_nodes(map)
        node.add_map_image_projection(map)
    map.save('CoordTestMap.html')


def get_test_nodes():
    survey = Survey("LocationTesting")
    survey.calculate_bearing()

    print(f"Coords: {survey.images[7].latitude}, {survey.images[7].longitude}")

    nodes = [CoordPrediction(survey.images[0], 2200, 1380, 59.48054382645299, -151.64851537394878, 'Little Shack'),
             CoordPrediction(survey.images[0], 2150, 300, 59.4803198273309, -151.64899910229394, 'Green House'),
             CoordPrediction(survey.images[0], 2220, 1375, 59.4805488998053, -151.64851407613193, 'Little House 2'),
             CoordPrediction(survey.images[0], 2185, 940, 59.48045093853801, -151.6487049678374, 'Little House 1'),
             CoordPrediction(survey.images[1], 6700, 5750, 59.482352804320044, -151.65147676559374, 'Silver House'),
             CoordPrediction(survey.images[1], 980, 5500, 59.4803198273309, -151.64899910229394, 'Green House'),
             CoordPrediction(survey.images[12], 1200, 1500, 59.468198761866724, -151.70028882983817, 'Blue Roof House'),
             CoordPrediction(survey.images[13], 5252, 4600, 59.46896181288199, -151.70274036887025, 'Tri-Roof'),
             CoordPrediction(survey.images[13], 8000, 2000, 59.46898088893636, -151.70414048193038,
                             'Another Green House'),
             CoordPrediction(survey.images[15], 430, 2440, 59.51433283671182, -151.48546318976835, 'Blue-Green House'),
             CoordPrediction(survey.images[15], 150, 850, 59.51397904095424, -151.48546318976835, 'Another Red House')]

    return survey, nodes


def predict_and_print_nodes():
    survey, nodes = get_test_nodes()

    total_error = 0
    num_nodes = len(nodes)
    for node in nodes:
        node.process()
        total_error += node.error
        print("========================================================")
        print(f'{node.description}\r\n'
              f'File: {node.img.file_name.ljust(25)}\r\n'
              f'Heading: {node.img.direction}.\r\n'
              f'Error: {node.error}\r\n'
              f'Predicted Coords: {node.predicted_lat}, {node.predicted_long}\r\n'
              f'Image Coords: {node.img.latitude}, {node.img.longitude}')

    average_error = total_error / num_nodes

    print()
    print("========================================================")
    print(f" - Nodes:          {num_nodes}\r\n"
          f" - Average Error:  {average_error}")
    print("========================================================")
    print()


def brute_force_camera_center_test():
    survey, nodes = get_test_nodes()

    min_error = -1
    best_x = 0
    best_y = 0
    best_roll = 0
    best_fov = 0
    best_gps_delay_offset = 0

    gps_delay = -200
    while gps_delay < 0:
        gps_delay += 25
        x_scale = .7
        while x_scale < .9:
            x_scale += .04
            y_scale = .6
            while y_scale < .75:
                y_scale += .04
                roll = 0
                while roll <= 32:
                    roll += 2
                    fov = -2
                    while fov <= 24:
                        fov += 2
                        avg_error = 0
                        for node in nodes:
                            node.img.calibration.camera_roll = roll
                            node.img.calibration.gps_center_x = x_scale
                            node.img.calibration.gps_center_x = y_scale
                            node.img.calibration.fov = fov
                            node.calculate_coordinates()
                            node.calculate_error()
                            avg_error += node.error #** 2
                            # print(f"{node.description.ljust(20)}{node.error}m")

                        avg_error /= len(nodes)
                        # print(f"x: {x_scale}, y: {y_scale}, roll: {roll}. Average Error: " + str(avg_error))
                        if avg_error < min_error or min_error < 1:
                            min_error = avg_error
                            best_x = x_scale
                            best_y = y_scale
                            best_roll = roll
                            best_fov = fov
                            best_gps_delay_offset = gps_delay
                            print(f"New Best.  x: {best_x}, y: {best_y}, roll: {best_roll}, "
                                  f"gps_offset: {best_gps_delay_offset}, fov: {best_fov}. Error: {min_error}")

    print("=========================================================================\r\n")
    print(f"Best.  x: {best_x}, y: {best_y}, roll: {best_roll}, fov: {best_fov}, gps_offset: {best_gps_delay_offset}. "
          f"Error: {min_error}")


#brute_force_camera_center_test()
predict_and_print_nodes()
make_map()
