import os
import re
from config import WALDO_IMAGE_REGEX


class WaldoImageName:

    def __init__(self, camera_type, transect_id, image_id, on_transect=True, extension="jpg"):
        self.camera_type = camera_type
        self.transect_id = transect_id
        self.image_id = image_id
        self.on_transect = on_transect
        self.extension = extension

    def __str__(self):
        return self.file_name

    @property
    def camera_type_id(self):
        if self.camera_type == "left":
            return 1
        if self.camera_type == "right":
            return 0
        raise Exception(f"Invalid waldo camera name: {self.camera_type}")

    @property
    def file_name(self):
        fn = f"{self.camera_type_id}_{self.on_transect_id:03}_{self.transect_id:02}_{self.image_id:03}.{self.extension}"
        return fn

    @property
    def image_postfix(self):
        return f"{self.on_transect_id:03}_{self.transect_id:02}_{self.image_id:03}.{self.extension}"

    @property
    def on_transect_id(self):
        return 0 if self.on_transect else 999

    @classmethod
    def from_path(cls, path):
        file_name = os.path.basename(path)
        result = re.search(WALDO_IMAGE_REGEX, file_name)
        if result is None:
            raise Exception(f"Invalid Waldo image name [{file_name}]")
        camera_id = int(result.group(1))
        camera_type = "left" if camera_id == 1 else "right"
        on_transect = False if result.group(2) == "999" else True
        return WaldoImageName(camera_type=camera_type,
                              transect_id=int(result.group(3)),
                              image_id=int(result.group(4)),
                              on_transect=on_transect)
