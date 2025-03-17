from django.apps import AppConfig


class MaxiappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Maxiapp'


class MyAppConfig(AppConfig):
    name = 'Maxiapp'

    def ready(self):
        import Maxiapp.signals