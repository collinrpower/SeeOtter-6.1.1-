from unittest import TestCase
from Camera.camera import Camera
from Camera.camera_system import CameraSystem
from Processing.survey_image_processing import get_coordinates_at_pixel, get_coordinate_bounds, \
    get_distance_between_coordinates, get_total_rotation_for_pixel
from SurveyEntities.survey_image import SurveyImage


test_img = "TestingResources/Images/test_img.jpg"


class Test(TestCase):

    def assert_lists_almost_equal(self, list1, list2, delta=.01):
        if len(list1) != len(list2):
            raise ValueError("Lists must be equal length to compare")
        for idx in range(len(list1)):
            self.assertAlmostEqual(list1[idx], list2[idx], delta=delta)

    def test_assert_lists_almost_equal(self):
        self.assert_lists_almost_equal([1, 2, 3], [1, 2, 3])
        self.assert_lists_almost_equal([1.1, 2.2, 3.3], [1.1002, 2.199, 3.303], delta=.01)
        with self.assertRaises(ValueError):
            self.assert_lists_almost_equal(list1=[1, 2, 3, 4], list2=[1, 2, 3])

    @staticmethod
    def get_test_img(altitude, coordinates, direction, camera=Camera()):
        img = SurveyImage(file_path=test_img)
        img.altitude = altitude
        img.latitude, img.longitude = coordinates
        img.direction = direction
        camera.orientation.hfov = 90
        img.camera = camera
        return img

    def test_get_total_rotation_for_pixel(self):
        img = self.get_test_img(altitude=1000, coordinates=(0, 0), direction=0)
        self.assert_lists_almost_equal((0, 0, 0), get_total_rotation_for_pixel(img, *img.center_pixel))
        self.assert_lists_almost_equal((0, -45, 0),
                                       get_total_rotation_for_pixel(img, img.resolution_x, img.resolution_y/2))
        self.assert_lists_almost_equal((-30, 0, 0),
                                       get_total_rotation_for_pixel(img, img.resolution_x/2, img.resolution_y))
        img.direction = 90
        get_total_rotation_for_pixel(img, img.resolution_x / 2, img.resolution_y)
        self.assert_lists_almost_equal((-30, 0, 90),
                                       get_total_rotation_for_pixel(img, img.resolution_x/2, img.resolution_y))
        # todo: add more tests for different camera calibration values

    def test_get_coordinates_at_pixel(self):
        img = self.get_test_img(altitude=1000, coordinates=(0, 0), direction=0)

        top = get_coordinates_at_pixel(img, img.resolution_x/2, 0)
        bottom = get_coordinates_at_pixel(img, img.resolution_x/2, img.resolution_y)
        left = get_coordinates_at_pixel(img, 0, img.resolution_y/2)
        right = get_coordinates_at_pixel(img, img.resolution_x, img.resolution_y/2)

        # Sanity checks
        self.assertTrue(top[0] > 0)
        self.assertTrue(bottom[0] < 0)
        self.assertTrue(left[1] < 0)
        self.assertTrue(right[1] > 0)

        # todo: add more tests
        # self.assert_lists_almost_equal(
        #     (0, 0),
        #     get_coordinates_at_pixel(img, img.resolution_x/2, img.resolution_y/2), delta=.000001)
        # self.assert_lists_almost_equal(
        #     (-0.005221379610074049, 0),
        #     get_coordinates_at_pixel(img, img.resolution_x/2, img.resolution_y), delta=.000001)
        # self.assert_lists_almost_equal(
        #     (0.007384145828203412, -0.008983152890597347),
        #     get_coordinates_at_pixel(img,  0, img.resolution_y), delta=.000001)
        # right = get_coordinates_at_pixel(img,  img.resolution_x, img.resolution_y/2)
        # self.assertAlmostEqual(first=1000, second=get_distance_between_coordinates((0, 0), right), delta=1)
        # img.direction = 90
        # self.assert_lists_almost_equal(
        #     (0.0, 0.005186425711035608),
        #     get_coordinates_at_pixel(img, img.resolution_x/2, img.resolution_y), delta=.000001)
        # self.assert_lists_almost_equal(
        #     (0.009043694744882107, 0.007334713641292088),
        #     get_coordinates_at_pixel(img,  0, img.resolution_y), delta=.000001)
        # img.direction = -90
        # self.assert_lists_almost_equal(
        #     (0.0, -0.005186425711035608),
        #     get_coordinates_at_pixel(img, img.resolution_x/2, img.resolution_y), delta=.000001)
        # self.assert_lists_almost_equal(
        #     (-0.009043694744882107, -0.007334713641292088),
        #     get_coordinates_at_pixel(img,  0, img.resolution_y), delta=.000001)
        # img.direction = 0
        # img.camera.orientation.angle_y = -45
        # self.assert_lists_almost_equal(
        #     (0.0, 0.008983152841195217),
        #     get_coordinates_at_pixel(img, img.resolution_x/2, img.resolution_y/2), delta=.000001)
        # self.assert_lists_almost_equal(
        #     (0.007384145828203412, 0.008983152890597347),
        #     get_coordinates_at_pixel(img,  img.resolution_x/2, img.resolution_y), delta=.000001)
        # self.assert_lists_almost_equal(
        #     (0.0, 0.0),
        #     get_coordinates_at_pixel(img,  0, img.resolution_y/2), delta=.000001)
        # img.direction = 0
        # img.camera.orientation.angle_y = 0
        # img.camera.orientation.angle_x = 45
        # self.assert_lists_almost_equal(
        #     (0.009043694769749647, 0.0),
        #     get_coordinates_at_pixel(img, img.resolution_x/2, img.resolution_y/2), delta=.000001)
        # self.assert_lists_almost_equal(
        #     (0.03375152833246258, 0.0),
        #     get_coordinates_at_pixel(img,  img.resolution_x/2, img.resolution_y), delta=.000001)
        # self.assert_lists_almost_equal(
        #     (0.012789715743523994, -0.008983152989401617),
        #     get_coordinates_at_pixel(img,  0, img.resolution_y/2), delta=.000001)
        # img.direction = 0
        # img.camera.orientation.angle_x = 0
        # img.camera.orientation.angle_z = 90

        print(f"Center:       {get_coordinates_at_pixel(img, img.resolution_x/2, img.resolution_y/2)}")
        print(f"Top:          {get_coordinates_at_pixel(img, img.resolution_x/2, 0)}")
        print(f"Bottom:       {get_coordinates_at_pixel(img, img.resolution_x/2, img.resolution_y)}")
        print(f"Left:         {get_coordinates_at_pixel(img, 0, img.resolution_y/2)}")
        print(f"Right:        {get_coordinates_at_pixel(img, img.resolution_x, img.resolution_y/2)}")
        print(f"Top-Left:     {get_coordinates_at_pixel(img, 0, 0)}")
        print(f"Bottom-Right: {get_coordinates_at_pixel(img, img.resolution_x, img.resolution_y)}")
        print(f"Bottom-Left:  {get_coordinates_at_pixel(img, 0, img.resolution_y)}")

        """ 
        direction = -90
        Top:          (0.0, -0.005186425711035608)
        Bottom:       (0.0, 0.005186425711035608)
        Left:         (-0.009043694769749647, 0.0)
        Right:        (0.009043694769749647, 0.0)
        Top-Left:     (-0.009043694744882107, -0.007334713641292088)
        Bottom-Right: (0.009043694744882107, 0.007334713641292088)
        
        direction = 0
        y_roll = -45
        Center:       (0.0, 0.008983152841195217)
        Top:          (0.007384145828203412, 0.008983152890597347)
        Bottom:       (-0.007384145828203412, 0.008983152890597347)
        Left:         (0.0, 0.0)
        
        direction = 0
        x_roll = 45
        
        Center:       (0.009043694769749647, 0.0)
        Top:          (0.03375152833246258, 0.0)
        Bottom:       (0.002423250710335558, 0.0)
        Left:         (0.012789715743523994, -0.008983152989401617)
        """

