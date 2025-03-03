import os
from unittest import TestCase

from UnitTests.unit_test_helpers import testing_output_dir
from Utilities.path_mapping import PathMapping


class TestPathMapping(TestCase):

    def test_constructor_init_dict(self):
        m = PathMapping({"a": 1, "b": 2})
        self.assertEqual(2, len(m.keys()))
        self.assertTrue(m["a"] == 1)
        self.assertTrue(m["b"] == 2)

    def test_remove_path(self):
        m = PathMapping()
        m.add_path("Path1", "Path2")
        m.add_path("Path3", "Path4")
        self.assertTrue(len(m.keys()) == 2)
        self.assertTrue(m["Path1"] == "Path2")
        self.assertTrue(m["Path3"] == "Path4")
        m.remove_path("Path2")
        self.assertTrue(len(m.keys()) == 1)
        self.assertFalse(m.keys().__contains__("Path1"))

    def test_get_original_path(self):
        m = PathMapping()
        m.add_path("Path1", "Path2")
        self.assertEqual("Path1", m.get_original_path(current_path="Path2"))

    def test_add_path(self):
        m = PathMapping()
        m.add_path("Path1", "Path2")
        self.assertTrue(len(m.keys()) == 1)
        self.assertTrue(m["Path1"] == "Path2")

    def test_update_path(self):
        m = PathMapping()
        m.add_path("Path1", "Path2")
        m.update_path(current_path="Path2", new_path="Path69")
        self.assertEqual("Path69", m["Path1"])

    def test_save(self):
        csv_path = os.path.join(testing_output_dir, "test_path_mapping_save.csv")
        m = PathMapping()
        m.add_path("Path1", "Path2")
        m.add_path("Path3", "Path4")
        m.save(csv_path)
        self.assertTrue(os.path.exists(csv_path))

    def test_load(self):
        csv_path = os.path.join(testing_output_dir, "test_path_mapping_load.csv")
        PathMapping({"a": "1", "b": "2"}).save(csv_path)
        m = PathMapping.load(csv_path)
        self.assertEqual(2, len(m.keys()))
        self.assertEqual("1", m["a"])
        self.assertEqual("2", m["b"])
