from django.core.exceptions import ValidationError

from django_oauth_hub.oauth_client.backend import DefaultOAuthClientBackend
from django_oauth_hub.oauth_client.models import OAuthClient


class OAuthClientBackend(DefaultOAuthClientBackend):

    def validate_oauth_client(self, oauth_client: OAuthClient):
        if oauth_client.openid_url and oauth_client.openid_url.startswith('http://'):
            raise ValidationError('OpenID Connect Discovery URL must use HTTPS instead of HTTP.')
