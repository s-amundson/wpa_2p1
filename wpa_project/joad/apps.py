from django.apps import AppConfig


class JoadConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'joad'

    def ready(self):
        import joad.signals
