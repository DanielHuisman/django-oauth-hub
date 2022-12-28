from django.utils import timezone

from .models import OAuthClient, OAuthClientToken


def delete_expired_oauth_client_tokens():
    """
    Delete expired OAuth client tokens. OAuth 1.0 tokens never expire, so none are deleted. OAuth 2.0 tokens are deleted if no refresh token is available.
    """

    # Delete expired OAuth 2.0 tokens without a refresh token.
    OAuthClientToken.objects.filter(
        expires_at__lte=timezone.now(),
        client__version=OAuthClient.Version.V2_0,
        refresh_token__isnull=True
    ).delete()
