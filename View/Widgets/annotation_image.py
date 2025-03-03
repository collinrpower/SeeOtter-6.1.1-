import math
from functools import partial
from typing import List
from kivy.clock import Clock
from kivy.properties import BooleanProperty

from Config.otter_checker_config import OtterCheckerConfig
from Controller.see_otter_controller_base import SeeOtterControllerBase, OTTER_CHECKER_MODE
from SurveyEntities.object_prediction_data import ObjectPredictionData, ValidationState
from SurveyEntities.survey_image import SurveyImage
from View.Elements.annotation_box import AnnotationBox
from View.Elements.gridlines import GridLines
from View.Widgets.pannable_image import PannableImage


class AnnotationImage(PannableImage):

    annotations_visible = BooleanProperty(True)
    is_drawing_annotation = False
    draw_annotation_start_pos = None
    is_new_image = False

    def __init__(self, controller: SeeOtterControllerBase, **kwargs):
        self.controller = controller
        self.annotations = []
        super(AnnotationImage, self).__init__(**kwargs)
        self.gridlines = GridLines()
        self.bind_events()

    def on_current_image_changed(self, instance, value):
        self.is_new_image = True
        if isinstance(value, SurveyImage):
            path = value.file_path
        elif isinstance(value, str):
            path = value
        else:
            raise Exception(f"Invalid type. Value: {value}, Type: {type(value)}. Must be SurveyImage or String.")
        self.set_image(path)
        self.gridlines.initialize_grid()
        self.event.image_changed()

    def on_current_prediction_changed(self, instance, value):
        prediction: ObjectPredictionData = value
        if prediction:
            self.select_prediction(prediction)
            if self.is_new_image:
                self.is_new_image = False
                self.pan_to_prediction(prediction, duration=0)
            else:
                self.pan_to_prediction(prediction, duration= self.controller.config.NEXT_PREDICTION_TRANSITION_TIME)

    def on_predictions_changed(self, instance, value):
        predictions: List[ObjectPredictionData] = value
        self.create_annotation_boxes(predictions)

    def select_prediction(self, prediction: ObjectPredictionData):
        for annotation in self.annotations:
            if annotation.prediction == prediction:
                annotation.select()
            else:
                annotation.unselect()

    def pan_to_prediction(self, prediction: ObjectPredictionData, duration=0, delay=0):
        if not self.controller.predictions.__contains__(prediction):
            raise Exception("Error panning to prediction. Image does not contain given prediction.")
        if delay > 0:
            Clock.schedule_once(lambda pan: self.pan_to_standard_coords(
                prediction.pixel_pos, self.controller.config.DEFAULT_ZOOM, duration), delay)
        else:
            self.pan_to_standard_coords(prediction.pixel_pos, self.controller.config.DEFAULT_ZOOM, duration)

    def pan_to_selected_annotation(self, *args):
        if self.controller.current_prediction:
            self.pan_to_standard_coords(self.controller.current_prediction.pixel_pos,
                                        self.controller.config.DEFAULT_ZOOM,
                                        self.controller.config.NEXT_PREDICTION_TRANSITION_TIME)

    def create_annotation_boxes(self, predictions):
        self.clear_annotations()
        if predictions:
            for prediction in predictions:
                self.add_annotation(prediction)
        self.event.image_changed()

    def clear_annotations(self):
        for annotation in self.annotations:
            self.remove_annotation(annotation)
        self.annotations.clear()

    def get_annotation_from_prediction(self, prediction):
        for annotation in self.annotations:
            if annotation.prediction == prediction:
                return annotation

    def remove_annotation(self, annotation):
        self.remove_widget(annotation)

    def remove_selected_prediction(self):
        self.controller.remove_prediction(self.controller.current_image, self.controller.current_prediction)

    def add_annotation(self, prediction):
        annotation = AnnotationBox(prediction, self.resolution)
        self.bind_annotation_box_events(annotation)
        self.annotations.append(annotation)
        self.add_widget(annotation)

    def handle_left_mouse_click(self, touch):
        super().handle_left_mouse_click(touch)
        if self.controller.draw_mode and not self.current_image_is_background:
            self.start_draw_annotation(touch.pos)

    def handle_left_mouse_drag(self, touch):
        super().handle_left_mouse_drag(touch)

    def handle_left_mouse_release(self, touch):
        if self.is_drawing_annotation:
            self.stop_draw_annotation(touch.pos)

    def start_draw_annotation(self, position):
        self.is_drawing_annotation = True
        self.draw_annotation_start_pos = position

    def stop_draw_annotation(self, position):
        self.is_drawing_annotation = False
        self.draw_new_annotation(start_pos=self.draw_annotation_start_pos, end_pos=position)

    def draw_new_annotation(self, start_pos, end_pos):
        min_x = min(start_pos[0], end_pos[0])
        max_x = max(start_pos[0], end_pos[0])
        min_y = min(start_pos[1], end_pos[1])
        max_y = max(start_pos[1], end_pos[1])
        distance = math.dist((min_x, min_y), (max_x, max_y))

        if distance > 20:
            top_left = self.get_pixel_coordinates_at_pos((min_x, max_y))
            bottom_right = self.get_pixel_coordinates_at_pos((max_x, min_y))
            new_prediction = ObjectPredictionData(image_name=self.controller.current_image.file_name,
                                                  is_user_generated=True,
                                                  xmin=top_left[0], ymin=top_left[1],
                                                  xmax=bottom_right[0], ymax=bottom_right[1],
                                                  score=1.0,
                                                  validation_state=ValidationState.CORRECT,
                                                  category_name=self.controller.current_annotation_category,
                                                  category_id=self.controller.current_annotation_id)
            self.controller.add_prediction(self.controller.current_image, new_prediction)

    def annotation_clicked(self, dispatcher, annotation, *args):
        if not self.controller.draw_mode:
            self.controller.set_current_prediction(annotation.prediction)

    def annotation_header_clicked(self, dispatcher, annotation, *args):
        if not self.controller.draw_mode:
            self.controller.set_current_prediction(annotation.prediction)

    def redraw_overlay(self, image=None, *args):
        self.redraw_annotations()
        self.redraw_gridlines()

    def redraw_gridlines(self):
        if self.controller.gridlines_visible:
            self.remove_widget(self.gridlines)
            self.add_widget(self.gridlines)
            self.gridlines.redraw(self.image)

    def redraw_annotations(self, image=None, *args):
        for annotation in self.annotations:
            annotation.redraw(self.image)

    def zoom_changed(self):
        self.redraw_overlay()
        super(AnnotationImage, self).zoom_changed()

    def image_moved(self, touch, *args):
        self.redraw_overlay()

    def on_mode_changed(self, instance, value):
        if self.controller.default_mode:
            self.disable_panning = False
        if self.controller.draw_mode:
            self.disable_panning = True
        if self.controller.edit_mode:
            pass

    def on_gridlines_visible(self, *args):
        if self.controller.gridlines_visible:
            self.gridlines.initialize_grid()
            self.add_widget(self.gridlines)
            self.redraw_gridlines()
        else:
            self.remove_widget(self.gridlines)

    def on_annotations_visible(self, instance, value):
        opacity = 1 if self.annotations_visible else 0
        self.set_annotation_opacity(opacity)
        self.gridlines.opacity = opacity

    def set_annotation_opacity(self, opacity):
        for annotation in self.annotations:
            annotation.opacity = opacity

    def bind_annotation_box_events(self, annotation: AnnotationBox):
        annotation.event.bind(on_annotation_clicked=self.annotation_clicked)
        annotation.event.bind(on_annotation_header_clicked=self.annotation_header_clicked)

    def bind_events(self):
        super().bind_events()
        self.event.bind(on_image_changed=self.redraw_overlay)
        self.controller.bind(gridlines_visible=self.on_gridlines_visible)
        self.controller.bind(current_image=self.on_current_image_changed)
        self.controller.bind(predictions=self.on_predictions_changed)
        self.controller.bind(current_prediction=self.on_current_prediction_changed)
        self.controller.bind(mode=self.on_mode_changed)
