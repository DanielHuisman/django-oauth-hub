from abc import abstractmethod, ABC
from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from authlib.integrations.django_client import OAuth
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext as _

from ..settings import Settings
from .models import OAuthClient, OAuthClientToken
from .providers import providers as all_providers, OAuthProvider


class BaseOAuthClientBackend(ABC):

    @abstractmethod
    def get_providers(self) -> dict[str, OAuthProvider]:
        raise NotImplementedError()

    @abstractmethod
    def get_client(self, oauth_client_id: int | UUID = None, oauth_client_slug: str = None) -> tuple[OAuthClient, Any]:
        raise NotImplementedError()

    def get_client_by_id(self, oauth_client_id: int | UUID) -> tuple[OAuthClient, Any]:
        return self.get_client(oauth_client_id=oauth_client_id)

    def get_client_by_slug(self, oauth_client_slug: str) -> tuple[OAuthClient, Any]:
        return self.get_client(oauth_client_slug=oauth_client_slug)

    @abstractmethod
    def store_client_token(self, oauth_client: OAuthClient, token) -> OAuthClientToken:
        raise NotImplementedError()

    def validate_oauth_client(self, oauth_client: OAuthClient):
        pass


class DefaultOAuthClientBackend(BaseOAuthClientBackend):

    _oauth = OAuth()
    _client_cache: dict[UUID, tuple[datetime, Any]] = {}

    def get_providers(self) -> dict[str, OAuthProvider]:
        # Filter providers if necessary
        if Settings.CLIENT_PROVIDERS:
            return {slug: provider for slug, provider in all_providers.items() if slug in Settings.CLIENT_PROVIDERS}

        return all_providers

    def create_oauth_client(self, provider_slug: str, client_id: str = None, client_secret: str = None) -> OAuthClient:
        provider = self.get_providers().get(provider_slug)
        if not provider:
            raise ValidationError(_(f'OAuth provider "%(slug)s" was not found.'), code='not_found', params={'slug': provider_slug})

        oauth_client = OAuthClient(**provider, client_id=client_id, client_secret=client_secret)
        oauth_client.save()

        return oauth_client

    def get_client(self, oauth_client_id: int | UUID = None, oauth_client_slug: str = None) -> tuple[OAuthClient, Any]:
        # Obtain OAuth client definition
        if oauth_client_id:
            oauth_client = OAuthClient.objects.get(id=oauth_client_id)
        elif oauth_client_slug:
            oauth_client = OAuthClient.objects.get(slug=oauth_client_slug)
        else:
            raise ValidationError('No OAuth client ID or slug specified.', code='no_id_or_slug')

        # Check if OAuth client is cached and up-to-date
        cached = self._client_cache.get(oauth_client.id, None)
        # TODO: remove debug print
        print('Stored', cached[0] if cached else None, 'Current', oauth_client.updated_at, cached[0] >= oauth_client.updated_at if cached else False)
        if cached and cached[0] >= oauth_client.updated_at:
            return oauth_client, cached[1]

        # Create OAuth client
        client = self._oauth.register(
            name=str(oauth_client.id),
            overwrite=True,
            client_id=oauth_client.client_id,
            client_secret=oauth_client.client_secret,
            request_token_url=oauth_client.request_token_url,
            access_token_url=oauth_client.access_token_url,
            authorize_url=oauth_client.authorize_url,
            server_metadata_url=oauth_client.openid_url,
            client_kwargs={
                'scope': oauth_client.scope
            } if oauth_client.scope else {}
        )

        # Store OAuth client in cache
        self._client_cache[oauth_client.id] = (oauth_client.updated_at, client)

        return oauth_client, client

    # TODO: token typing
    def store_client_token(self, oauth_client: OAuthClient, token: Any) -> OAuthClientToken:
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
