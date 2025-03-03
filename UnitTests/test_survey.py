from unittest import TestCase
from Processing.survey_processing import *
from UnitTests import unit_test_helpers
from UnitTests.unit_test_helpers import test_image_paths, testing_surveys_dir, copy_test_images_to
from config import *


class TestSurvey(TestCase):
    survey_name = '_TestSurvey'

    @classmethod
    def setUpClass(cls):
        try:
            survey = unit_test_helpers.create_empty_survey(cls.survey_name)
            unit_test_helpers.copy_test_images_to(survey.images_dir)
            survey = Survey.load(cls.survey_name)
            survey.save()
        except Exception as ex:
            print("Error running setup class for test_survey.")
            raise ex

    @classmethod
    def tearDownClass(cls):
        unit_test_helpers.delete_all_test_surveys()

    def test_root_dir(self):
        survey = Survey.load(self.survey_name)
        expected = '..\\Surveys\\_TestSurvey'
        self.assertTrue(os.path.samefile(expected, survey.project_path),
                        msg=f"Expected: {expected}, Actual: {survey.project_path}")

    def test_default_images_dir(self):
        survey = Survey.load(self.survey_name)
        expected = '..\\Surveys\\_TestSurvey\\Images'
        self.assertTrue(os.path.samefile(expected, survey.images_dir),
                        msg=f"Expected: {expected}, Actual: {survey.images_dir}")

    def test_new(self):
        new_survey_name = "_TestNewSurvey"
        survey_path = Survey.get_default_survey_path(new_survey_name)
        if os.path.isdir(survey_path):
            shutil.rmtree(survey_path)
        new_survey = Survey.new(new_survey_name)
        self.assertTrue(len(new_survey.images) == 0)
        self.assertTrue(os.path.exists(os.path.join(survey_path, SURVEY_SAVE_FILE)))

    def test_new_fails_if_survey_exists(self):
        new_survey_name = "_TestNewSurvey"
        survey_path = Survey.get_default_survey_path(new_survey_name)
        if os.path.isdir(survey_path):
            shutil.rmtree(survey_path)
        Survey.new(new_survey_name)
        with self.assertRaises(Exception):
            Survey.new(new_survey_name)

    def test_new_overwrite_retains_images(self):
        new_survey_name = "_TestNewSurvey"
        survey_path = Survey.get_default_survey_path(new_survey_name)
        if os.path.isdir(survey_path):
            shutil.rmtree(survey_path)
        new_survey = Survey.new(new_survey_name)
        self.assertEqual(0, new_survey.num_images)
        unit_test_helpers.copy_test_images_to(new_survey.images_dir)
        new_survey.load_new_images()
        self.assertEqual(10, new_survey.num_images)
        newer_survey = Survey.new(new_survey_name, overwrite=True, force=True)
        self.assertEqual(10, newer_survey.num_images)

    def test_new_overwrite_overwrites_predictions(self):
        new_survey_name = "_TestNewSurvey"
        survey_path = Survey.get_default_survey_path(new_survey_name)
        if os.path.isdir(survey_path):
            shutil.rmtree(survey_path)
        new_survey = Survey.new(new_survey_name)
        self.assertEqual(0, new_survey.num_images)
        unit_test_helpers.copy_test_images_to(new_survey.images_dir)
        new_survey.load_new_images()
        self.assertEqual(10, new_survey.num_images)
        for image in new_survey.images:
            image.predictions.append(ObjectPredictionData())
        self.assertEqual(10, len(new_survey.predictions))
        newer_survey = Survey.new(new_survey_name, overwrite=True, force=True)
        self.assertEqual(0, len(newer_survey.predictions))

    def test_load_save_retains_prediction_values(self):
        new_survey_name = "_TestLoadSurvey"
        survey_path = Survey.get_default_survey_path(new_survey_name)
        if os.path.isdir(survey_path):
            shutil.rmtree(survey_path)
        new_survey = Survey.new(new_survey_name)
        self.assertEqual(0, new_survey.num_images)
        unit_test_helpers.copy_test_images_to(new_survey.images_dir)
        new_survey.load_new_images()
        self.assertEqual(10, new_survey.num_images)
        for image in new_survey.images:
            prediction = ObjectPredictionData()
            prediction.score = .75
            prediction.overlaps_image = "overlap"
            prediction.almost_overlaps_image = "almost"
            prediction.xmin = 40
            prediction.xmax = 45
            prediction.ymin = 50
            prediction.ymax = 55
            image.predictions.append(prediction)
        self.assertEqual(10, len(new_survey.predictions))
        new_survey.save()
        loaded_survey = Survey.load(new_survey_name)
        self.assertEqual(10, loaded_survey.num_images)
        self.assertEqual(10, len(loaded_survey.predictions))
        for prediction in loaded_survey.predictions:
            self.assertEqual(.75, prediction.score)
            self.assertEqual("overlap", prediction.overlaps_image)
            self.assertEqual("almost", prediction.almost_overlaps_image)
            self.assertEqual(40, prediction.xmin)
            self.assertEqual(45, prediction.xmax)
            self.assertEqual(50, prediction.ymin)
            self.assertEqual(55, prediction.ymax)

    def test_save_saves_camera_config(self):
        pass
        # todo: fix this
        # save_survey_name = "_TestSave"
        # survey = Survey(save_survey_name)
        # if exists(survey.camera_system_path):
        #     os.remove(survey.camera_system_path)
        # camera_system = DualCameraSystem(
        #     left_camera=CameraCalibration(camera_type=CAMERA_TYPE.WALDO_LEFT),
        #     right_camera=CameraCalibration(camera_type=CAMERA_TYPE.WALDO_RIGHT),
        #     percent_image_overlap=42,
        #     max_gps_y_offset_difference=43)
        # survey.camera_system = camera_system
        # self.assertFalse(os.path.exists(survey.camera_system_path))
        # survey.save()
        # self.assertTrue(os.path.exists(survey.camera_system_path))
        # loaded_survey = survey.load(save_survey_name)
        # self.assertTrue(loaded_survey.camera_system is not None)
        # self.assertIsInstance(loaded_survey.camera_system, DualCameraSystem)
        # self.assertEqual(CAMERA_TYPE.WALDO_LEFT, loaded_survey.camera_system.left_camera.camera_type)
        # self.assertEqual(CAMERA_TYPE.WALDO_RIGHT, loaded_survey.camera_system.right_camera.camera_type)
        # self.assertEqual(42, loaded_survey.camera_system.percent_image_overlap)
        # self.assertEqual(43, loaded_survey.camera_system.max_gps_y_offset_difference)

    def test_load_survey_from_survey_path(self):
        new_survey_name = "_TestSurveyLoad"
        survey_path = Survey.get_default_survey_path(new_survey_name)
        if os.path.isdir(survey_path):
            shutil.rmtree(survey_path)
        new_survey = Survey.new(new_survey_name)
        load_from_survey_dir_path = Survey.load(survey_path)
        self.assertEqual(new_survey_name, load_from_survey_dir_path.survey_name)

    def test_load_survey_from_survey_name(self):
        new_survey_name = "_TestSurveyLoad"
        survey_path = Survey.get_default_survey_path(new_survey_name)
        if os.path.isdir(survey_path):
            shutil.rmtree(survey_path)
        new_survey = Survey.new(new_survey_name)
        survey_from_survey_name = Survey.load(survey_path)
        self.assertEqual(new_survey_name, survey_from_survey_name.survey_name)

    def test_load_survey_from_save_file_path(self):
        new_survey_name = "_TestSurveyLoad"
        survey_path = Survey.get_default_survey_path(new_survey_name)
        if os.path.isdir(survey_path):
            shutil.rmtree(survey_path)
        new_survey = Survey.new(new_survey_name)
        load_from_survey_dir_path = Survey.load(survey_path)
        self.assertEqual(new_survey_name, load_from_survey_dir_path.survey_name)

    def test_load_image(self):
        pass
        # self.fail()

    def test_load_new_images(self):
        pass
        # self.fail()

    def test_load_camera_system(self):
        pass
        # self.fail()

    def test_autodetect_camera_system_type(self):
        pass
        # self.fail()

    def test_apply_camera_calibration_to_images(self):
        pass
        # self.fail()

    def test_get_image(self):
        pass
        # self.fail()

    def test_update_project_path(self):
        original_survey_name = "_TestUpdateProjectPathOriginal"
        new_survey_name = "_TestUpdateProjectPathNew"
        survey_path = Survey.get_default_survey_path(original_survey_name)
        new_survey_path = Survey.get_default_survey_path(new_survey_name)
        if os.path.isdir(survey_path):
            shutil.rmtree(survey_path)
        survey = Survey.new(original_survey_name)
        original_images_dir = survey.images_dir
        self.assertEqual(survey_path, survey.project_path)
        rmdir_if_exists(new_survey_path)
        os.rename(src=survey_path, dst=new_survey_path)
        survey.update_project_path(new_survey_path)
        self.assertEqual(new_survey_path, survey.project_path)
        self.assertEqual(original_images_dir, survey.images_dir)

    def test_update_images_dir(self):
        new_survey_name = "_TestUpdateImagesDir"
        survey_path = Survey.get_default_survey_path(new_survey_name)
        if os.path.isdir(survey_path):
            shutil.rmtree(survey_path)
        new_survey = Survey.new(new_survey_name)
        unit_test_helpers.copy_test_images_to(new_survey.images_dir)
        new_survey.load_new_images()
        self.assertEqual(10, len(new_survey.images))
        new_image_dir = new_survey.images_dir.replace(new_survey_name, TestSurvey.survey_name)
        new_survey.update_images_dir(images_dir=new_image_dir)
        self.assertEqual(10, len(new_survey.images))
        self.assertEqual(new_image_dir, new_survey.images_dir)
        self.assertFalse(new_survey.images_dir.__contains__(new_survey_name))
        self.assertTrue(new_survey.images_dir.__contains__(TestSurvey.survey_name))
        self.assertFalse(new_survey.images[0].file_path.__contains__(new_survey_name))
        self.assertTrue(new_survey.images[0].file_path.__contains__(TestSurvey.survey_name))

    def test_backup(self):
        new_survey_name = "_TestSurveyBackup"
        survey_path = Survey.get_default_survey_path(new_survey_name)
        if os.path.isdir(survey_path):
            shutil.rmtree(survey_path)
        new_survey = Survey.new(new_survey_name)
        shutil.copy2(test_image_paths[0], new_survey.images_dir)
        new_survey.load_new_images()
        self.assertEqual(1, len(new_survey.images))
        new_survey.images[0].predictions.append(ObjectPredictionData())
        self.assertEqual(1, len(new_survey.predictions))
        self.assertTrue(exists(new_survey.backup_dir))
        self.assertEqual(0, len(os.listdir(new_survey.backup_dir)))
        backup_dir = new_survey.backup()
        self.assertEqual(1, len(os.listdir(new_survey.backup_dir)))
        self.assertTrue(exists(join(backup_dir, ANNOTATIONS_DIR)))
        self.assertTrue(exists(join(backup_dir, TRANSECT_DIR)))
        self.assertTrue(exists(join(backup_dir, SURVEY_SAVE_FILE)))
        self.assertTrue(exists(join(backup_dir, PREDICTIONS_BACKUP_FILE)))
        for path in EXCLUDE_FROM_BACKUP:
            self.assertFalse(exists(join(backup_dir, path)))

    def test_backup_predictions(self):
        new_survey_name = "_TestSurveyBackupPredictions"
        survey_path = Survey.get_default_survey_path(new_survey_name)
        if os.path.isdir(survey_path):
            shutil.rmtree(survey_path)
        new_survey = Survey.new(new_survey_name)
        unit_test_helpers.copy_test_images_to(new_survey.images_dir)
        new_survey.load_new_images()
        for i, image in enumerate(new_survey.images):
            new_prediction = ObjectPredictionData(image_name=image.file_name)
            new_prediction.category_id = i
            new_prediction.xmin, new_prediction.xmax = 1, 2
            new_prediction.ymin, new_prediction.ymax = 3, 4
            new_prediction.score = .69
            new_prediction.validation_state = ValidationState.CORRECT
            new_prediction2 = copy.deepcopy(new_prediction)
            new_prediction2.score = 4.20
            new_prediction2.validation_state = ValidationState.AMBIGUOUS
            image.predictions.append(new_prediction)
            image.predictions.append(new_prediction2)
        original_images = copy.deepcopy(new_survey.images)
        new_survey.backup_predictions()
        self.assertTrue(exists(new_survey.get_relative_path(PREDICTIONS_BACKUP_FILE)))
        self.assertEqual(20, len(new_survey.predictions))
        new_survey.clear_all_predictions()
        self.assertEqual(0, len(new_survey.predictions))
        new_survey.images[0].predictions.append(ObjectPredictionData())
        new_survey.load_predictions_from_backup()
        self.assertEqual(20, len(new_survey.predictions))
        new_images = new_survey.images
        for i in range(10):
            new = new_images[i]
            original = original_images[i]
            self.assertEqual(original.file_name, new.file_name)
            self.assertEqual(original.file_path, new.file_path)
            self.assertEqual(len(original.predictions), len(new.predictions))
            new_prediction = new.predictions[0]
            original_prediction = original.predictions[0]
            self.assertEqual(original_prediction.score, new_prediction.score)
            self.assertEqual(original_prediction.xmin, new_prediction.xmin)
            self.assertEqual(original_prediction.xmax, new_prediction.xmax)
            self.assertEqual(original_prediction.ymin, new_prediction.ymin)
            self.assertEqual(original_prediction.ymax, new_prediction.ymax)
            self.assertEqual(original_prediction.validation_state, new_prediction.validation_state)
            self.assertEqual(original_prediction.score, new_prediction.score)

    def test_upgrade_project_version(self):
        survey_src_name = "V2_Survey"
        new_survey_name = "_TestSurveyUpgradeProjectVersion"
        survey_path = Survey.get_default_survey_path(new_survey_name)
        survey_src_path = join(testing_surveys_dir, survey_src_name)
        if os.path.isdir(survey_path):
            shutil.rmtree(survey_path)
        shutil.copytree(survey_src_path, survey_path)
        survey_img_path = join(survey_path, IMAGE_DIR)
        copy_test_images_to(survey_img_path)

        old_survey = Survey.load(survey=new_survey_name, quick_load=True, skip_upgrade=True)
        self.assertTrue(old_survey.version.major == 2)
        Survey.upgrade_project_version(survey_name=new_survey_name, force=True)
        new_survey = Survey.load(survey=new_survey_name)
        self.assertEqual(version, new_survey.version)

        # Test Image/Prediction Counts
        self.assertEqual(9, len(new_survey.images))
        self.assertEqual(1, len(new_survey.excluded_images))
        self.assertEqual(5, len(new_survey.predictions))
        self.assertEqual(9, len(new_survey.processed_images))
        self.assertEqual(0, len(new_survey.unprocessed_images))
        self.assertEqual(5, len(new_survey.validated_predictions))
        self.assertEqual(1, len(new_survey.validated_correct_predictions))
        self.assertEqual(2, len(new_survey.validated_incorrect_predictions))
        self.assertEqual(2, len(new_survey.validated_ambiguous_predictions))

        # Test New Fields
        prediction = new_survey.predictions[0]
        self.assertEqual("", prediction.validated_by)
        self.assertEqual(None, prediction.validated_dttm)
        self.assertTrue(prediction.created_by.__contains__("SeeOtter"))
        self.assertIsNotNone(prediction.original_prediction_data)
        self.assertIsNone(new_survey.inclinometer)
        self.assertTrue(exists(new_survey.inclinometer_dir))

    def test_fill_off_transect_gaps(self):
        new_survey_name = "_TestFillOffTransectGaps"
        survey_path = Survey.get_default_survey_path(new_survey_name)
        if os.path.isdir(survey_path):
            shutil.rmtree(survey_path)
        survey = Survey.new(new_survey_name)
        unit_test_helpers.copy_test_images_to(survey.images_dir)
        survey.load_new_images()
        images = sorted(survey.images, key=lambda img: img.file_name)

        images[1].transect_id = 1
        images[4].transect_id = 2
        images[5].transect_id = 3
        images[8].transect_id = 3

        survey.fill_off_transect_gaps()

        [print(f"img: {image.file_name} transect: {image.transect_id}") for image in images]

        self.assertEqual(None, images[0].transect_id)
        self.assertEqual(1, images[1].transect_id)
        self.assertEqual(None, images[2].transect_id)
        self.assertEqual(None, images[3].transect_id)
        self.assertEqual(2, images[4].transect_id)
        self.assertEqual(3, images[5].transect_id)
        self.assertEqual(3, images[6].transect_id)
        self.assertEqual(3, images[7].transect_id)
        self.assertEqual(3, images[8].transect_id)
        self.assertEqual(None, images[9].transect_id)

        for image in images:
            image.transect_id = None

        images[0].transect_id = 1
        images[9].transect_id = 1

        survey.fill_off_transect_gaps(max_gap=7)

        self.assertEqual(1, images[0].transect_id)
        self.assertEqual(None, images[1].transect_id)
        self.assertEqual(None, images[2].transect_id)
        self.assertEqual(None, images[3].transect_id)
        self.assertEqual(None, images[4].transect_id)
        self.assertEqual(None, images[5].transect_id)
        self.assertEqual(None, images[6].transect_id)
        self.assertEqual(None, images[7].transect_id)
        self.assertEqual(None, images[8].transect_id)
        self.assertEqual(1, images[9].transect_id)

        survey.fill_off_transect_gaps(max_gap=8)

        for image in images:
            self.assertEqual(1, image.transect_id)

    def test_apply_manual_transect_assignments(self):
        new_survey_name = "_TestApplyManualTransectAssignments"
        survey_path = Survey.get_default_survey_path(new_survey_name)
        if os.path.isdir(survey_path):
            shutil.rmtree(survey_path)
        survey = Survey.new(new_survey_name)
        unit_test_helpers.copy_test_images_to(survey.images_dir)
        shutil.copy2(src="TestingResources/Files/transect_assignment.csv",
                     dst=survey.transect_assignment_file_path)
        survey = Survey.load(new_survey_name)

        images = sorted(survey.images, key=lambda img: img.file_name)

        [print(f"img: {image.file_name} transect: {image.transect_id}") for image in images]

        self.assertEqual(None, images[0].transect_id)
        self.assertEqual(None, images[1].transect_id)
        self.assertEqual(1, images[2].transect_id)
        self.assertEqual(1, images[3].transect_id)
        self.assertEqual(None, images[4].transect_id)

        self.assertEqual(None, images[5].transect_id)
        self.assertEqual(1, images[6].transect_id)
        self.assertEqual(2, images[7].transect_id)
        self.assertEqual(2, images[8].transect_id)
        self.assertEqual(2, images[9].transect_id)
