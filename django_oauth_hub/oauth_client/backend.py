from abc import abstractmethod, ABC
from datetime import datetime
from functools import cache
from typing import Any, TYPE_CHECKING
from uuid import UUID

from authlib.integrations.django_client import OAuth

from ..settings import Settings
from ..util import import_attribute

if TYPE_CHECKING:
    from .models import OAuthClient


@cache
def get_client_backend() -> 'BaseOAuthClientBackend':
    backend_class = import_attribute(Settings.CLIENT_BACKEND, type(BaseOAuthClientBackend))
    return backend_class()


class BaseOAuthClientBackend(ABC):

    @abstractmethod
    def get_client(self, oauth_client_id: UUID | str) -> tuple[OAuthClient, Any]:
        raise NotImplementedError()

    def validate_oauth_client(self, oauth_client: 'OAuthClient'):
        pass


class DefaultOAuthClientBackend(BaseOAuthClientBackend):

    _oauth = OAuth()
    _client_cache: dict[UUID, tuple[datetime, Any]] = {}

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
