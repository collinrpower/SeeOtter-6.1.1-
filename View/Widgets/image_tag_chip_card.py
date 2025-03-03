from typing import List

from kivymd.uix.stacklayout import MDStackLayout

from SurveyEntities.image_tag import ImageTag
from SurveyEntities.survey_image import SurveyImage
from View.Elements.card import Card
from View.Elements.image_tag_chip import ImageTagChip
from View.Events.chip_tag_card_event_dispatcher import ChipTagCardEventDispatcher


class ImageTagChipCard(Card):

    def __init__(self, tags: List[ImageTagChip], on_tag_pressed, **kwargs):
        super().__init__("Image Tags", **kwargs)
        self.tag_chips = []
        self.on_tag_pressed = on_tag_pressed
        self.layout = MDStackLayout(size_hint=(1, 1), spacing=5)
        [self.add_tag(tag) for tag in tags]
        self.add_widget(self.layout)

    def update_tag_state(self, instance, survey_image):
        if not isinstance(survey_image, SurveyImage):
            return
        for tag_chip in self.tag_chips:
            tag = tag_chip.tag
            matching_tag = survey_image.tags.get_matching_tag(tag)
            if matching_tag and matching_tag.state is True:
                tag_chip.set_tag_state(True)
            else:
                tag_chip.set_tag_state(False)

    def add_tag(self, tag):
        self.tag_chips.append(tag)
        self.layout.add_widget(tag)
        tag.event.bind(on_tag_pressed=self.on_tag_pressed)

    def on_touch_down(self, touch):
        super().on_touch_down(touch)

