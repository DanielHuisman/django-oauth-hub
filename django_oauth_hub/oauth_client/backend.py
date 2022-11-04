from abc import abstractmethod, ABC
from datetime import datetime
from typing import Any
from uuid import UUID

from authlib.integrations.django_client import OAuth
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from .models import OAuthClient
from .providers import providers as default_providers, OAuthProvider


class BaseOAuthClientBackend(ABC):

    @abstractmethod
    def get_providers(self) -> dict[str, OAuthProvider]:
        raise NotImplementedError()

    @abstractmethod
    def get_client(self, oauth_client_id: UUID | str) -> tuple[OAuthClient, Any]:
        raise NotImplementedError()

    def validate_oauth_client(self, oauth_client: OAuthClient):
        pass


class DefaultOAuthClientBackend(BaseOAuthClientBackend):

    _oauth = OAuth()
    _client_cache: dict[UUID, tuple[datetime, Any]] = {}

    def get_providers(self) -> dict[str, OAuthProvider]:
        return default_providers

    def create_oauth_client(self, provider_slug: str, client_id: str = None, client_secret: str = None) -> OAuthClient:
        provider = self.get_providers().get(provider_slug)
        if not provider:
            raise ValidationError(_(f'OAuth provider "%(slug)s" was not found.'), code='not_found', params={'slug': provider_slug})

        oauth_client = OAuthClient(**provider, client_id=client_id, client_secret=client_secret)
        oauth_client.save()

        return oauth_client

    def get_client(self, oauth_client_id: UUID | str) -> tuple[OAuthClient, Any]:
        # Obtain OAuth client definition
        oauth_client = OAuthClient.objects.get(slug=oauth_client_id) if isinstance(oauth_client_id, str) else OAuthClient.objects.get(id=oauth_client_id)

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
