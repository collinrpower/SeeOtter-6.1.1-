import asyncio
import subprocess
import threading
from functools import partial
from os.path import realpath
from pathlib import Path
from tkinter import filedialog
from typing import List
from kivy.clock import Clock
from kivy.event import EventDispatcher
from kivy.properties import ObjectProperty, StringProperty
from tqdm import tqdm
import tkinter as tk
from Controller.see_otter_controller_base import SeeOtterControllerBase, SeeOtterState
from DataGenerators.AnnotationFormats.yolo_annotation import YoloAnnotation
from DataGenerators.annotation_generator import AnnotationGenerator
from DataGenerators.kml_map_generator import KmlMapGenerator
from DataGenerators.results_generator import ResultsGenerator
from Processing.predict import run_image_detection
from Processing.survey_processing import pre_processing, post_processing, get_images_to_preprocess, \
    clone_filtered_survey, vote_ambiguous_validations
from SurveyEntities.object_prediction_data import ValidationState
from SurveyEntities.survey import Survey
from SurveyEntities.waldo_survey import WaldoSurvey
from Utilities.custom_exceptions import SurveyVersionException, ImageDirNotFoundException
from Utilities.exit_flag import ExitFlag
from Utilities.tqdm_plus import TqdmPlus
from Utilities.utilities import PromptUserNotification
from config import AMBIGUOUS_VOTE_DIR


class SurveyCommandController(EventDispatcher):

    command_progress = ObjectProperty(allownone=True, force_dispatch=True)
    current_command_name = StringProperty(allownone=True)

    def __init__(self, controller: SeeOtterControllerBase, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.controller = controller
        self.exit_flag = ExitFlag()

    @property
    def survey(self):
        return self.controller.survey

    def raise_exit_flag(self, *args, **kwargs):
        print("Exit flag raised")
        self.exit_flag.request_exit()

    def reset_exit_flag(self):
        self.exit_flag.reset()

    def show_operation_cancelled_by_user_snackbar(self, *args, **kwargs):
        self.controller.set_snackbar_message("Operation cancelled by user.")

    def set_current_command(self, command_name):
        def set_current_command_task(command_name, command_controller, *args):
            command_controller.current_command_name = command_name
        Clock.schedule_once(partial(set_current_command_task, command_name, self))

    def set_command_progress(self, progress):
        def set_command_progress_task(progress, command_controller, *args):
            command_controller.command_progress = progress
        Clock.schedule_once(partial(set_command_progress_task, progress, self))

    def run_command(self, command, action_name, refresh=True, *args, **kwargs):

        def command_task(command_controller: SurveyCommandController, command, action_name, refresh):
            controller = command_controller.controller
            try:
                controller.state = SeeOtterState.RUNNING_COMMAND
                command_controller.set_current_command(action_name)
                Clock.schedule_once(partial(controller.set_snackbar_message, f"Running: {action_name}"))
                command()
                Clock.schedule_once(partial(controller.set_snackbar_message, f"Completed: {action_name}"))
                if refresh:
                    Clock.schedule_once(controller.refresh_survey)
            except Exception as ex:
                message = f"Error running command ({action_name}): " + str(ex)
                Clock.schedule_once(partial(controller.set_snackbar_message, message))
            finally:
                Clock.schedule_once(controller.set_idle_state)
                command_controller.set_current_command("")

        action_name = action_name or "command"
        command_thread = threading.Thread(target=command_task, args=(self, command, action_name, refresh,))
        command_thread.start()

    def run_command_on_user_prompt(self, prompt, command, action_name, refresh=True):

        def run_command_on_user_prompt_task(controller: SurveyCommandController, command, action_name):
            response = PromptUserNotification.wait_for_response()
            if response is True:
                controller.run_command(command=command, action_name=action_name, refresh=refresh)
            else:
                Clock.schedule_once(controller.show_operation_cancelled_by_user_snackbar)

        PromptUserNotification.raise_prompt(prompt)
        task = threading.Thread(target=run_command_on_user_prompt_task, args=(self, command, action_name,))
        task.start()

    def load_survey(self, survey, img_dir=None, *args):

        def load_survey_task(controller: SeeOtterControllerBase,
                             command_controller: SurveyCommandController,
                             img_dir=None):
            controller.state = SeeOtterState.LOADING_SURVEY
            Clock.schedule_once(partial(controller.set_program_status_message, f"Loading survey: {survey}"))
            if isinstance(survey, Survey):
                controller.set_survey(survey, gui_threadsafe=True)
            else:
                try:
                    loaded_survey = Survey.load(survey=survey, images_dir=img_dir)
                    controller.set_survey(loaded_survey, gui_threadsafe=True)
                except SurveyVersionException as sve:
                    controller.set_snackbar_message("Warning: Survey version out of date. Attempting to update "
                                                    "project...")
                    survey_path = Path(survey).parent
                    Survey.upgrade_project_version(survey_path=survey_path, survey_type=WaldoSurvey, force=True)
                    controller.survey = Survey.load(survey)
                except ImageDirNotFoundException as idnfe:
                    PromptUserNotification.raise_prompt(f"{idnfe}\n\nLocate and "
                                                        f"update images folder?")
                    response = PromptUserNotification.wait_for_response()
                    if response:
                        Clock.schedule_once(partial(command_controller.locate_img_dir_and_load_survey, survey))
                    raise idnfe

            Clock.schedule_once(partial(controller.set_snackbar_message, f"Loaded survey: {survey}"), .2)

        self.run_command(command=partial(load_survey_task, self.controller, self, img_dir), action_name="Load Survey")

    def locate_img_dir_and_load_survey(self, survey, *args):
        root = tk.Tk()
        root.withdraw()
        img_dir = filedialog.askdirectory(title="Select Image Dir")
        self.load_survey(survey, img_dir)

    def run_pre_processing(self, *args, **kwargs):
        images_to_preprocess = get_images_to_preprocess(self.survey)
        if images_to_preprocess == 0:
            self.controller.set_snackbar_message("Operation cancelled: All images have been pre-processed")
        self.run_command(command=partial(pre_processing, self.survey, force=False), action_name="Run Pre-Processing",
                         refresh=True)

    def force_run_pre_processing(self, *args, **kwargs):
        prompt = f"You are about to force run pre-processing for all images regardless of whether they've already " \
                 f"been pre-processed and may take a while.\n\n" \
                 f"Are you sure you want to continue?"
        self.run_command_on_user_prompt(prompt=prompt,
                                        command=partial(pre_processing, self.survey, force=True),
                                        action_name="Force Run Pre-Processing",
                                        refresh=True)

    def run_post_processing(self, *args, **kwargs):
        self.run_command(command=partial(post_processing, self.survey), action_name="Run Post-Processing",
                         refresh=True)

    def reset_all_predictions(self, *args, **kwargs):
        if len(self.survey.predictions) < 0:
            self.controller.set_snackbar_message("Operation cancelled: Survey contains no predictions")
            return

        prompt = f"You are about to reset all {len(self.survey.predictions)} predictions\n\n" \
                 f"Are you sure you want to continue?"
        self.run_command_on_user_prompt(prompt=prompt,
                                        command=self.survey.clear_all_predictions,
                                        action_name="Reset all Predictions",
                                        refresh=True)

    def reset_all_validations(self, *args, **kwargs):
        if len(self.survey.validated_predictions) < 0:
            self.controller.set_snackbar_message("Operation cancelled: Survey contains no validations")
        else:
            prompt = f"You are about to reset all {len(self.survey.validated_predictions)} validations\n\n" \
                     f"Are you sure you want to continue?"
            self.run_command_on_user_prompt(prompt=prompt,
                                            command=self.survey.clear_all_validations,
                                            action_name="Reset all Validations",
                                            refresh=True)

    def reload_inclinometer_data(self, *args, **kwargs):

        def reload_inclinometer_data_task(survey: Survey):
            survey.loaded_inclinometer_files = []
            survey.load_and_apply_inclinometer_data()

        self.run_command(command=partial(reload_inclinometer_data_task, self.survey),
                         action_name="Reload Inclinometer Data")

    def reload_image_metadata(self, *args, **kwargs):

        def reload_image_metadata_task(survey: Survey):
            for image in tqdm(survey.images):
                image.reload_metadata()

        self.run_command(command=partial(reload_image_metadata_task, self.survey), action_name="Reload Image Metadata")

    def reload_transects(self, *args, **kwargs):

        def reload_transects_task(survey: Survey):
            survey.clear_transects()
            survey.load_transects()

        self.run_command(command=partial(reload_transects_task, self.survey), action_name="Reload Transects")

    def create_survey_from_waldo_data(self, path, *args, **kwargs):

        def create_survey_from_waldo_data_task(path, controller, command_controller):
            survey = WaldoSurvey.create_from_waldo_survey(path)
            if controller.survey and controller.has_unsaved_changes:
                PromptUserNotification.raise_prompt("You have unsaved changes\n"
                                                    "Would you like to save and load new survey?")
                response = PromptUserNotification.wait_for_response()
                if response is False:
                    return
                else:
                    controller.survey.save()
            command_controller.load_survey(survey)

        self.run_command(partial(create_survey_from_waldo_data_task, path, self.controller, self),
                         action_name="Create survey from Waldo Data")

    def create_new_survey(self, survey_name, survey_path, images_dir, survey_type):

        def create_new_survey_task(controller: SeeOtterControllerBase, command_controller: SurveyCommandController,
                                   survey_name, survey_path, images_dir, survey_type):
            survey = survey_type.new(survey_name=survey_name, survey_path=survey_path, images_dir=images_dir)
            Clock.schedule_once(partial(
                controller.set_snackbar_message, f"Successfully created new survey: {survey.survey_name}")
            )
            if controller.survey and controller.has_unsaved_changes:
                PromptUserNotification.raise_prompt("You have unsaved changes\n"
                                                    "Would you like to save and load new survey?")
                response = PromptUserNotification.wait_for_response()
                if response is False:
                    return
                else:
                    controller.survey.save()
            command_controller.load_survey(survey)

        self.run_command(command=partial(create_new_survey_task, self.controller, self, survey_name,
                                         survey_path, images_dir, survey_type), action_name="Create new survey")

    def create_backup(self, *args, **kwargs):
        try:
            self.survey.backup()
            self.controller.snackbar_message = "Created backup"
        except Exception as ex:
            self.controller.snackbar_message = f"Error creating backup: {ex}"

    def run_processing(self, *args, **kwargs):

        def processing_task(command_controller: SurveyCommandController):
            controller = command_controller.controller
            command_controller.reset_exit_flag()
            try:
                controller.state = SeeOtterState.PRE_PROCESSING
                pre_processing(controller.survey)
                controller.state = SeeOtterState.RUNNING_IMAGE_DETECTION
                run_image_detection(controller.survey, progress_callback=command_controller.set_command_progress,
                                    exit_flag=command_controller.exit_flag)
                controller.state = SeeOtterState.POST_PROCESSING
                post_processing(controller.survey)
                controller.state = SeeOtterState.SAVING_SURVEY
                controller.survey.save()
            except Exception as ex:
                print(f"Error while processing: {ex}")
            finally:
                controller.set_idle_state()
                command_controller.reset_exit_flag()

        if self.controller.state == SeeOtterState.SURVEY_LOADED:
            self.run_command(command=partial(processing_task, self,), action_name="Run Processing")
        else:
            print(f"Warning: Cannot run processing while program state is '{self.controller.state.name}'")

    def generate_annotations(self, *args):

        def generate_annotations_task(survey: Survey):
            annotation_generator = AnnotationGenerator(survey, YoloAnnotation())
            annotation_generator.generate()
            subprocess.Popen(f'explorer /select,"{realpath(annotation_generator.output_dir)}"')

        self.run_command(command=partial(generate_annotations_task, self.survey), action_name="Generate Annotations")

    def clone_filtered_survey(self, cloned_survey_path, validation_types: List[ValidationState]):
        self.run_command(command=partial(clone_filtered_survey, self.survey, include_validation_types=validation_types,
                                         out_dir_name=cloned_survey_path), action_name="Clone filtered survey")

    def vote_ambiguous_validations(self, *args):
        self.run_command(command=partial(vote_ambiguous_validations, self.survey),
                         action_name="Vote ambiguous validations")

    def generate_results(self, *args):

        def generate_results_task(survey, controller):
            Clock.schedule_once(partial(controller.set_program_status_message, f"Generating Results, this may take "
                                                                               f"several minutes..."))
            post_processing(survey)
            KmlMapGenerator.survey_transect_map(survey, performance_mode=True).\
                save(survey.transect_map_file_path_kml)

            # Generate Results
            ResultsGenerator(survey).all_otters().save('results_all_otters.csv')
            ResultsGenerator(survey).distinct_otters().save('results_distinct_otters.csv')
            ResultsGenerator(survey).all_predictions().save('results_all_predictions.csv')
            ResultsGenerator(survey).distinct_otter_count_by_image().\
                save('results_distinct_otter_count_by_image.csv')
            ResultsGenerator(survey).validated_predictions().save('validated_predictions.csv')
            ResultsGenerator(survey).survey_overview().save('survey_overview.csv')
            subprocess.Popen(f'explorer /select,"{realpath(survey.get_relative_path(AMBIGUOUS_VOTE_DIR))}"')

        self.run_command(command=partial(generate_results_task, self.survey, self.controller),
                         action_name="Generate Results")
