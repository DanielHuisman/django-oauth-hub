from abc import abstractmethod, ABC
from typing import Any, Optional, TypedDict
from uuid import UUID

from django.contrib.auth.base_user import AbstractBaseUser
from django.http import HttpRequest

from ..models import OAuthClient, OAuthClientToken, OAuthClientConnection
from ..providers import OAuthProvider


class OAuthUserInfo(TypedDict):
    id: str
    email: Optional[str]
    username: Optional[str]
    data: dict


class BaseOAuthClientBackend(ABC):

    @abstractmethod
    def get_providers(self) -> dict[str, OAuthProvider]:
        raise NotImplementedError()

    def clean_oauth_client(self, oauth_client: OAuthClient):
        pass

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
    def get_user_info(self, oauth_client: OAuthClient, data: dict) -> OAuthUserInfo:
        raise NotImplementedError()

    @abstractmethod
    def connect(self, oauth_client: OAuthClient, token: OAuthClientToken, user_info: OAuthUserInfo, request: HttpRequest):
        raise NotImplementedError()

    @abstractmethod
    def disconnect(self, oauth_client: OAuthClient, connection: OAuthClientConnection):
        raise NotImplementedError()

    def validate_existing_connect(self, oauth_client: OAuthClient, user_info: OAuthUserInfo, request: HttpRequest, connection: OAuthClientConnection):
        pass

    def validate_new_connect(self, oauth_client: OAuthClient, user_info: OAuthUserInfo, request: HttpRequest):
        pass

    def create_connection(self, oauth_client: OAuthClient, token: OAuthClientToken, user_info: OAuthUserInfo, user: AbstractBaseUser) -> OAuthClientConnection:
        pass

    def update_connection(self, connection: OAuthClientConnection, token: OAuthClientToken, user_info: OAuthUserInfo,  user: AbstractBaseUser):
        pass

    def create_user(self, user_info: OAuthUserInfo) -> AbstractBaseUser:
        pass

    def update_user(self, user: AbstractBaseUser, user_info: OAuthUserInfo):
        pass
