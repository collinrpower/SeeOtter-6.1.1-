from kivy.lang import Builder
from kivy.uix.gridlayout import GridLayout
from kivy.utils import get_color_from_hex
from kivymd.uix.behaviors import RoundedRectangularElevationBehavior
from kivymd.uix.card import MDCard
from Controller.see_otter_controller_base import SeeOtterControllerBase
from SurveyEntities.survey_image import SurveyImage
from View.Elements.rounded_card import RoundedCard

Builder.load_string("""
<CurrentImageInfoHeader>:
    size_hint: None, .85
    width: 300
    line_color: (.5, .5, .5)
    pos_hint: {"center_x": .5, "center_y": .5}
    
    MDStackLayout:
        size_hint: 1, 1
        MDLabel:
            size_hint: 1, .5
            id: image_label
            text: "Image:"
            font_size: 18
            bold: True
            halign: "center"
            theme_text_color: "Primary"
        MDLabel:
            size_hint: 1, .5
            id: prediction_label
            text: "Prediction:"
            bold: True
            font_size: 16
            halign: "center"
            theme_text_color: "Secondary"
""")


class CurrentImageInfoHeader(RoundedCard):

    controller = None

    def __init__(self, controller: SeeOtterControllerBase, **kwargs):
        self.controller = controller
        super().__init__(**kwargs)
        self.prediction_label = self.ids.prediction_label
        self.image_label = self.ids.image_label
        self.md_bg_color = get_color_from_hex("#444455")
        self.bind_events()

    def update_labels(self, instance, value):
        if self.controller.images and self.controller.current_image:
            self.image_label.text = f"Image: " + f"{self.controller.image_idx + 1}/{len(self.controller.images)} " \
                                                 f"({len(self.controller.survey.images)})"
        else:
            self.image_label.text = "Image: N/A"
        num_predictions = len(self.controller.current_image.predictions) \
            if isinstance(self.controller.current_image, SurveyImage) else 0
        num_filtered_predictions = len(self.controller.predictions) if self.controller.predictions else 0
        if num_filtered_predictions == 0:
            self.prediction_label.text = "Prediction: N/A"
        else:
            self.prediction_label.text = \
                f"Prediction: {self.controller.prediction_idx + 1}/{len(self.controller.predictions)}"
        if num_predictions > num_filtered_predictions:
            self.prediction_label.text += f" ({num_predictions})"

    def on_survey_changed(self, *args):
        if self.controller.survey is None:
            self.image_label.text = "No Survey Loaded"
            self.prediction_label.text = ""

    def bind_events(self):
        self.controller.bind(survey=self.on_survey_changed)
        self.controller.bind(images=self.update_labels)
        self.controller.bind(predictions=self.update_labels)
        self.controller.bind(current_image=self.update_labels)
        self.controller.bind(current_prediction=self.update_labels)
