from django.conf import settings as django_settings


class Settings:
    _settings = getattr(django_settings, 'DJANGO_OAUTH_HUB', {})

    USE_UUID = _settings.get('use_uuid', False)

    _client_settings = _settings.get('client', {})
    CLIENT_USE_EMAIL = _client_settings.get('use_email', True)
    CLIENT_USE_USERNAME = _client_settings.get('use_username', False)
    CLIENT_ALLOW_BLANK_EMAIL = _client_settings.get('allow_blank_email', False)
    CLIENT_ALLOW_BLANK_USERNAME = _client_settings.get('allow_blank_username', False)
    CLIENT_MAX_LENGTH_USERNAME = int(_client_settings.get('max_length_username', 150))

    _server_settings = _settings.get('server', {})
