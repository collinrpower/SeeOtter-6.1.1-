from unittest import TestCase
from config import *
from Utilities.image_processing import ImageProcessing
from unit_test_helpers import *

test_dir = "TestDir/TestImageProcessing"
test_img_src = test_image_paths[0]
test_img_path = os.path.join(test_dir, "0_000_00_000.jpg")


class TestImageProcessing(TestCase):

    @staticmethod
    def copy_test_img():
        if exists(test_img_path):
            os.remove(test_img_path)
        shutil.copy2(src=test_img_src, dst=test_img_path)

    @staticmethod
    def get_orientation(img_path):
        return ImageProcessing.load_exif_tags(test_img_path)[EXIF_IMAGE_ORIENTATION].printable

    def test_get_modified_dttm(self):
       # todo: make test
        pass

    def test_update_utc_image_time(self):
        # todo: make test
        pass

    def test_rotate_image(self):
        self.copy_test_img()
        orientation = self.get_orientation(test_img_path)
        self.assertEqual("Horizontal (normal)", orientation)
        ImageProcessing.rotate_image_to_180(test_img_path)
        orientation = self.get_orientation(test_img_path)
        self.assertEqual("Rotated 180", orientation)
        ImageProcessing.rotate_image_to_normal(test_img_path)
        orientation = self.get_orientation(test_img_path)
        self.assertEqual("Horizontal (normal)", orientation)

    def test_load_exif_tags(self):
        self.copy_test_img()
        tags = ImageProcessing.load_exif_tags(test_img_path)
        self.assertEqual(64, len(tags))
        self.assertEqual(tags[EXIF_CAMERA_MAKE].printable, "Canon")
        self.assertEqual(tags[EXIF_IMAGE_HEIGHT].printable, "5792")
