from kivy.event import EventDispatcher


class AnnotationBoxEventDispatcher(EventDispatcher):

    def __init__(self, **kwargs):
        self.register_event_type('on_annotation_clicked')
        self.register_event_type('on_annotation_header_clicked')
        super(AnnotationBoxEventDispatcher, self).__init__(**kwargs)

    def annotation_clicked(self, annotation):
        self.dispatch('on_annotation_clicked', annotation)

    def annotation_header_clicked(self, annotation):
        self.dispatch('on_annotation_header_clicked', annotation)

    def on_annotation_clicked(self, *args):
        pass

    def on_annotation_header_clicked(self, *args):
        pass
