from View.Elements.circle_icon_button import CircleIconButton


class DrawAnnotationMenuButton(CircleIconButton):
    def __init__(self, callback, **kwargs):
        super().__init__(callback, **kwargs)
        self.icon = "pencil"
        self.set_active(False)

    def set_active(self, active):
        if active:
            self.md_bg_color = self.theme_cls.primary_dark
        else:
            self.md_bg_color = [.5, .5, .5]
