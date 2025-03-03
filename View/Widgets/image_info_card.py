from Controller.see_otter_controller_base import SeeOtterControllerBase
from SurveyEntities.survey_image import SurveyImage
from Utilities.utilities import meters_to_feet
from View.Elements.property_row import PropertyRow
from View.Elements.stack_card import StackCard


class ImageInfoCard(StackCard):

    def __init__(self, controller: SeeOtterControllerBase, **kwargs):
        super().__init__("Image Info", **kwargs)
        self.size_hint_y = None
        self.height = 250
        self.controller = controller
        self.controller.bind(current_image=self.update_fields)
        self.build()

    def build(self):
        self.image_name = PropertyRow("Image")
        self.created_dttm = PropertyRow("Created Dttm")
        self.lattitude = PropertyRow("Latitude")
        self.longitude = PropertyRow("Longitude")
        self.altitude = PropertyRow("Altitude")
        self.iso = PropertyRow("ISO")
        self.fstop = PropertyRow("fStop")
        self.exposure = PropertyRow("Exposure")

        self.add(self.image_name)
        self.add(self.created_dttm)
        self.add(self.lattitude)
        self.add(self.longitude)
        self.add(self.altitude)
        self.add(self.iso)
        self.add(self.fstop)
        self.add(self.exposure)

    def clear_fields(self):
        self.image_name.value = ""
        self.created_dttm.value = ""
        self.lattitude.value = ""
        self.longitude.value = ""
        self.altitude.value = ""
        self.iso.value = ""
        self.fstop.value = ""
        self.exposure.value = ""

    def set_fields(self, image: SurveyImage):
        self.image_name.value = image.file_name
        self.created_dttm.value = image.datetime
        self.lattitude.value = str(image.latitude)
        self.longitude.value = str(image.longitude)
        self.altitude.value = f"{image.altitude}m ({image.altitude_ft}ft)"
        self.iso.value = image.metadata.iso
        self.fstop.value = "f/" + image.metadata.fstop
        self.exposure.value = image.metadata.exposure

    def update_fields(self, value, instance):
        image = self.controller.current_image
        if image and isinstance(self.controller.current_image, SurveyImage) :
            self.set_fields(image)
        else:
            self.clear_fields()
