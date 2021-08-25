from django.apps import AppConfig


class MembershipConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'membership'

    def ready(self):
        import membership.signals
