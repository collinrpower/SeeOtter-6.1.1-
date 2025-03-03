from typing import Dict, List
from Camera.camera import Camera
from Utilities.json_convert import *


@JsonConvert.register
class CameraSystem:
    """
    Represents a camera system containing one or more cameras.
    """

    def __init__(self, name="", cameras: List[Camera] = None):
        self.name = name
        self.cameras: List[Camera] = cameras or []

    def __repr__(self):
        return self.name

    def __str__(self):
        return f"Camera System: {self.name}\n" \
               f"------------------------------\n" \
               f"{[{str(camera)} for camera in self.cameras]}"

    def add_camera(self, new_camera):
        for camera in self.cameras:
            if camera.name == new_camera.name:
                raise Exception(f"Error adding camera: '{new_camera.name}'. Camera with that name already exists on "
                                f"this camera system.")
        self.cameras.append(new_camera)

    @staticmethod
    def load(path):
        try:
            return JsonConvert.from_file(path)
        except FileNotFoundError:
            return None

    def save(self, path):
        JsonConvert.to_file(self, path)

    def get_camera_from_image(self, path):
        """
        Determine which camera in camera system is associated with an image using image regex.
        :param path: Path to image
        :return: Camera that is associated with a given image
        """
        if len(self.cameras) == 0:
            raise Exception("Camera system contains no cameras.")
        matching_cameras = [camera for camera in self.cameras if camera.is_image_from_this_camera(path)]
        num_matches = len(matching_cameras)
        if num_matches == 0:
            raise Exception(f"No matching cameras found for image: '{path}'")
        if num_matches == 1:
            return matching_cameras[0]
        if num_matches > 1:
            raise Exception(f"Found {num_matches} matching cameras for image: '{path}'. Each image must be unique to a "
                            f"single camera")
