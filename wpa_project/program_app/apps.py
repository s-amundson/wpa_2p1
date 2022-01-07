from django.apps import AppConfig


class ProgramConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'program_app'

    def ready(self):
        import program_app.signals
