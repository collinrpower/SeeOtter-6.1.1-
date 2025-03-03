import copy
import os
import re
import shutil
from glob import glob
from tqdm import tqdm
from os.path import realpath, join, exists
from Utilities.WaldoUtilities.waldo_image_name import WaldoImageName
from Utilities.WaldoUtilities.waldo_survey_path import WaldoSurveyPath
from Utilities.path_mapping import PathMapping
from Utilities.utilities import prompt_user
from Utilities.WaldoUtilities.waldo_utilities import is_waldo_file_name
from config import WALDO_CORRUPTED_IMAGE_REGEX, WALDO_DTTM_FILE_REGEX, \
    WALDO_IMAGE_REGEX

increment_transect_id_count = 1000


class WaldoSurveyConverter:

    @staticmethod
    def get_waldo_directories(path):
        subdirs = glob(path + "/*/")
        subdirs = list(filter(is_waldo_file_name, subdirs))
        return subdirs

    @staticmethod
    def get_image_name(type, transect, id):
        return type + "_000_" + str(transect).zfill(2) + "_" + str(id).zfill(3) + ".jpg"

    @staticmethod
    def get_image_paths_in_dir(dir):
        paths = []
        for root, dirs, files in os.walk(dir):
            for name in files:
                if name.endswith(".jpg"):
                    path = os.path.join(root, name)
                    paths.append(path)

        return paths

    @staticmethod
    def get_image_pairs(image_paths):
        image_pair_dict = {}
        for path in image_paths:
            if re.search(WALDO_IMAGE_REGEX, path):
                waldo_image = WaldoImageName.from_path(path)
                postfix = str(waldo_image.image_postfix)
                parent = os.path.dirname(path)
                key = os.path.join(parent, postfix)
                if key not in image_pair_dict.keys():

                    waldo_image_left = copy.deepcopy(waldo_image)
                    waldo_image_left.camera_type = "left"
                    waldo_image_right = copy.deepcopy(waldo_image)
                    waldo_image_right.camera_type = "right"

                    left_path = os.path.join(parent, waldo_image_left.file_name)
                    right_path = os.path.join(parent, waldo_image_right.file_name)

                    if not exists(left_path):
                        left_path = None
                    if not exists(right_path):
                        right_path = None

                    image_pair_dict[key] = (left_path, right_path)

        return list(image_pair_dict.values())

    @staticmethod
    def move_and_rename_images(path_mapping):
        with tqdm(path_mapping.items()) as path_mapping:
            path_mapping.set_description("Moving Images")
            for src, dest in path_mapping:
                if not src:
                    continue
                shutil.move(src, dest)

    @staticmethod
    def create_images_dir(parent_dir):
        image_dir_path = join(parent_dir, "Images")
        if exists(image_dir_path):
            raise Exception(f"Cannot create Images directory. Path already exists [{image_dir_path}]")
        else:
            os.mkdir(image_dir_path)
        return image_dir_path

    @classmethod
    def get_path_mapping(cls, paths, image_out_dir):
        path_mapping = PathMapping()
        for index, image_pair in enumerate(paths):
            image_id = index % increment_transect_id_count
            transect_id = int(index / increment_transect_id_count)
            left_path, right_path = image_pair

            if left_path:
                left_path = realpath(left_path)
                left_dest_name = cls.get_image_name("1", transect_id, image_id)
                left_dest_path = realpath(os.path.join(image_out_dir, left_dest_name))
                path_mapping.add_path(original_path=left_path, current_path=left_dest_path)

            if right_path:
                right_path = realpath(right_path)
                right_dest_name = cls.get_image_name("0", transect_id, image_id)
                right_dest_path = realpath(os.path.join(image_out_dir, right_dest_name))
                path_mapping.add_path(original_path=right_path, current_path=right_dest_path)

        return path_mapping

    @staticmethod
    def get_project_name_from_survey_path(path):
        waldo_path = WaldoSurveyPath(path)
        return f"{waldo_path.location}_{waldo_path.year}_{waldo_path.month_day}"

    @staticmethod
    def move_waldo_files(dir):
        waldo_files_out_dir = os.path.join(dir, "WaldoFiles")
        os.mkdir(waldo_files_out_dir)
        for file in os.listdir(dir):
            path = os.path.join(dir, file)
            if not os.path.isfile(path):
                continue
            if not re.match(WALDO_DTTM_FILE_REGEX, file):
                continue
            dest = os.path.join(waldo_files_out_dir, file)
            shutil.move(path, dest)

    @staticmethod
    def remove_waldo_image_dirs(image_dirs, force=False):
        print("Removing empty directories.")
        for image_src_dir in image_dirs:
            contents = os.listdir(image_src_dir)
            contents = [file for file in contents if not re.match(WALDO_CORRUPTED_IMAGE_REGEX, file)]
            if len(contents) > 0:
                msg = f"Warning, directory [{image_src_dir}] is not empty.\n"
                for file in contents:
                    msg += f" - {file}\n"
                msg += "Do you want to delete this directory? [Y/N]"
                response = prompt_user(msg)
                if response is False and force is False:
                    continue
            shutil.rmtree(image_src_dir)

    @staticmethod
    def validate_path_mapping(path_mapping, image_dirs):
        num_images = len(path_mapping.keys())
        if num_images == 0:
            raise Exception("Found no images in directories. Exiting.")
        else:
            msg = f"You are about to rename and move {num_images} survey images from the following directories:\n"
            for path in image_dirs:
                msg += f" - {path}\n"
            msg += "Are you sure you want to continue? [Y/N]"
            response = prompt_user(msg)
            if response is False:
                raise Exception("Cancelled actions due to user response.")

    @classmethod
    def run_for_day(cls, path):
        waldo_path = WaldoSurveyPath(path)
        if waldo_path.path_level != "month_day":
            raise Exception("Path must point to day of survey data in 'MM_DD' format.")
        if exists(join(str(waldo_path), "WaldoFiles")):
            print("Waldo files have already been converted. Skipping...")
            return join(str(waldo_path), "Images")
        image_dirs = cls.get_waldo_directories(path)
        image_paths = []
        for dir in image_dirs:
            image_paths += cls.get_image_paths_in_dir(dir)
        image_pairs = cls.get_image_pairs(image_paths)
        image_out_dir = cls.create_images_dir(waldo_path.month_day_path)
        path_mapping = cls.get_path_mapping(image_pairs, image_out_dir)
        cls.validate_path_mapping(path_mapping, image_dirs)
        cls.move_and_rename_images(path_mapping)
        cls.move_waldo_files(path)
        cls.remove_waldo_image_dirs(image_dirs)
        path_mapping.save(file_path=join(waldo_path.month_day_path, "image_path_mapping.csv"))
        print(f"Finished. {len(image_paths)} have been renamed and moved to [{image_out_dir}]")
        return image_out_dir
