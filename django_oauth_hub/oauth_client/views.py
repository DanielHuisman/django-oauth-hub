from uuid import UUID

from django.conf import settings
from django.contrib import auth
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext as _
from django.views.generic import FormView, ListView, View

from .backend.base import OAuthUserInfo
from ..settings import Settings
from .forms import OAuthConfirmConnectForm
from .models import OAuthClient, OAuthClientToken, OAuthClientConnection


class OAuthLoginView(ListView):

    model = OAuthClient
    queryset = OAuthClient.objects.filter(is_choice=True)
    context_object_name = 'clients'
    template_name = 'oauth_client/login.html'

    is_connect = False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_connect'] = self.is_connect
        return context

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated and not self.is_connect:
            return redirect(settings.LOGIN_REDIRECT_URL)

        request.session['oauth_connect'] = self.is_connect

        if Settings.CLIENT_REDIRECT_LOGIN:
            queryset = OAuthClient.objects.filter(is_choice=True)

            if queryset.count() == 1:
                # Redirect to OAuth view
                oauth_client = queryset.first()
                return redirect(oauth_client.oauth_url)

        return super().get(request, *args, **kwargs)


class OAuthConnectView(LoginRequiredMixin, OAuthLoginView):

    is_connect = True


class OAuthView(View):

    def get(self, request: HttpRequest, oauth_client_id: UUID = None, oauth_client_slug: str = None) -> HttpResponse:
        # Obtain client backend
        backend = Settings.get_client_backend()

        # Find OAuth client
        oauth_client, client = backend.get_client(oauth_client_id, oauth_client_slug)

        # Clear previously stored token
        request.session['oauth_token_id'] = None
        request.session['oauth_user_info'] = None

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

        if request.user.is_authenticated and not request.session.get('oauth_connect'):
            # Store token and user info
            request.session['oauth_token_id'] = str(oauth_client_token.id) if Settings.USE_UUID else oauth_client.id
            request.session['oauth_user_info'] = user_info

            # Redirect to connect view
            return redirect('oauth_connect')

        # Find or create OAuth client connection
        connection = backend.connect(oauth_client, oauth_client_token, user_info, request)

        # Log the user in
        auth.login(request, connection.user)

        # Redirect to specified URL
        return redirect(settings.LOGIN_REDIRECT_URL)


class OAuthConfirmConnectView(LoginRequiredMixin, FormView):

    form_class = OAuthConfirmConnectForm
    template_name = 'oauth_client/connect.html'

    def get_token_and_user_info(self) -> tuple[OAuthClientToken, OAuthUserInfo]:
        # Validate session data
        oauth_token_id = self.request.session.get('oauth_token_id')
        oauth_user_info = self.request.session.get('oauth_user_info')
        if not oauth_token_id or not oauth_user_info:
            return redirect('oauth_login')

        # Validate token
        oauth_token = OAuthClientToken.objects.filter(id=oauth_token_id).first()
        if not oauth_token:
            return redirect('oauth_login')

        return oauth_token, oauth_user_info

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        token, user_info = self.get_token_and_user_info()
        context['user_info'] = user_info

        return context

    def form_valid(self, form):
        token, user_info = self.get_token_and_user_info()
        choice = form.cleaned_data.get('choice')

        # Log the existing user out
        if choice == 'login':
            auth.logout(self.request)

        # Obtain client backend
        backend = Settings.get_client_backend()

        # Find or create OAuth client connection
        connection = backend.connect(token.client, token, user_info, self.request)

        # Log the user in
        if choice == 'login':
            auth.login(self.request, connection.user)
            return redirect(settings.LOGIN_REDIRECT_URL)

        return redirect('oauth_connections')


class OAuthConnectionsView(LoginRequiredMixin, ListView):

    model = OAuthClientConnection
    context_object_name = 'connections'
    template_name = 'oauth_client/connections.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['Settings'] = Settings
        return context

    def get_queryset(self):
        order_by = 'identifier'
        if Settings.CLIENT_USE_EMAIL:
            order_by = 'email'
        if Settings.CLIENT_USE_USERNAME:
            order_by = 'username'

        return OAuthClientConnection.objects.filter(user=self.request.user).order_by(order_by)


class OAuthDisconnectView(FormView):

    form_class = OAuthConfirmConnectForm
    template_name = 'oauth_client/disconnect.html'
    success_url = reverse_lazy('oauth_connections')

    # TODO: disconnect logic
    # TODO: add setting for allowing disconnecting of all accounts
