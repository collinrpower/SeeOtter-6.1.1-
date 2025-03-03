from unittest import TestCase

from Utilities.spatial_utilities import get_image_rotation_offset, get_vector_ground_collision_point


class Test(TestCase):

    def assert_lists_almost_equal(self, list1, list2, delta=.01):
        if len(list1) != len(list2):
            raise ValueError("Lists must be equal length to compare")
        for idx in range(len(list1)):
            self.assertAlmostEqual(list1[idx], list2[idx], delta=delta)

    def test_get_image_rotation_offset(self):
        resolution = (100, 100)
        hfov = 180
        self.assertEqual((0, 0, 0), get_image_rotation_offset(resolution, hfov, pixel_coords=(50, 50)))
        self.assertEqual((0, -90, 0), get_image_rotation_offset(resolution, hfov, pixel_coords=(100, 50)))
        self.assertEqual((-90, -90, 0), get_image_rotation_offset(resolution, hfov, pixel_coords=(100, 100)))

    def test_get_vector_ground_collision_point(self):
        self.assert_lists_almost_equal([0, 0, 0], get_vector_ground_collision_point(altitude=100, rotation=[0, 0, 0]))
        self.assert_lists_almost_equal([0, 100, 0],
                                       get_vector_ground_collision_point(altitude=100, rotation=[45, 0, 0]))
        self.assert_lists_almost_equal([0, -100, 0],
                                       get_vector_ground_collision_point(altitude=100, rotation=[-45, 0, 0]))
        self.assert_lists_almost_equal([-100, 0, 0],
                                       get_vector_ground_collision_point(altitude=100, rotation=[0, 45, 0]))
        self.assert_lists_almost_equal([100, 0, 0],
                                       get_vector_ground_collision_point(altitude=100, rotation=[0, -45, 0]))