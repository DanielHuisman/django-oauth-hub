from functools import cache
from typing import TYPE_CHECKING, Literal

from django.conf import settings as django_settings

from .util import import_attribute

if TYPE_CHECKING:
    from .oauth_client.backend import BaseOAuthClientBackend


class Settings:
    _settings = getattr(django_settings, 'DJANGO_OAUTH_HUB', {})

    USE_UUID = _settings.get('use_uuid', False)
    FORCE_HTTPS_URLS = _settings.get('force_https_urls', True)

    _client_settings = _settings.get('client', {})
    CLIENT_BACKEND = _client_settings.get('backend', 'django_oauth_hub.oauth_client.backend.DefaultOAuthClientBackend')
    CLIENT_USE_EMAIL = _client_settings.get('use_email', True)
    CLIENT_USE_USERNAME = _client_settings.get('use_username', False)
    CLIENT_ALLOW_BLANK_EMAIL = _client_settings.get('allow_blank_email', False)
    CLIENT_ALLOW_BLANK_USERNAME = _client_settings.get('allow_blank_username', False)
    CLIENT_MAX_LENGTH_USERNAME = int(_client_settings.get('max_length_username', 150))
    CLIENT_PROVIDERS = _client_settings.get('providers')
    CLIENT_REDIRECT_LOGIN = _client_settings.get('redirect_login', False)
    CLIENT_IS_CHOICE_DEFAULT = _client_settings.get('is_choice_default', False)

    _server_settings = _settings.get('server', {})

    @staticmethod
    @cache
    def get_client_backend() -> 'BaseOAuthClientBackend':
        backend_class = import_attribute(Settings.CLIENT_BACKEND)
        return backend_class()

    @staticmethod
    def get_client_is_choice_default() -> bool:
        return Settings.CLIENT_IS_CHOICE_DEFAULT
