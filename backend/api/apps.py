from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'
    verbose_name = 'Gestão do sistema'

    def ready(self):
        import api.signals  # noqa: F401
