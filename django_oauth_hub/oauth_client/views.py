from typing import Optional
from uuid import UUID

from django.conf import settings
from django.contrib import auth
from django.core.exceptions import ValidationError, ImproperlyConfigured
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views.generic import View

from ..settings import Settings
from ..util import get_by_key_string
from .models import OAuthClient, OAuthClientConnection


class OAuthRedirectView(View):

    def get(self, request: HttpRequest) -> HttpResponse:
        if OAuthClient.objects.count() != 1:
            raise ValidationError(_('More than one OAuth client available.'), code='too_many_clients')

        oauth_client = OAuthClient.objects.first()
        return redirect('oauth', args=(str(oauth_client.id), ))


class OAuthView(View):

    def get(self, request: HttpRequest, oauth_client_id: UUID = None, oauth_client_slug: str = None) -> HttpResponse:
        # Obtain client backend and user model
        backend = Settings.get_client_backend()

        # Find OAuth client
        oauth_client, client = backend.get_client(oauth_client_id, oauth_client_slug)

        # Redirect to OAuth provider
        redirect_uri = request.build_absolute_uri(reverse('oauth_callback', args=(str(oauth_client.id), )))
        return client.authorize_redirect(request, redirect_uri, **oauth_client.parameters)


class OAuthCallbackView(View):

    # TODO: check and refactor to backend
    def get(self, request: HttpRequest, oauth_client_id: UUID = None, oauth_client_slug: str = None) -> HttpResponse:
        # Obtain client backend and user model
        backend = Settings.get_client_backend()
        User = auth.get_user_model()

        # Find OAuth client
        oauth_client, client = backend.get_client(oauth_client_id, oauth_client_slug)

        # Obtain token from OAuth provider
        token = client.authorize_access_token(request)

        # Store OAuth client token
        oauth_client_token = backend.store_client_token(oauth_client, token)

        # Fetch user info if necessary
        user_info: Optional[dict]
        if 'userinfo' in token:
            user_info = token.get('userinfo')
        else:
            if oauth_client.user_api_url:
                # Fetch user info from API
                user_info = client.get(oauth_client.user_api_url, request=request)

                # Obtain nested user info from API response
                if oauth_client.user_api_key:
                    user_info = get_by_key_string(user_info, oauth_client.user_api_key)
            elif oauth_client.openid_url:
                # Fetch user info from OpenID Connect
                user_info = client.userinfo(token)
            else:
                raise ImproperlyConfigured(_('OAuth client needs either a User API URL or an OpenID Connect Discovery URL.'))

        if not user_info:
            raise Exception(_('OAuth client was unable to obtain user info.'))

        # Determine user ID
        user_info_id = get_by_key_string(user_info, oauth_client.user_id_key)
        if not user_info_id:
            raise Exception(_('OAuth client was unable to obtain an ID from user info.'))

        # Determine user email
        user_info_email = get_by_key_string(user_info, oauth_client.user_email_key)
        if not user_info_email:
            raise Exception(_('OAuth client was unable to obtain an email address from user info.'))

        # TODO: add support for username
        # TODO: possibly add support for arbitrary mappings

        # Attempt to find existing OAuth client connection
        connection = OAuthClientConnection.objects.filter(client=oauth_client, identifier=user_info_id).first()
        if connection:
            # Check if the user is trying to connect another user's OAuth account
            if request.user.is_authenticated and connection.user.id != request.user.id:
                raise ValidationError(_('OAuth user is already connected to another user.'), code='already_connected')
        else:
            # Check if email address already exists
            email_users = User.objects.filter(email=user_info_email)
            email_connections = OAuthClientConnection.objects.filter(email=user_info_email)
            # TODO: replace this check with a backend validation hook
            email_addresses = EmailAddress.objects.filter(email=user_info_email, is_verified=True)

            if request.user.is_authenticated:
                email_users = email_users.exclude(id=request.user.id)
                email_connections = email_connections.exclude(user=request.user)
                email_addresses = email_addresses.exclude(entity=request.user.person.entity if hasattr(request.user, 'person') else None)

            if email_users.count() > 0:
                raise ValidationError(_('Email address already exists.'), code='email_exists')
            if email_connections.count() > 0:
                # TODO: This validation check does not make any sense. An email address is allowed to exist for multiple OAuth accounts.
                raise ValidationError(_('Email address already exists for an account connected to another user.'), code='email_exists')
            if email_addresses.count() > 0:
                raise ValidationError(_('Email address already exists for another entity.'), code='email_exists')

            # Create OAuth client connection
            connection = OAuthClientConnection(client=oauth_client, identifier=user_info_id)

            if request.user.is_authenticated:
                # Connect to existing user
                connection.user = request.user
            else:
                # Create new user
                connection.user = User(email=user_info_email)
                connection.user.save()

        # Update OAuth client connection
        connection.email = user_info_email
        connection.data = user_info
        connection.save()

        # Update OAuth client token
        oauth_client_token.connection = connection
        oauth_client_token.save()

        # Log the user in
        if not request.user.is_authenticated:
            auth.login(request, connection.user)

        # Redirect to specified URL
        return redirect(settings.LOGIN_REDIRECT_URL)
