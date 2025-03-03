import os
from datetime import datetime, timedelta
import exifread
from PIL import Image
import exif
from exif import Orientation


class ImageProcessing:

    @staticmethod
    def get_modified_dttm(path):
        modified_timestamp = os.path.getmtime(path)
        return datetime.fromtimestamp(modified_timestamp)

    @staticmethod
    def update_utc_image_time(path, force=False, reverse=False):
        time_format = "%Y:%m:%d %H:%M:%S"
        with open(path, 'rb') as img_file:
            exif_data = exif.Image(img_file)
        img_dttm_str = exif_data.datetime_original
        img_dttm = datetime.strptime(img_dttm_str, time_format)
        modified_dttm = ImageProcessing.get_modified_dttm(path)
        modified_time_delta = img_dttm - modified_dttm
        if force or timedelta(hours=7, minutes=58) < modified_time_delta < timedelta(hours=8, minutes=2):
            if reverse:
                akst_corrected_img_dttm = img_dttm + timedelta(hours=8)
            else:
                akst_corrected_img_dttm = img_dttm - timedelta(hours=8)
            exif_data.datetime_original = akst_corrected_img_dttm.strftime(time_format)
            with open(path, 'wb') as img_file:
                img_file.write(exif_data.get_file())
        else:
            print(f"Modified time delta out of range: {modified_time_delta}")

    @staticmethod
    def rotate_image_to_180(path):
        try:
            with open(path, 'rb') as img_file:
                exif_data = exif.Image(img_file)
            if exif_data.orientation == Orientation.TOP_LEFT:
                exif_data.orientation = Orientation.BOTTOM_RIGHT
                with open(path, 'wb') as img_file:
                    img_file.write(exif_data.get_file())
        except Exception as ex:
            print(f"Error rotating image [{path}]")
            raise ex

    @staticmethod
    def rotate_image_to_normal(path):
        try:
            with open(path, 'rb') as img_file:
                exif_data = exif.Image(img_file)
            if exif_data.orientation == Orientation.BOTTOM_RIGHT:
                exif_data.orientation = Orientation.TOP_LEFT
                with open(path, 'wb') as img_file:
                    img_file.write(exif_data.get_file())
        except Exception as ex:
            print(f"Error rotating image [{path}]")
            raise ex

    @staticmethod
    def load_exif_tags(path):
        with open(path, 'rb') as file:
            tags = exifread.process_file(file, details=False)
            return tags
