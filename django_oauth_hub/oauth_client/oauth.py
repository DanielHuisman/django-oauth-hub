from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from authlib.integrations.django_client import OAuth
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import OAuthClient, OAuthClientToken

oauth = OAuth()
client_cache: dict[UUID, tuple[datetime, Any]] = {}


def get_oauth_client_by_id(oauth_client_id: UUID) -> tuple[OAuthClient, Any]:
    return get_oauth_client(oauth_client_id=oauth_client_id)


def get_oauth_client_by_slug(oauth_client_slug: str) -> tuple[OAuthClient, Any]:
    return get_oauth_client(oauth_client_slug=oauth_client_slug)


def get_oauth_client(oauth_client_id: UUID = None, oauth_client_slug: str = None) -> tuple[OAuthClient, Any]:
    # Obtain OAuth client definition
    if oauth_client_id:
        oauth_client = OAuthClient.objects.get(id=oauth_client_id)
    elif oauth_client_slug:
        oauth_client = OAuthClient.objects.get(slug=oauth_client_slug)
    else:
        raise ValidationError('No OAuth client ID or slug specified.', code='no_id_or_slug')

    # Check if OAuth client is cached and up-to-date
    cached = client_cache.get(oauth_client.id, None)
    print('Stored', cached[0] if cached else None, 'Current', oauth_client.updated_at, cached[0] >= oauth_client.updated_at if cached else False)
    if cached and cached[0] >= oauth_client.updated_at:
        return oauth_client, cached[1]

    scope = oauth_client.scope
    if oauth_client.openid_url and 'openid' not in scope:
        scope = f'openid,{scope}' if scope else 'openid'

    # Create OAuth client
    client = oauth.register(
        name=str(oauth_client.id),
        overwrite=True,
        client_id=oauth_client.client_id,
        client_secret=oauth_client.client_secret,
        request_token_url=oauth_client.request_token_url,
        access_token_url=oauth_client.access_token_url,
        authorize_url=oauth_client.authorize_url,
        server_metadata_url=oauth_client.openid_url if oauth_client.openid_url else None,
        client_kwargs={
            'scope': scope
        } if scope else {}
    )

    # Store OAuth client in cache
    client_cache[oauth_client.id] = (oauth_client.updated_at, client)

    return oauth_client, client


def store_oauth_client_token(oauth_client: OAuthClient, token) -> OAuthClientToken:
    print(token)

    if oauth_client.version == OAuthClient.Version.V1_0:
        # Attempt to find existing OAuth client token
        oauth_client_token = OAuthClientToken.objects.filter(
            client=oauth_client, oauth_token=token.get('oauth_token'), oauth_token_secret=token.get('oauth_token_secret')
        ).first()

        # Create OAuth client token if necessary
        if not oauth_client_token:
            oauth_client_token = OAuthClientToken(client=oauth_client, oauth_token=token.get('oauth_token'), oauth_token_secret=token.get('oauth_token_secret'))
            oauth_client_token.save()
    elif oauth_client.version == OAuthClient.Version.V2_0:
        # Attempt to find existing OAuth client token
        oauth_client_token: Optional[OAuthClientToken] = None
        if 'refresh_token' in token:
            oauth_client_token = OAuthClientToken.objects.filter(client=oauth_client, refresh_token=token.get('refresh_token')).first()

        # Create OAuth client token if necessary
        if not oauth_client_token:
            oauth_client_token = OAuthClientToken(client=oauth_client)

        # Update OAuth client token
        oauth_client_token.token_type = token.get('token_type')
        oauth_client_token.access_token = token.get('access_token')
        oauth_client_token.refresh_token = token.get('refresh_token')

        expires_at = token.get('expires_at')
        if type(expires_at) == int:
            expires_at = timezone.make_aware(datetime.fromtimestamp(expires_at))
        oauth_client_token.expires_at = expires_at

        oauth_client_token.save()

        return oauth_client_token
    else:
        raise NotImplementedError('Unknown OAuth client version.')
