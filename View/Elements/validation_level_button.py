from kivy.uix.button import Button


class ValidationLevelButton(Button):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = 44
