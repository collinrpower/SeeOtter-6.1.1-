from Utilities.image_processing import ImageProcessing
from config import *


class ImageMetadata:

    def __init__(self, path):
        exif = ImageProcessing.load_exif_tags(path)
        self.image_path = path
        self.camera_make = self.get_exif_tag(exif, EXIF_CAMERA_MAKE)
        self.camera_model = self.get_exif_tag(exif, EXIF_CAMERA_MODEL)
        self.image_orientation = self.get_exif_tag(exif, EXIF_IMAGE_ORIENTATION)
        self.datetime = self.get_exif_tag(exif, EXIF_DATETIME_ORIGINAL)
        self.resolution_x = float(self.get_exif_tag(exif, EXIF_IMAGE_WIDTH))
        self.resolution_y = float(self.get_exif_tag(exif, EXIF_IMAGE_HEIGHT))
        self.iso = self.get_exif_tag(exif, EXIF_ISO)
        self.fstop = self.get_exif_tag(exif, EXIF_FSTOP)
        self.exposure = self.get_exif_tag(exif, EXIF_EXPOSURE)
        self.focal_length = self.get_exif_tag(exif, EXIF_FOCAL_LENGTH)

    def get_exif_tag(self, exif_tags, key):
        try:
            return exif_tags[key].printable
        except KeyError as key_err:
            print(f'Could not locate photo metadata for field [{key}] on image [{self.image_path}]')
            if FAIL_ON_MISSING_EXIF_FIELD:
                raise key_err
            else:
                print("Ignoring error due to config Setting: 'FAIL_ON_MISSING_EXIF_FIELD = False'")
                return None
