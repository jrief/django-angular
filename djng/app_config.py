from django.apps import AppConfig


class DjangoAngularConfig(AppConfig):
    name = 'djng'

    def ready(self):
        from django.forms.widgets import RadioSelect

        def id_for_label(self, id_, index=None):
            if id_ and index and self.add_id_index:
                id_ = '%s_%s' % (id_, index)
            return id_

        RadioSelect.id_for_label = id_for_label
