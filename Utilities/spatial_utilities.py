import numpy as np
from scipy.spatial.transform import Rotation as R
from Utilities.utilities import get_rounded_list


def line_plane_collision(plane_normal, plane_point, ray_direction, ray_point, epsilon=1e-6):
    """
    Calculates coordinates that a vector crosses a plane.
    :param plane_normal: Normal vector of plane
    :param plane_point: Any point on plane
    :param ray_direction: Ray direction vector
    :param ray_point: Starting point of ray
    :param epsilon: Epsilon
    :return: coordinates that a vector crosses a plane
    """
    ndotu = plane_normal.dot(ray_direction)
    if abs(ndotu) < epsilon:
        raise RuntimeError("no intersection or line is within plane")
    w = ray_point - plane_point
    si = -plane_normal.dot(w) / ndotu
    psi = w + si * ray_direction + plane_point
    return psi


def get_vector_ground_collision_point(altitude, rotation):
    """
    Applies rotation to a vector pointed straight down at (0, 0, altitude) and calculates the x, y offset
    between the origin and the point where a vector crosses the ground. This is to find distance between
    a camera's GPS location and a point on the ground.
    :param altitude: Altitude
    :param rotation: Rotation to apply to vector
    :return: Distance from origin that vector crosses ground (z=0)
    """
    water_plane_norm = np.array([0, 0, 1])
    water_plane_point = np.array([0, 0, 0])
    rotation[2] *= -1
    ray_direction = get_rotated_vector(np.array([0, 0, -1]), rotation)
    ray_point = np.array([0, 0, altitude])  # Any point along the ray
    psi = line_plane_collision(water_plane_norm, water_plane_point, ray_direction, ray_point)

    return psi


def get_rotated_vector(vector, rotation):
    """
    Rotates a vector by a given x, y, z euler angle
    :param vector: Inital vector
    :param rotation: Rotation to apply to vector (x, y, z)
    :return: Rotated vector
    """
    for idx, axis_val in enumerate(rotation):
        rotation_radians = np.radians(rotation[idx])
        axis_array = [0, 0, 0]
        axis_array[idx] = 1
        rotation_axis = np.array(axis_array)
        rotation_vector = rotation_radians * rotation_axis
        vec_rotation = R.from_rotvec(rotation_vector)
        vector = vec_rotation.apply(vector)
    return vector


def get_image_rotation_offset(resolution, hfov, pixel_coords):
    """
    Calculates the x and y degrees of rotation between the center point of an
    image and a target point given as pixel coordinates
    :param resolution: Resolution of image
    :param hfov: Horizontal field of view
    :param pixel_coords: Pixel coordinates of target on image
    :return: Rotation angle between center of image and target
    """
    x, y = pixel_coords
    degrees_per_pixel = float(hfov) / float(resolution[0])
    center = (resolution[0]/2, resolution[1]/2)
    x_offset = x - center[0]
    y_offset = y - center[1]
    x_rotation = -y_offset * degrees_per_pixel
    y_rotation = -x_offset * degrees_per_pixel
    return x_rotation, y_rotation, 0