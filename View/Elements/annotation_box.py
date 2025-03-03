from kivy.graphics import Rectangle, Color, StencilPush, StencilUse, StencilUnUse, StencilPop
from kivy.lang import Builder
from kivy.properties import ListProperty
from kivy.uix.behaviors import DragBehavior
from kivy.uix.widget import Widget

from Config.otter_checker_config import OtterCheckerConfig
from SurveyEntities.object_prediction_data import ObjectPredictionData, ValidationState
from Utilities.kivy_utilities import get_kivy_coordinates
from View.Events.annotation_box_event_dispatcher import AnnotationBoxEventDispatcher
from config import *

validation_to_annotation_color_dict = {
    ValidationState.UNVALIDATED: OtterCheckerConfig.instance().ANNOTATION_UNVALIDATED_COLOR,
    ValidationState.CORRECT: OtterCheckerConfig.instance().ANNOTATION_CORRECT_COLOR,
    ValidationState.INCORRECT: OtterCheckerConfig.instance().ANNOTATION_INCORRECT_COLOR,
    ValidationState.AMBIGUOUS: OtterCheckerConfig.instance().ANNOTATION_AMBIGUOUS_COLOR
}

Builder.load_string("""
<AnnotationRect>:
    id: annotation_rect
    prediction_label: prediction_label
    # drag_rectangle: self.x, self.y, self.width, self.height
    # drag_timeout: 10000000
    # drag_distance: 0
    
    # Box
    canvas:
        Color:
            rgba: self.line_color
        Line:
            width: 2
            rectangle: (self.x, self.y, self.width, self.height)
            
    # Header Tab   
    FloatLayout:
        canvas:
            Color:
                rgba: root.header_color
            Rectangle:
                pos: (root.x - 2, root.y + root.height + 2)
                size: (80, 20)
        Label:
            id: prediction_label
            text: ''
            color: (0, 0, 0, 1)
            pos: (root.x - 25, root.y + root.height - 40)
            size: (80, 20)
        """)


class AnnotationRect(Widget):

    line_color = ListProperty()
    header_color = ListProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.line_color = [0, 0, 0, 1]
        self.line_width = 2

    def highlight(self, highlight=True):
        if highlight:
            self.header_color = OtterCheckerConfig.instance().ANNOTATION_SELECTED_COLOR
            self.opacity = 1
        else:
            self.header_color = self.line_color
            self.opacity = .5

    def set_color(self, color):
        self.line_color = color
        self.header_color = color


class AnnotationBox(Widget):

    def __init__(self, prediction: ObjectPredictionData, resolution, **kwargs):
        super(AnnotationBox, self).__init__(**kwargs)
        self.prediction = prediction
        self.is_selected = False
        self.resolution = resolution
        self.norm_size, self.norm_pos = self.get_normalized_size_pos(prediction, resolution)
        self.rect = AnnotationRect()
        self.rect.set_color(self.get_validation_color())
        self.label = self.rect.ids.prediction_label
        self.event = AnnotationBoxEventDispatcher()
        self.add_widget(self.rect)

    @classmethod
    def get_normalized_size_pos(cls, prediction: ObjectPredictionData, resolution):
        size = (prediction.width, prediction.height)
        size = cls.normalized_img_size(size, resolution)
        pos = get_kivy_coordinates((prediction.xmin, prediction.ymax), resolution)
        pos = cls.normalized_img_size(pos, resolution)
        return size, pos

    def update_size_pos(self):
        self.size, self.pos = self.get_normalized_size_pos(self.prediction, self.resolution)

    def select(self):
        self.is_selected = True
        self.rect.highlight(True)
        self.label.bold = True

    def unselect(self):
        self.is_selected = False
        self.rect.highlight(False)
        self.label.bold = False

    def get_validation_color(self):
        return validation_to_annotation_color_dict[self.prediction.validation_state]

    def on_touch_down(self, touch):
        super().on_touch_down(touch)

    def on_touch_up(self, touch):
        if touch.button == "left":
            self.handle_left_mouse_up(touch)

    def handle_left_mouse_up(self, touch):
        mouse_held_time = touch.time_end - touch.time_start
        single_tap = mouse_held_time < .22
        if single_tap:
            if self.rect.collide_point(*touch.pos):
                if not self.is_pos_within_image(touch.pos):
                    return
                self.event.annotation_clicked(self)
            if self.rect.prediction_label.collide_point(*touch.pos):
                self.event.annotation_header_clicked(self)

    def is_pos_within_image(self, pos):
        return self.parent.collide_point(*pos)

    @staticmethod
    def normalized_img_size(val, resolution):
        return val[0] / resolution[0], val[1] / resolution[1]

    def set_label_text(self, text):
        self.rect.prediction_label.text = text

    def redraw(self, image, *args):
        self.rect.size = image.size[0] * self.norm_size[0], image.size[1] * self.norm_size[1]
        self.rect.pos = image.pos[0] + image.size[0] * self.norm_pos[0], image.pos[1] + image.size[1] * self.norm_pos[1]
        self.rect.set_color(self.get_validation_color())
        self.rect.highlight(self.is_selected)
        prediction_score = f"{self.prediction.score:.2f}"
        self.set_label_text(f"{self.prediction.category_name} {prediction_score}")
