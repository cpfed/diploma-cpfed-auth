from django.apps import AppConfig


class ContestConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'contest'

    def ready(self):
        import contest.signals
