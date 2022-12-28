from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ClientConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_oauth_hub.oauth_client'
    verbose_name = _('OAuth client')
