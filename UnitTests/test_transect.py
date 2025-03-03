from unittest import TestCase
from os import path

from SurveyEntities.transect import Transect

southeast_kml_path = path.abspath("TestingResources/TransectKml/SoutheastTransects2022.kml")


class TestTransect(TestCase):

    def test_load_transects_from_kml(self):
        transects = Transect.load_transects_from_kml(southeast_kml_path)
        self.assertEqual(789, len(transects))
        self.assertEqual(21, transects[21].transect_id)
        self.assertEqual(0.8, transects[25].length)

    def test_is_point_within_transect_bounds(self):
        transects = Transect.load_transects_from_kml(southeast_kml_path)
        transect11 = transects[11]
        transect119 = transects[119]
        transect680 = transects[680]

        self.assertTrue(transect11.is_point_within_transect_bounds((58.355001, -136.498924)))
        self.assertFalse(transect11.is_point_within_transect_bounds((58.385248, -135.996781)))
        self.assertTrue(transect119.is_point_within_transect_bounds((58.29128, -135.91668)))
        self.assertFalse(transect119.is_point_within_transect_bounds((58.385248, -135.996781)))
        self.assertTrue(transect680.is_point_within_transect_bounds((59.031242, -138.231701)))
        self.assertFalse(transect680.is_point_within_transect_bounds((59.031242, -137.231701)))

    def test_is_on_transect(self):
        transects = Transect.load_transects_from_kml(southeast_kml_path)
        transect11 = transects[11]
        transect680 = transects[680]

        self.assertTrue(transect11.is_on_transect((58.355001, -136.498924), 52.16946455555716))
        self.assertTrue(transect11.is_on_transect((58.355001, -136.498924), -127.8121453369872))
        self.assertFalse(transect11.is_on_transect((58.355001, -136.498924), -30.16946455555716))
        self.assertFalse(transect11.is_on_transect((58.355001, -136.498924), 110.8121453369872))

        self.assertTrue(transect680.is_on_transect((59.031242, -138.231701), -50))
        self.assertTrue(transect680.is_on_transect((59.031242, -138.231701), 130))
        self.assertFalse(transect680.is_on_transect((59.031242, -138.231701), -10))
        self.assertFalse(transect680.is_on_transect((59.031242, -138.231701), 70))
