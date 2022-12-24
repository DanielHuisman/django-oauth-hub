from abc import abstractmethod, ABC
from datetime import datetime
from typing import Any, Optional, TypedDict
from uuid import UUID

from authlib.integrations.django_client import OAuth
from django.contrib import auth
from django.contrib.auth.base_user import AbstractBaseUser
from django.core.exceptions import ValidationError, ImproperlyConfigured
from django.http import HttpRequest
from django.utils import timezone
from django.utils.translation import gettext as _

from ..settings import Settings
from ..util import get_by_key_string
from .models import OAuthClient, OAuthClientToken, OAuthClientConnection
from .providers import providers as all_providers, OAuthProvider


class UserInfo(TypedDict):
    id: str
    email: Optional[str]
    username: Optional[str]
    data: dict


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
    def store_client_token(self, oauth_client: OAuthClient, token: Any) -> OAuthClientToken:
        raise NotImplementedError()

    @abstractmethod
    def get_user_info_data(self, oauth_client: OAuthClient, client: Any, token, request: HttpRequest) -> dict:
        raise NotImplementedError()

    @abstractmethod
    def get_user_info(self, oauth_client: OAuthClient, data: dict) -> UserInfo:
        raise NotImplementedError()

    @abstractmethod
    def connect(self, oauth_client: OAuthClient, token: OAuthClientToken, user_info: UserInfo, request: HttpRequest) -> OAuthClientConnection:
        raise NotImplementedError()

    @abstractmethod
    def validate_existing_connect(self, oauth_client: OAuthClient, user_info: UserInfo, request: HttpRequest, connection: OAuthClientConnection):
        raise NotImplementedError()

    @abstractmethod
    def validate_new_connect(self, oauth_client: OAuthClient, user_info: UserInfo, request: HttpRequest):
        raise NotImplementedError()


    @abstractmethod
    def create_connection(self, oauth_client: OAuthClient, token: OAuthClientToken, user_info: UserInfo, user: AbstractBaseUser) -> OAuthClientConnection:
        raise NotImplementedError()

    @abstractmethod
    def update_connection(self, connection: OAuthClientConnection, token: OAuthClientToken, user_info: UserInfo,  user: AbstractBaseUser):
        raise NotImplementedError()

    @abstractmethod
    def create_user(self, user_info: UserInfo) -> AbstractBaseUser:
        raise NotImplementedError()

    @abstractmethod
    def update_user(self, user: AbstractBaseUser, user_info: UserInfo):
        raise NotImplementedError()

    @abstractmethod
    def disconnect(self, oauth_client: OAuthClient, connection: OAuthClientConnection):
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

    def get_user_info_data(self, oauth_client: OAuthClient, client: Any, token, request: HttpRequest) -> dict:
        # Check if user info is present in the OAuth token
        if 'userinfo' in token:
            return token.get('userinfo')

        if oauth_client.user_api_url:
            # Fetch user info from API
            user_info = client.get(oauth_client.user_api_url, request=request)

            # Obtain nested user info from API response
            if oauth_client.user_api_key:
                user_info = get_by_key_string(user_info, oauth_client.user_api_key)

            return user_info
        elif oauth_client.openid_url:
            # Fetch user info from OpenID Connect
            return client.userinfo(token)
        else:
            raise ImproperlyConfigured(_('OAuth client needs either a User API URL or an OpenID Connect Discovery URL.'))

    def get_user_info(self, oauth_client: OAuthClient, data: dict) -> UserInfo:
        # TODO: possibly add support for arbitrary mappings
        return {
            'id': self.get_user_info_id(oauth_client, data),
            'email': self.get_user_info_email(oauth_client, data),
            'username':  self.get_user_info_username(oauth_client, data),
            'data': data
        }

    def get_user_info_id(self, oauth_client: OAuthClient, data: dict):
        identifier = get_by_key_string(data, oauth_client.user_id_key)
        if not identifier:
            raise Exception(_('OAuth client was unable to obtain an ID from user info.'))

        return identifier

    def get_user_info_email(self, oauth_client: OAuthClient, data: dict) -> Optional[str]:
        if not Settings.CLIENT_USE_EMAIL:
            return None

        if Settings.CLIENT_ALLOW_BLANK_EMAIL and not oauth_client.user_email_key:
            return None

        email = get_by_key_string(data, oauth_client.user_email_key)

        if not Settings.CLIENT_ALLOW_BLANK_EMAIL and not email:
            raise Exception(_('OAuth client was unable to obtain an email address from user info.'))

        return email

    def get_user_info_username(self, oauth_client: OAuthClient, data: dict) -> Optional[str]:
        if not Settings.CLIENT_USE_USERNAME:
            return None

        if Settings.CLIENT_ALLOW_BLANK_USERNAME and not oauth_client.user_username_key:
            return None

        username = get_by_key_string(data, oauth_client.user_username_key)

        if not Settings.CLIENT_ALLOW_BLANK_USERNAME and not username:
            raise Exception(_('OAuth client was unable to obtain a username from user info.'))

        return username

    def connect(self, oauth_client: OAuthClient, token: OAuthClientToken, user_info: UserInfo, request: HttpRequest) -> OAuthClientConnection:
        connection: OAuthClientConnection
        user: AbstractBaseUser

        # Attempt to find existing OAuth client connection
        connection = OAuthClientConnection.objects.filter(client=oauth_client, identifier=user_info['id']).first()

        if connection:
            # Validate
            self.validate_existing_connect(oauth_client, user_info, request, connection)

            user = connection.user
        else:
            # Validate
            self.validate_new_connect(oauth_client, user_info, request)

            if request.user.is_authenticated:
                # Use existing user
                user = request.user
            else:
                # Create user
                user = self.create_user(user_info)

            # Update user
            self.update_user(user, user_info)

            # Create OAuth client connection
            connection = self.create_connection(oauth_client, token, user_info, user)

        # Update OAuth client connection
        self.update_connection(connection, token, user_info, user)

        return connection

    def validate_existing_connect(self, oauth_client: OAuthClient, user_info: UserInfo, request: HttpRequest, connection: OAuthClientConnection):
        # Check if the user is trying to connect another user's OAuth account
        if request.user.is_authenticated and connection.user.id != request.user.id:
            raise ValidationError(_('OAuth user is already connected to another user.'), code='already_connected')

    def validate_new_connect(self, oauth_client: OAuthClient, user_info: UserInfo, request: HttpRequest):
        User = auth.get_user_model()

        # Validate email address
        if Settings.CLIENT_USE_EMAIL and user_info['email']:
            users = User.objects.filter(email=user_info['email'])

            if request.user.is_authenticated:
                users = users.exclude(id=request.user.id)

            if users.count() > 0:
                raise ValidationError(_('Email address already exists. This OAuth user can only be connected to a user with the same email address.'),
                                      code='email_exists')

        # Validate username
        if Settings.CLIENT_USE_USERNAME and user_info['username']:
            users = User.objects.filter(username=user_info['username'])

            if request.user.is_authenticated:
                users = users.exclude(id=request.user.id)

            if users.count() > 0:
                raise ValidationError(_('Username already exists. This OAuth user can only be connected to a user with the same username.'),
                                      code='username_exists')

    def create_connection(self, oauth_client: OAuthClient, token: OAuthClientToken, user_info: UserInfo, user: AbstractBaseUser):
        return OAuthClientConnection(client=oauth_client, identifier=user_info['id'], user=user)

    def update_connection(self, connection: OAuthClientConnection, token: OAuthClientToken, user_info: UserInfo, user: AbstractBaseUser):
        # Update email address
        if Settings.CLIENT_USE_EMAIL:
            if Settings.CLIENT_ALLOW_BLANK_EMAIL and not user_info['email']:
                connection.email = ''
            else:
                connection.email = user_info['email']

        # Update username
        if Settings.CLIENT_USE_USERNAME:
            if Settings.CLIENT_ALLOW_BLANK_USERNAME and not user_info['username']:
                connection.username = ''
            else:
                connection.username = user_info['username']

        # Update data
        connection.data = user_info['data']
        connection.save()

        # Update OAuth client token
        token.connection = connection
        token.save()

    def create_user(self, user_info: UserInfo) -> AbstractBaseUser:
        User = auth.get_user_model()
        user = User()

        if Settings.CLIENT_USE_EMAIL:
            user.email = user_info['email']

        if Settings.CLIENT_USE_USERNAME:
            user.username = user_info['username']

        return user

    def update_user(self, user: AbstractBaseUser, user_info: UserInfo):
        user.save()

    def disconnect(self, oauth_client: OAuthClient, connection: OAuthClientConnection):
        raise NotImplementedError()
