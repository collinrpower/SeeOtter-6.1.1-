from unittest import TestCase

from SurveyEntities.transect import ManualTransectAssignment


class TestManualTransectAssignment(TestCase):

    def test_load(self):
        transect_assignments = ManualTransectAssignment.load(r"TestingResources/Files/test_transect_assignment1.csv")
        self.assertEqual(2, len(transect_assignments))
        self.assertEqual("first_img_1", transect_assignments[0].start_img)
        self.assertEqual("last_img_2", transect_assignments[1].end_img)
        self.assertEqual(420, transect_assignments[0].transect_id)
        self.assertEqual(None, transect_assignments[1].transect_id)
