from uuid import UUID

from django.conf import settings
from django.contrib import auth
from django.core.exceptions import ValidationError
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse, NoReverseMatch
from django.utils.translation import gettext as _
from django.views.generic import View

from ..settings import Settings
from .models import OAuthClient


class OAuthRedirectView(View):

    def get(self, request: HttpRequest) -> HttpResponse:
        if OAuthClient.objects.count() != 1:
            raise ValidationError(_('More than one OAuth client available.'), code='too_many_clients')

        oauth_client = OAuthClient.objects.first()
        arg = oauth_client.slug if oauth_client.slug else str(oauth_client.id)

        try:
            return redirect('oauth', args=(arg, ))
        except NoReverseMatch:
            return redirect('/oauth/{}'.format(arg))


class OAuthView(View):

    def get(self, request: HttpRequest, oauth_client_id: UUID = None, oauth_client_slug: str = None) -> HttpResponse:
        # Obtain client backend and user model
        backend = Settings.get_client_backend()

        # Find OAuth client
        oauth_client, client = backend.get_client(oauth_client_id, oauth_client_slug)

        # Redirect to OAuth provider
        arg = oauth_client.slug if oauth_client.slug else str(oauth_client.id)
        redirect_uri = request.build_absolute_uri(reverse('oauth_callback', args=(arg, )))
        return client.authorize_redirect(request, redirect_uri, **oauth_client.parameters)


class OAuthCallbackView(View):

    def get(self, request: HttpRequest, oauth_client_id: UUID = None, oauth_client_slug: str = None) -> HttpResponse:
        # Obtain client backend
        backend = Settings.get_client_backend()

        # Find OAuth client
        oauth_client, client = backend.get_client(oauth_client_id, oauth_client_slug)

        # Obtain token from OAuth provider
        token = client.authorize_access_token(request)

        # Store OAuth client token
        oauth_client_token = backend.store_client_token(oauth_client, token)

        # Fetch user info data
        user_info_data = backend.get_user_info_data(oauth_client, client, token, request)
        if not user_info_data:
            raise Exception(_('OAuth client was unable to obtain user info.'))

        # Process user info
        user_info = backend.get_user_info(oauth_client, user_info_data)
        if not user_info:
            raise Exception(_('OAuth client was unable to process user info.'))

        # Find or create OAuth client connection
        connection = backend.connect(oauth_client, oauth_client_token, user_info, request)

        # Log the user in
        if not request.user.is_authenticated:
            auth.login(request, connection.user)

        # Redirect to specified URL
        return redirect(settings.LOGIN_REDIRECT_URL)
