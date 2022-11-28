from django.urls import path

from .views import OAuthView, OAuthCallbackView, OAuthRedirectView

urlpatterns = [
    path('oauth', OAuthRedirectView.as_view(), name='oauth_redirect'),
    path('oauth/<uuid:oauth_client_id>', OAuthView.as_view(), name='oauth'),
    path('oauth/<slug:oauth_client_slug>', OAuthView.as_view(), name='oauth'),
    path('oauth/<uuid:oauth_client_id>', OAuthCallbackView.as_view(), name='oauth_callback'),
    path('oauth/<slug:oauth_client_slug>', OAuthCallbackView.as_view(), name='oauth_callback')
]
