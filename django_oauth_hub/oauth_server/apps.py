from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ServerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_oauth_hub.oauth_server'
    verbose_name = _('OAuth server')
