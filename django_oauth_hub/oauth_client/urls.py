from django.urls import path

from ..settings import Settings
from .views import OAuthView, OAuthCallbackView, OAuthRedirectView

urlpatterns = [
    path('', OAuthRedirectView.as_view(), name='oauth_redirect'),
] + ([
    path('<uuid:oauth_client_id>', OAuthView.as_view(), name='oauth'),
    path('<uuid:oauth_client_id>/callback', OAuthCallbackView.as_view(), name='oauth_callback'),
] if Settings.USE_UUID else [
    path('<int:oauth_client_id>', OAuthView.as_view(), name='oauth'),
    path('<int:oauth_client_id>/callback', OAuthCallbackView.as_view(), name='oauth_callback'),
]) + [
    path('<slug:oauth_client_slug>', OAuthView.as_view(), name='oauth'),
    path('<slug:oauth_client_slug>/callback', OAuthCallbackView.as_view(), name='oauth_callback')
]
