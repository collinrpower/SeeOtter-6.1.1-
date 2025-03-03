from kivy.event import EventDispatcher


class PannableImageEventDispatcher(EventDispatcher):
    def __init__(self, **kwargs):
        self.register_event_type('on_image_changed')
        self.register_event_type('on_zoom_level_changed')
        super(PannableImageEventDispatcher, self).__init__(**kwargs)

    def image_changed(self, image=None):
        self.dispatch('on_image_changed', image)

    def zoom_level_changed(self, value):
        self.dispatch('on_zoom_level_changed', value)

    def on_image_changed(self, *args):
        pass

    def on_zoom_level_changed(self, *args):
        pass
