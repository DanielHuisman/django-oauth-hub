from uuid import UUID

from django.core.exceptions import ValidationError
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views.generic import View

from .models import OAuthClient
from .oauth import get_oauth_client_by_id, get_oauth_client_by_slug


class OAuthRedirectView(View):

    def get(self, request: HttpRequest) -> HttpResponse:
        if OAuthClient.objects.count() != 1:
            raise ValidationError(_('More than one OAuth client available.'), code='too_many_clients')

        oauth_client = OAuthClient.objects.first()
        return redirect('oauth', args=(str(oauth_client.id), ))


class OAuthView(View):

    def get(self, request: HttpRequest, oauth_client_id: UUID = None, oauth_client_slug: str = None) -> HttpResponse:
        # Find OAuth client
        if oauth_client_id:
            oauth_client, client = get_oauth_client_by_id(oauth_client_id)
        elif oauth_client_slug:
            oauth_client, client = get_oauth_client_by_slug(oauth_client_slug)
        else:
            raise ValidationError('No OAuth client ID or slug specified.', code='no_id_or_slug')

        # Redirect to OAuth provider
        redirect_uri = request.build_absolute_uri(reverse('oauth_callback', args=(str(oauth_client.id), )))
        return client.authorize_redirect(request, redirect_uri, **oauth_client.parameters)


class OAuthCallbackView(View):

    def get(self, request: HttpRequest) -> HttpResponse:
        # TODO
        pass
