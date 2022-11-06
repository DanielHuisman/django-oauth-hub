from typing import Optional, TypedDict

from .models import OAuthClient


class OAuthProvider(TypedDict, total=False):
    name: str
    slug: str
    version: OAuthClient.Version
    type: OAuthClient.Type
    request_token_url: Optional[str]
    access_token_url: Optional[str]
    authorize_url: Optional[str]
    scope: Optional[str]
    parameters: Optional[dict]
    openid_url: Optional[str]
    user_api_url: Optional[str]
    user_api_key: Optional[str]
    user_id_key: Optional[str]
    user_email_key: Optional[str]
    user_username_key: Optional[str]


providers: dict[str, OAuthProvider] = {
    provider['slug']: provider for provider in [
        {
            'name': 'Google',
            'slug': 'google',
            'version': OAuthClient.Version.V2_0,
            'type': OAuthClient.Type.GENERIC,
            'scope': 'openid email profile',
            'parameters': {
                'access_type': 'offline'
            },
            'openid_url': 'https://accounts.google.com/.well-known/openid-configuration',
            'user_id_key': 'sub',
            'user_email_key': 'email'
        },
        {
            'name': 'Microsoft',
            'slug': 'microsoft',
            'version': OAuthClient.Version.V2_0,
            'type': OAuthClient.Type.GENERIC,
            'scope': 'openid email profile offline_access',
            # Available tenants: common, organizations, consumers, tenant ID
            # https://learn.microsoft.com/en-us/azure/active-directory/develop/v2-protocols-oidc#find-your-apps-openid-configuration-document-uri
            'openid_url': 'https://login.microsoftonline.com/common/v2.0/.well-known/openid-configuration',
            'user_id_key': 'sub',
            'user_email_key': 'email',
            'user_username_key': 'preferred_username'
        }
    ]
}
