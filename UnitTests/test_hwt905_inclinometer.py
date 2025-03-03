from os.path import exists, join
from unittest import TestCase
from Inclinometer.hwt905_inclinometer import Hwt905Inclinometer
from UnitTests.unit_test_helpers import testing_files_dir


class TestHwt905Inclinometer(TestCase):

    def test_load_file_data(self):
        file_name = "220605105210.txt"
        file_path = join(testing_files_dir, file_name)
        inclinometer = Hwt905Inclinometer()
        records = inclinometer.load(file_path)
        record = records[0]
        datetime = record.datetime

        self.assertEqual(3, len(records))
        self.assertEqual(-0.0176, record.acceleration_x)
        self.assertEqual(10.9094, record.angle_x)
        self.assertEqual(2022, datetime.year)
        self.assertEqual(6, datetime.month)
        self.assertEqual(5, datetime.day)
        self.assertEqual(10, datetime.hour)
        self.assertEqual(52, datetime.minute)
        self.assertEqual(10, datetime.second)

        records2 = inclinometer.load(file_path)
        self.assertEqual(3, len(records2))
