from kivymd.uix.label import MDLabel


class CardSectionHeader(MDLabel):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.theme_text_color = "Secondary"
        self.size_hint_y = None
        self.height = 50
