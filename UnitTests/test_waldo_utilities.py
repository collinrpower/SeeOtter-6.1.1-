from unittest import TestCase
from Utilities.WaldoUtilities.waldo_image_name import WaldoImageName


class TestWaldoImageName(TestCase):

    def test__str__(self):
        self.assertEqual("0_000_00_000.jpg", str(WaldoImageName("right", 0, 0)))
        self.assertEqual("0_999_01_001.jpg", str(WaldoImageName("right", 1, 1, False)))
        self.assertEqual("1_999_12_251.jpg", str(WaldoImageName("left", 12, 251, False)))
        self.assertEqual("1_000_123_4567.jpg", str(WaldoImageName("left", 123, 4567, True)))

    def test_from_file_name(self):
        waldo_image = WaldoImageName.from_path(path="0_000_00_000.jpg")
        self.assertEqual("right", waldo_image.camera_type)
        self.assertEqual(True, waldo_image.on_transect)
        self.assertEqual(0, waldo_image.transect_id)
        self.assertEqual(0, waldo_image.image_id)
        self.assertEqual("jpg", waldo_image.extension)

        waldo_image = WaldoImageName.from_path(path="1_999_12_345.jpg")
        self.assertEqual("left", waldo_image.camera_type)
        self.assertEqual(False, waldo_image.on_transect)
        self.assertEqual(12, waldo_image.transect_id)
        self.assertEqual(345, waldo_image.image_id)
        self.assertEqual("jpg", waldo_image.extension)

        waldo_image = WaldoImageName.from_path(path="0_000_123_4567.jpg")
        self.assertEqual("right", waldo_image.camera_type)
        self.assertEqual(True, waldo_image.on_transect)
        self.assertEqual(123, waldo_image.transect_id)
        self.assertEqual(4567, waldo_image.image_id)
        self.assertEqual("jpg", waldo_image.extension)


