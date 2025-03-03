from unittest import TestCase
from Utilities.utilities import *


class SampleClass:
    def __init__(self, a):
        self.a = a

class Test(TestCase):

    def test_cartesian_to_nautical_degrees(self):
        self.assertEqual(90, cartesian_to_compass_bearing(0))
        self.assertEqual(0, cartesian_to_compass_bearing(90))
        self.assertEqual(-90, cartesian_to_compass_bearing(180))
        self.assertEqual(45, cartesian_to_compass_bearing(45))
        self.assertEqual(-90, cartesian_to_compass_bearing(-180))

    def test_get_bearing(self):
        coord_center = 60, -151
        coord_south = 59, -151
        coord_north = 60, -151
        coord_east = 60, -150.999
        coord_west = 60, -151.001
        self.assertAlmostEqual(180, get_bearing(coord_center, coord_south), delta=.01)
        self.assertAlmostEqual(-90, get_bearing(coord_center, coord_west), delta=.01)
        self.assertAlmostEqual(90, get_bearing(coord_center, coord_east), delta=.01)
        self.assertAlmostEqual(0, get_bearing(coord_center, coord_north), delta=.01)

    def test_format_compass_bearing(self):
        self.assertEqual(0, format_compass_bearing(0))
        self.assertEqual(45, format_compass_bearing(45))
        self.assertEqual(-45, format_compass_bearing(-45))
        self.assertEqual(180, format_compass_bearing(180))
        self.assertEqual(180, format_compass_bearing(-180))
        self.assertEqual(179, format_compass_bearing(-181))
        self.assertEqual(-179, format_compass_bearing(181))
        self.assertEqual(0, format_compass_bearing(360))
        self.assertEqual(0, format_compass_bearing(-360))
        self.assertEqual(10, format_compass_bearing(370))
        self.assertEqual(-40, format_compass_bearing(-400))

    def test_bearing_within_target_threshold(self):
        self.assertTrue(bearing_within_target_threshold(0, 0, 0))
        self.assertTrue(bearing_within_target_threshold(-180, 180, 0))
        self.assertTrue(bearing_within_target_threshold(180, -180, 0))
        self.assertTrue(bearing_within_target_threshold(90, 0, 90))
        self.assertTrue(bearing_within_target_threshold(-90, 0, 90))
        self.assertTrue(bearing_within_target_threshold(-170, 170, 20))
        self.assertTrue(bearing_within_target_threshold(170, -170, 20))
        self.assertTrue(bearing_within_target_threshold(-170, -175, 10))
        self.assertTrue(bearing_within_target_threshold(170, 175, 10))

        self.assertFalse(bearing_within_target_threshold(1, 0, 0))
        self.assertFalse(bearing_within_target_threshold(0, 1, 0))
        self.assertFalse(bearing_within_target_threshold(11, 0, 10))
        self.assertFalse(bearing_within_target_threshold(0, 11, 10))
        self.assertFalse(bearing_within_target_threshold(-11, 0, 10))
        self.assertFalse(bearing_within_target_threshold(0, -11, 10))
        self.assertFalse(bearing_within_target_threshold(-179, 180, 0))
        self.assertFalse(bearing_within_target_threshold(180, -179, 0))
        self.assertFalse(bearing_within_target_threshold(90, 0, 89))
        self.assertFalse(bearing_within_target_threshold(-90, 0, 89))
        self.assertFalse(bearing_within_target_threshold(-170, 170, 19))
        self.assertFalse(bearing_within_target_threshold(170, -170, 19))
        self.assertFalse(bearing_within_target_threshold(-170, -175, 4))
        self.assertFalse(bearing_within_target_threshold(170, 175, 4))

    def test_index_out_of_range(self):
        self.assertTrue(index_out_of_range(-1, [1, 2, 3]))
        self.assertFalse(index_out_of_range(0, [1, 2, 3]))
        self.assertFalse(index_out_of_range(1, [1, 2, 3]))
        self.assertFalse(index_out_of_range(2, [1, 2, 3]))
        self.assertTrue(index_out_of_range(3, [1, 2, 3]))

    def test_get_file_name_without_extension(self):
        self.assertEqual("file", get_file_name_without_extension("C:/Dir/file.exe"))
        self.assertEqual("file", get_file_name_without_extension("file.png"))
        self.assertEqual("file", get_file_name_without_extension("../file.html"))
        self.assertEqual("file", get_file_name_without_extension("Dir\\file.html"))
        self.assertEqual("file", get_file_name_without_extension("C:/Dir\\file.html"))

    def test_get_drive_root(self):
        print(os.sep)
        self.assertEqual("C:\\", get_drive_root())

    def test_loop_iterator_forward(self):
        numbers = [1, 2, 3, 4, 5]
        out = list(loop_iterator(list=numbers, start_index=2, start_at_next=True, direction=1))
        self.assertEqual([4, 5, 1, 2, 3], out)
        out = list(loop_iterator(list=numbers, start_index=4, start_at_next=True, direction=1))
        self.assertEqual([1, 2, 3, 4, 5], out)
        out = list(loop_iterator(list=numbers, start_index=2, start_at_next=False, direction=1))
        self.assertEqual([3, 4, 5, 1, 2], out)
        out = list(loop_iterator(list=numbers, start_index=4, start_at_next=False, direction=1))
        self.assertEqual([5, 1, 2, 3, 4], out)

    def test_loop_iterator_backward(self):
        numbers = [1, 2, 3, 4, 5]
        out = list(loop_iterator(list=numbers, start_index=0, start_at_next=True, direction=-1))
        self.assertEqual([5, 4, 3, 2, 1], out)
        out = list(loop_iterator(list=numbers, start_index=2, start_at_next=True, direction=-1))
        self.assertEqual([2, 1, 5, 4, 3], out)
        out = list(loop_iterator(list=numbers, start_index=0, start_at_next=False, direction=-1))
        self.assertEqual([1, 5, 4, 3, 2], out)
        out = list(loop_iterator(list=numbers, start_index=2, start_at_next=False, direction=-1))
        self.assertEqual([3, 2, 1, 5, 4], out)

    def test_add_attr_if_not_exists(self):
        obj = SampleClass(12)
        add_attr_if_not_exists(obj, "b", 44)
        self.assertEqual(44, obj.b)
