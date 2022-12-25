from django.contrib.auth.views import LogoutView
from django.urls import path

from ..settings import Settings
from .views import OAuthView, OAuthCallbackView, OAuthConnectionsView, OAuthConnectView, OAuthDisconnectView, OAuthLoginView

urlpatterns = [
    path('login', OAuthLoginView.as_view(), name='oauth_login'),
    path('logout', LogoutView.as_view(), name='oauth_logout'),
    path('connect', OAuthConnectView.as_view(), name='oauth_connect'),
    path('connections', OAuthConnectionsView.as_view(), name='oauth_connections'),
] + ([
    path('<uuid:oauth_client_id>', OAuthView.as_view(), name='oauth'),
    path('<uuid:oauth_client_id>/callback', OAuthCallbackView.as_view(), name='oauth_callback'),
    path('disconnect/<uuid:oauth_connection_id>', OAuthDisconnectView.as_view(), name='oauth_disconnect'),
] if Settings.USE_UUID else [
    path('<int:oauth_client_id>', OAuthView.as_view(), name='oauth'),
    path('<int:oauth_client_id>/callback', OAuthCallbackView.as_view(), name='oauth_callback'),
    path('disconnect/<int:oauth_connection_id>', OAuthDisconnectView.as_view(), name='oauth_disconnect'),
]) + [
    path('<slug:oauth_client_slug>', OAuthView.as_view(), name='oauth'),
    path('<slug:oauth_client_slug>/callback', OAuthCallbackView.as_view(), name='oauth_callback'),
]
