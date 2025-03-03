import json
import jsonpickle
import os.path
import pandas as pd
import numpy as np
from os.path import isdir
from shapely import geometry
from Inclinometer.inclinometer import Inclinometer
from SurveyEntities.survey_image import *
from os import walk
from tqdm import tqdm
from Camera.camera_system import CameraSystem
from SurveyEntities.transect import Transect, ManualTransectAssignment
from Utilities.custom_exceptions import SurveyVersionException, ImageDirNotFoundException, SurveyDirNotFoundException
from config import *
from Utilities.utilities import *
from version import version


class Survey(object):
    """
    Main project representative of an arial photo survey. Responsible for loading and storing
    all info relating to the survey:
      - Project and file paths
      - Survey Images
      - Camera System
      - Inclinometer Data
      - Transects
    """

    def __init__(self, survey_name, survey_path=None, images_dir=None, camera_system: CameraSystem = None,
                 images: List[SurveyImage] = None, inclinometer: Inclinometer = None):
        mkdir_if_not_exists(SURVEYS_DIR)
        self.survey_name = survey_name
        self.project_path = survey_path or Survey.get_default_survey_path(survey_name)
        self.images_dir = images_dir or self.default_images_dir
        self.version = version
        self.has_unsaved_changes = False
        self.create_survey_directories()
        self.transects: List[Transect] = []
        self.loaded_inclinometer_files = []
        self.loaded_kml_modified_dttm = None
        self.inclinometer: Inclinometer = inclinometer
        self.images: List[SurveyImage] = images or Survey.load_images(self.images_dir)
        self.excluded_images: List[SurveyImage] = []
        self.camera_system = camera_system or self.load_camera_system()
        self.load_transects()
        self.load_and_apply_inclinometer_data()
        self.assign_cameras_to_images()
        self.order_images_by_type_and_datetime()
        self.assign_image_ids()

    def __repr__(self):
        return f"{self.survey_name} (V{self.version})"

    @staticmethod
    def surveys_dir():
        return realpath(join(get_root_path(), SURVEYS_DIR))

    def save_file_path(self):
        return self.get_relative_path(SURVEY_SAVE_FILE)

    @staticmethod
    def get_default_survey_path(survey_name):
        if survey_name is None:
            raise Exception("Survey name cannot be empty.")
        return join(get_root_path(), SURVEYS_DIR, survey_name)

    @staticmethod
    def get_survey_save_file_path(survey_path):
        return realpath(join(survey_path, SURVEY_SAVE_FILE))

    def get_relative_path(self, path):
        return realpath(join(self.project_path, path))

    @property
    def config(self):
        return SeeOtterConfig.instance()

    @property
    def inclinometer_dir(self):
        return self.get_relative_path(INCLINOMETER_DATA_DIR)

    @property
    def backup_dir(self):
        return self.get_relative_path(BACKUP_DIR)

    @property
    def transect_dir(self):
        return self.get_relative_path(TRANSECT_DIR)

    @property
    def results_dir(self):
        return self.get_relative_path(RESULTS_DIR)

    @property
    def default_images_dir(self):
        return self.get_relative_path(IMAGE_DIR)

    @property
    def map_file_path(self):
        return join(self.results_dir, f"SurveyMap({self.survey_name}).html")

    @property
    def otter_map_file_path(self):
        return join(self.results_dir, f"SurveyOtterMap({self.survey_name}).html")

    @property
    def transect_assignment_file_path(self):
        return join(self.transect_dir, TRANSECT_ASSIGNMENT_FILE)

    @property
    def transect_map_file_path(self):
        return join(self.results_dir, f"SurveyTransectMap({self.survey_name}).html")

    @property
    def transect_map_file_path_kml(self):
        return join(self.results_dir, f"SurveyTransectMap({self.survey_name}).kml")

    @property
    def camera_system_path(self):
        return self.get_relative_path(CAMERA_SYSTEM_FILE)

    @property
    def num_images(self):
        return len(self.images)

    @property
    def has_images(self):
        return self.num_images > 0

    @property
    def has_no_images(self):
        return not self.has_images

    @property
    def on_transect_images(self):
        return [image for image in self.images if image.transect_id is not None]

    @property
    def off_transect_images(self):
        return [image for image in self.images if image.transect_id is None]

    @property
    def images_with_inclinometer_data(self):
        return [image for image in self.images if image.has_inclinometer_data]

    @property
    def images_without_inclinometer_data(self):
        return [image for image in self.images if not image.has_inclinometer_data]

    @property
    def predictions(self) -> List[ObjectPredictionData]:
        return [prediction for image in self.images for prediction in image.predictions]

    @property
    def processed_images(self):
        return [image for image in self.images if image.has_been_processed is True]

    @property
    def unprocessed_images(self):
        return [image for image in self.images if image.has_been_processed is False]

    @property
    def pre_processed_images(self):
        return [image for image in self.images if image.has_been_preprocessed is True]

    @property
    def validated_predictions(self):
        return [p for p in self.predictions if p.validation_state != ValidationState.UNVALIDATED]

    @property
    def validated_correct_predictions(self):
        return [p for p in self.predictions if p.validation_state == ValidationState.CORRECT]

    @property
    def validated_incorrect_predictions(self):
        return [p for p in self.predictions if p.validation_state == ValidationState.INCORRECT]

    @property
    def validated_ambiguous_predictions(self):
        return [p for p in self.predictions if p.validation_state == ValidationState.AMBIGUOUS]

    @property
    def description(self):
        camera_system = str(self.camera_system.name) if self.camera_system else "None"
        inclinometer = str(self.inclinometer) if hasattr(self, "inclinometer") and self.inclinometer else "None"
        return "====================================================\n" + \
               "Survey: ".ljust(30) + self.survey_name + "\n" + \
               "Version: ".ljust(30) + str(self.version) + "\n" + \
               "Camera System: ".ljust(30) + camera_system + "\n" + \
               "Inclinometer: ".ljust(30) + inclinometer + "\n" \
               "Project Path: ".ljust(31) + str(self.project_path) + "\n" \
               "Images Dir: ".ljust(31) + self.images_dir + "\n" + \
               "Images: ".ljust(30) + str(self.num_images) + "\n" + \
               "Processed: ".ljust(30) + str(len(self.processed_images)) + "\n" + \
               "Unprocessed: ".ljust(30) + str(len(self.unprocessed_images)) + "\n" + \
               "Excluded: ".ljust(30) + str(len(self.excluded_images)) + "\n" + \
               "Predictions: ".ljust(30) + f"{len(self.predictions)}" + "\n" + \
               "  - Validated: ".ljust(30) + f"{len(self.validated_predictions)}" + "\n" + \
               "  - Validated Correct: ".ljust(30) + f"{len(self.validated_correct_predictions)}" + "\n" + \
               "  - Validated Incorrect: ".ljust(30) + f"{len(self.validated_incorrect_predictions)}" + "\n" + \
               "  - Validated Ambiguous: ".ljust(30) + f"{len(self.validated_ambiguous_predictions)}" + "\n" + \
               "===================================================="

    @staticmethod
    def get_all_survey_dirs():
        return [os.path.abspath(survey_path) for survey_path in os.listdir(Survey.surveys_dir())]

    @classmethod
    def new(cls, survey_name, survey_path=None, images_dir=None, camera_system=None, images=None, overwrite=False,
            force=False, inclinometer=None, survey_type=None):
        print(f"Creating new survey: {survey_name}")
        if survey_name is None:
            raise Exception("Survey name required for creating new survey")
        survey_path = survey_path or Survey.get_default_survey_path(survey_name)
        save_file_path = Survey.get_survey_save_file_path(survey_path)
        if os.path.exists(save_file_path):
            if overwrite:
                if force or prompt_user(f"You are about to overwrite survey ({survey_name}). Continue? [y/n]"):
                    Survey.remove_project_files(survey_path=survey_path)
                else:
                    raise Exception("Overwrite survey cancelled (Execution mode can be changed in config.py). Exiting.")
            else:
                raise Exception(
                    f"Error creating new survey. Survey already exists at {survey_path} and overwrite=False")

        survey = cls(survey_name=survey_name, survey_path=survey_path, images_dir=images_dir,
                     camera_system=camera_system, images=images, inclinometer=inclinometer)
        survey.save()
        return survey

    @classmethod
    def upgrade_project_version(cls, survey=None, survey_name=None, survey_path=None, images_dir=None, survey_type=None,
                                force=False):
        if survey is None and survey_name is None and survey_path is None:
            raise Exception("No survey, survey name, or survey_path supplied.")
        print(f"Preparing to upgrade survey.")
        if survey is None:
            survey_path = survey_path or Survey.get_default_survey_path(survey_name)
        old_survey = survey or Survey.load(survey=survey_path or survey_name, images_dir=images_dir, quick_load=True,
                                           skip_upgrade=True)
        if old_survey.version.major == version.major and force is False:
            raise Exception(f"Survey version is same as current (V{version.major}). Cannot upgrade.")
        old_survey.backup()
        confirm_upgrade = force or prompt_user(f"You are about to upgrade survey from V{old_survey.version} to "
                                               f"V{version}. Continue? (Y/N)")
        if confirm_upgrade or force:
            survey_type = survey_type or cls
            new_survey = survey_type(survey_name=old_survey.survey_name,
                                     survey_path=old_survey.project_path,
                                     images_dir=old_survey.images_dir)
            Survey.copy_survey_data(old_survey, new_survey)
            new_survey.load_predictions_from_backup()
            new_survey.save()
            print(f"Success! Upgraded from V{old_survey.version} -> V{new_survey.version}")
            return new_survey
        else:
            print("Cancelled survey upgrade.")

    @staticmethod
    def copy_survey_data(old_survey, new_survey):
        for old_image in old_survey.images:
            new_image = new_survey.get_image(old_image.file_name)
            if new_image is None:
                raise Exception(f"Error upgrading survey. Could not find image '{old_image}'")
            new_image.has_been_preprocessed = old_image.has_been_preprocessed
            new_image.has_been_processed = old_image.has_been_processed
            new_image.tags = old_image.tags
        for old_excluded_image in old_survey.excluded_images:
            new_excluded_image = new_survey.get_image(old_excluded_image.file_name)
            new_survey.exclude_image(new_excluded_image)

    @staticmethod
    def locate_save_file_path(survey):
        """
        Get the save file path of a survey given either:
           - Survey save file path
           - Survey directory path containing save file
           - Name of survey in default location
        :param survey: Survey path or name
        :return: Path to survey save file
        """
        survey_str = str(survey)
        if survey_str.endswith(SURVEY_SAVE_FILE):
            survey_path = Path(survey_str).parent.absolute()
        elif isdir(survey_str):
            survey_path = survey_str
        else:
            survey_path = Survey.get_default_survey_path(survey_str)
        save_file = join(survey_path, SURVEY_SAVE_FILE)
        if exists(save_file):
            return save_file, survey_path
        raise FileNotFoundError(f"Error locating survey: '{survey_str}'. Make sure the file exists and you are supplying "
                                f"one of the following:\n"
                                f"   - Name of survey stored in default location '/SeeOtter/Surveys/[SurveyName]/'\n"
                                f"   - Path to save file (Ending with '{SURVEY_SAVE_FILE}')\n"
                                f"   - Path to folder that contains save file")

    @classmethod
    def load(cls, survey, images_dir=None, reload_images=False, skip_upgrade=False, quick_load=False):
        save_file_path, survey_dir = Survey.locate_save_file_path(survey)
        print(f"Loading Survey From: {save_file_path}")
        with open(save_file_path, 'r') as save_file:
            data = json.load(save_file)
            survey = jsonpickle.decode(data)
        survey.update_paths(survey_dir, images_dir)
        if survey.version_upgrade_required() and skip_upgrade is False:
            raise SurveyVersionException(f"Survey version upgrade required. Run helper script "
                                         f"'upgrade_survey_version.py'")
        if quick_load:
            return survey
        survey.update_survey_attributes()
        if reload_images:
            survey.images = Survey.load_images(survey.images_dir)
        else:
            survey.load_new_images()
        survey.create_survey_directories()
        survey.load_transects()
        survey.load_camera_system()
        survey.load_and_apply_inclinometer_data()
        survey.assign_cameras_to_images()
        survey.order_images_by_type_and_datetime()
        survey.assign_image_ids()
        print(survey.description)
        return survey

    def save(self):
        self.create_survey_directories()
        self.save_camera_system()
        self.write_survey_to_json()
        self.has_unsaved_changes = True

    def save_camera_system(self):
        if self.camera_system:
            self.camera_system.save(self.camera_system_path)

    def write_survey_to_json(self):
        save_file_path = self.save_file_path()
        with open(save_file_path, 'w') as save_file:
            data = jsonpickle.encode(self)
            json.dump(data, save_file)
            print(f"Saved project to {save_file_path}")

    @staticmethod
    def load_images(image_dir):
        images = []
        image_paths = []
        for (root, dirs, files) in walk(image_dir):
            image_paths = [(file, join(root, file)) for file in files]
        with tqdm(image_paths) as image_paths:
            errors = []
            image_paths.set_description("Loading Images".ljust(PROGRESS_BAR_LABEL_PADDING))
            for (filename, path) in image_paths:
                if str(filename).upper().endswith(IMAGE_EXT.upper()):
                    try:
                        images.append(SurveyImage(path))
                    except Exception as ex:
                        errors.append(f"Error loading image [{path}]: {str(ex)}")
            if len(errors) > 0:
                print(f"{len(errors)} errors occurred while loading images:")
                for error in errors:
                    print(f"   - {error}")
            return images

    def load_image(self, path):
        self.images.append(SurveyImage(path))

    def load_new_images(self):
        image_paths_in_dir = [os.path.realpath(join(self.images_dir, path)) for path in os.listdir(self.images_dir)]
        image_paths_in_survey = [os.path.realpath(img.file_path) for img in self.images + self.excluded_images]
        new_image_count, failed_image_count = 0, 0
        for path in image_paths_in_dir:
            if not image_paths_in_survey.__contains__(path):
                try:
                    self.load_image(path)
                    new_image_count += 1
                except Exception as ex:
                    failed_image_count += 1
                    print(f"Error loading image [{path}]: {str(ex)}")
        print(f"Finished loading new images. [Successful: {new_image_count}] [Failed: {failed_image_count}]")

    def update_survey_attributes(self):
        """
        Adds any attributes not contained in an older survey. Used for backwards compatibility.
        """
        add_attr_if_not_exists(self, "loaded_kml_modified_dttm")
        add_attr_if_not_exists(self, "has_unsaved_changes", False)
        for image in self.images:
            add_attr_if_not_exists(image, "transect_id")
        for prediction in self.predictions:
            add_attr_if_not_exists(prediction, "overlaps_image")
            add_attr_if_not_exists(prediction, "almost_overlaps_image")
            add_attr_if_not_exists(prediction, "transect_overlap_images", [])

    def exclude_image(self, image: SurveyImage):
        image.excluded = True
        self.images.remove(image)
        self.excluded_images.append(image)
        self.has_unsaved_changes = True

    def clear_all_validations(self):
        print("Clearing all prediction validations")
        if len(self.validated_predictions) > 0:
            [image.reset_validations() for image in self.images]
            self.has_unsaved_changes = True

    def clear_all_predictions(self, *args, **kwargs):
        print("Clearing all predictions")
        if len(self.predictions) > 0:
            for image in self.images:
                image.predictions.clear()
                image.has_been_processed = False
            self.has_unsaved_changes = True

    def rename_image(self, image: SurveyImage, file_name):
        image.rename_image(file_name)

    def update_paths(self, project_path, images_dir=None, validate_paths=True, save_changes=False):
        project_path_changed, image_dir_changed = False, False
        is_default_image_dir = self.images_dir == self.default_images_dir
        # Update project path
        if not paths_equal(self.project_path, project_path):
            self.update_project_path(project_path)
            project_path_changed = True
        # Update image dir if given
        if images_dir and not paths_equal(self.images_dir, images_dir):
            self.update_images_dir(images_dir)
            image_dir_changed = True
        # Update image dir if using default location and project moved
        elif is_default_image_dir and self.images_dir != self.default_images_dir:
            self.update_images_dir()
            image_dir_changed = True
        if validate_paths:
            self.validate_paths()
        # Save project if paths changed
        if project_path_changed or image_dir_changed:
            self.has_unsaved_changes = True
            if save_changes:
                print(f"Updated paths: \n - Survey Path: {self.project_path}\n - Image Dir: {self.images_dir}")
                print("Saving Survey...")
                self.save()

    def validate_paths(self):
        if not exists(self.project_path):
            raise SurveyDirNotFoundException(f"Validation Error. Project path does not exist: '{self.project_path}'")
        if not exists(self.images_dir):
            raise ImageDirNotFoundException(f"Validation Error. Image dir does not exist:  '{self.images_dir}'")
        missing_images = []
        for image in self.images:
            if not exists(image.file_path):
                missing_images.append(image)
        if len(missing_images) > 0:
            raise FileNotFoundError(f"Validation Error. Could not find {len(missing_images)} images.")
        print("Validated project paths")

    def update_project_path(self, project_path):
        while not exists(project_path):
            user_input = input(f"Project path not found at '{project_path}'.\nSupply project path, or hit "
                               f"ENTER to cancel")
            if user_input == "":
                raise FileNotFoundError(f"Error updating project path. Path does not exist: '{project_path}'")
            else:
                project_path = user_input
        if self.project_path != project_path:
            print("Updating project path")
            self.project_path = project_path

    def update_images_dir(self, images_dir=None):
        images_dir = images_dir or self.default_images_dir
        while not exists(images_dir):
            user_input = input(f"Project path not found at '{images_dir}'.\nSupply correct path to image directory, or "
                               f"hit [ENTER] to cancel")
            if user_input == "":
                raise FileNotFoundError(f"Error updating image dir. Path does not exist: '{images_dir}'")
            else:
                project_path = user_input
        if self.images_dir != images_dir:
            print("Updating images dir")
            self.images_dir = images_dir
            for image in self.images + self.excluded_images:
                image_path = os.path.normpath(join(self.images_dir, image.file_name))
                image.update_file_path(image_path)

    def backup(self, backup_name=None):
        self.backup_predictions()
        if not backup_name:
            backup_name = f"backup_({get_datetime_str()})"
        backup_dir = join(self.backup_dir, backup_name)
        os.mkdir(backup_dir)
        files = [self.get_relative_path(file) for file in os.listdir(self.project_path)
                 if file not in EXCLUDE_FROM_BACKUP]
        for file in files:
            if os.path.isdir(file):
                dir_name = os.path.basename(file)
                dest = os.path.join(backup_dir, dir_name)
                shutil.copytree(file, dest)
            else:
                shutil.copy2(file, backup_dir)
        print(f"Completed backup at '{backup_dir}'")
        return backup_dir

    def backup_predictions(self):
        if not self.predictions:
            print("No predictions found in survey. Skipping prediction backup.")
            return
        file_path = self.get_relative_path(PREDICTIONS_BACKUP_FILE)
        prediction_json = [prediction.to_json_string() for prediction in self.predictions]
        with open(file=file_path, mode="w", encoding='utf-8') as file:
            json.dump(prediction_json, file, ensure_ascii=False, indent=4)

    def load_predictions_from_backup(self, file_path=None):
        print("Loading predictions from backup")
        file_path = file_path or self.get_relative_path(PREDICTIONS_BACKUP_FILE)
        if not exists(file_path):
            print(f"Warning: No prediction data file found at '{file_path}'")
            return
        with open(file=file_path, mode="r", encoding='utf-8') as file:
            loaded_predictions_json = json.load(file)
            if loaded_predictions_json is None:
                raise Exception(f"No prediction data found in '{file_path}'")
        predictions = []
        for prediction_json in loaded_predictions_json:
            prediction = ObjectPredictionData.from_json_string(prediction_json)
            predictions.append(prediction) if prediction else None
        self.clear_all_predictions()
        for prediction in predictions:
            image = self.get_image(prediction.image_name)
            image.predictions.append(prediction)

    def version_upgrade_required(self, ignore_version_error=False):
        return self.version.major < version.major

    def order_images_by_type_and_datetime(self):
        if self.camera_system:
            self.images = sorted(self.images, key=lambda img: (img.camera.name, img.datetime))
        else:
            self.images = sorted(self.images, key=lambda img: img.datetime)

    def assign_image_ids(self):
        for index, image in enumerate(self.images):
            image.id = index

    def create_survey_directories(self):
        mkdir_if_not_exists(self.project_path)
        for dir in CREATE_SURVEY_DIRS:
            dir_path = self.get_relative_path(dir)
            mkdir_if_not_exists(dir_path)

    @staticmethod
    def remove_project_files(survey_name=None, survey_path=None):
        if survey_name is None and survey_path is None:
            raise Exception("Project path or survey name required.")
        survey_path = survey_path or Survey.get_default_survey_path(survey_name=survey_name)
        save_file = Survey.get_survey_save_file_path(survey_path=survey_path)
        if exists(save_file):
            os.remove(save_file)

    def load_camera_system(self):
        if self.num_images == 0 and not os.path.exists(self.camera_system_path):
            print("No images in survey and no camera system config found. Skipping loading of camera config.")
            return
        try:
            camera_system: CameraSystem = CameraSystem.load(self.camera_system_path)
            self.camera_system = camera_system
            return camera_system
        except Exception as ex:
            print(f"Error loading camera system config.")
            raise ex

    def clear_transects(self):
        if self.transects or self.loaded_kml_modified_dttm:
            self.has_unsaved_changes = True
        self.transects = []
        self.loaded_kml_modified_dttm = None
        for image in self.images:
            image.transect_id = None

    def load_transects(self, force=False):
        files = [file for file in os.listdir(self.transect_dir) if file.endswith(".kml")]
        loaded_kml_transects = False
        if len(files) == 0:
            print(f"No kml files found in {self.transect_dir}")
        elif len(files) > 1:
            print("Warning: multiple kml files found in transects folder. Skipping loading of kml transects.")
            [print(f"  - {file}") for file in files]
        else:
            path = os.path.join(self.transect_dir, files[0])
            modified_dttm = os.path.getmtime(path)
            if modified_dttm == self.loaded_kml_modified_dttm and force is False:
                print("Transect file already loaded, and no changes found. Skipping loading of transects.")
                # return
            else:
                print(f"Loading transects from '{path}'")
                self.transects = Transect.load_transects_from_kml(path)
                self.loaded_kml_modified_dttm = modified_dttm
                loaded_kml_transects = True
                self.fill_off_transect_gaps()
                self.validate_transect_altitude_range()
        # Only run transect assignment if new data
        if force or loaded_kml_transects:
            self.assign_transect_ids_to_images()
        loaded_manual_transects = self.apply_manual_transect_assignments()
        if loaded_manual_transects or loaded_manual_transects:
            self.has_unsaved_changes = True
        return self.transects

    def assign_transect_ids_to_images(self):
        if self.has_no_images:
            return
        if self.transects is None:
            print("No loaded transects to apply.")
        else:
            print("Assigning transect id's to images.")
            survey_bounds = self.get_coordinate_bounds()
            nearby_transects = [transect for transect in self.transects if transect.intersects_polygon(survey_bounds)]
            for image in tqdm(self.images):
                for transect in nearby_transects:
                    if transect.is_on_transect(coordinates=image.coordinates, bearing=image.direction):
                        image.transect_id = transect.transect_id
                        break

    def apply_manual_transect_assignments(self):
        transect_assignments = ManualTransectAssignment.load(self.transect_assignment_file_path)
        if transect_assignments is None:
            print("No manual transect assignments found. Skipping...")
            return False
        print(f"Applying {len(transect_assignments)} manual transect assignments from "
              f"'{self.transect_assignment_file_path}'")
        modified = False
        images = sorted(self.images, key=lambda img: img.file_name)
        for assignment in transect_assignments:
            start_img, end_img = self.get_image(assignment.start_img), self.get_image(assignment.end_img)
            start_idx, end_idx = images.index(start_img), images.index(end_img)
            for image in images[start_idx:end_idx+1]:
                if image.transect_id != assignment.transect_id:
                    image.transect_id = assignment.transect_id
                    modified = True
        return modified

    def fill_off_transect_gaps(self, max_gap=None):
        max_gap = max_gap or self.config.MAX_OFF_TRANSECT_IMAGE_GAP
        if len([image for image in self.images if image.transect_id is not None]) == 0:
            return
        last_on_transect_idx = None
        off_transect_gap_count = 0
        images = [image for image in sorted(self.images, key=lambda img: img.file_name) if image.coordinates_valid]
        for current_idx, image in enumerate(images):
            # Off-Transect
            if image.transect_id is None:
                if last_on_transect_idx is not None:
                    off_transect_gap_count += 1
                    if off_transect_gap_count > max_gap:
                        last_on_transect_idx = None
                        off_transect_gap_count = 0
            # On-Transect
            else:
                # Image moved from off->on transect
                if off_transect_gap_count > 0:
                    last_transect_id = images[last_on_transect_idx].transect_id
                    if image.transect_id == last_transect_id:
                        for gap_image in images[last_on_transect_idx:current_idx]:
                            gap_image.transect_id = last_transect_id
                off_transect_gap_count = 0
                last_on_transect_idx = current_idx

    def validate_transect_altitude_range(self):
        for image in self.images:
            if image.altitude_ft < self.config.MIN_ON_TRANSECT_ALTITUDE_FT \
                    or image.altitude_ft > self.config.MAX_ON_TRANSECT_ALTITUDE_FT:
                image.transect_id = None

    def load_inclinometer_data(self, force=False):
        inclinometer_data = []
        mkdir_if_not_exists(self.inclinometer_dir)
        for file in os.listdir(self.inclinometer_dir):
            if force is False and file in self.loaded_inclinometer_files:
                print(f"Inclinometer file '{file}' already loaded. Skipping...")
            else:
                print(f"Loading inclinometer data for '{file}'.")
                path = os.path.join(self.inclinometer_dir, file)
                inclinometer_data += self.inclinometer.load(path)
                self.loaded_inclinometer_files.append(file)
                self.has_unsaved_changes = True
        if len(inclinometer_data) == 0:
            print("No inclinometer data to load.")
        return inclinometer_data

    def load_and_apply_inclinometer_data(self, force=False):
        inclinometer_data = self.load_inclinometer_data(force)
        if len(inclinometer_data) == 0:
            return
        inclinometer_df = pd.DataFrame({"datetime": [record.datetime for record in inclinometer_data],
                                        "inclinometer_record": inclinometer_data})
        image_df = pd.DataFrame({"datetime": [image.datetime_obj for image in self.images], "image": self.images})
        inclinometer_df.set_index("datetime")
        image_df.set_index("datetime")
        merged_df = pd.merge_asof(left=image_df.sort_values("datetime"), right=inclinometer_df.sort_values("datetime"),
                                  on="datetime", direction="nearest", tolerance=pd.Timedelta(seconds=1))
        for index, row in merged_df.iterrows():
            image = row["image"]
            inclinometer_record = row["inclinometer_record"]
            if inclinometer_record is not np.nan:
                image.inclinometer_data = inclinometer_record

    def assign_cameras_to_images(self):
        if self.camera_system is None:
            print("Survey does not have a camera system loaded. Skipping camera-image assignment.")
            return
        for image in self.images:
            image.camera = self.camera_system.get_camera_from_image(image.file_path)

    def get_image(self, image_name):
        for image in self.images:
            if image.file_name.__contains__(image_name):
                return image

    def get_images_of_camera_type(self, camera):
        return [image for image in self.images if image.camera == camera]

    def get_predictions_in_temporal_zone(self):
        return [prediction for prediction in self.predictions if prediction.is_in_temporal_overlap]

    def get_predictions_near_temporal_zone(self):
        return [prediction for prediction in self.predictions if prediction.is_near_temporal_overlap]

    @staticmethod
    def get_predictions_within_polygon(polygon: geometry.Polygon, predictions: List[ObjectPredictionData]):
        return [prediction for prediction in predictions
                if geometry.Point(prediction.latitude, prediction.longitude).within(polygon)]

    def get_coordinate_bounds(self):
        min_coords, max_coords = self.get_min_max_coordinate_bounds()
        bounds = [min_coords, (max_coords[0], min_coords[1]), max_coords, (min_coords[0], max_coords[1])]
        return bounds

    def get_min_max_coordinate_bounds(self):
        images = [image for image in self.images if image.latitude != 0 and image.longitude != 0]
        min_lat = min(images, key=lambda image: image.latitude).latitude
        max_lat = max(images, key=lambda image: image.latitude).latitude
        min_long = min(images, key=lambda image: image.longitude).longitude
        max_long = max(images, key=lambda image: image.longitude).longitude

        return (min_lat, min_long), (max_lat, max_long)

    @staticmethod
    def are_consecutive_images(image1: SurveyImage, image2: SurveyImage):
        return image1.id == image2.id + 1 or image1.id == image2.id - 1
