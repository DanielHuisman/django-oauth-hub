from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from django_oauth_hub.models import BaseModel

from .oauth_client import OAuthClient
from .oauth_client_connection import OAuthClientConnection


class OAuthClientToken(BaseModel):

    class Meta:
        verbose_name = _('OAuth client token')
        verbose_name_plural = _('OAuth client tokens')

    oauth_token = models.TextField(_('OAuth token'), blank=True, null=True)
    oauth_token_secret = models.TextField(_('OAuth token secret'), blank=True, null=True)
    token_type = models.TextField(_('token type'), blank=True, null=True)
    access_token = models.TextField(_('access token'), blank=True, null=True)
    refresh_token = models.TextField(_('refresh token'), blank=True, null=True)
    expires_at = models.DateTimeField(_('expires at'), blank=True, null=True)

    client = models.ForeignKey(OAuthClient, verbose_name=_('client'), related_name='tokens', on_delete=models.CASCADE)
    connection = models.ForeignKey(OAuthClientConnection, verbose_name=_('connection'), related_name='tokens', blank=True, null=True,
                                   on_delete=models.SET_NULL)

    def __str__(self):
        if self.client.version == OAuthClient.Version.V1_0:
            return self.oauth_token
        elif self.client.version == OAuthClient.Version.V2_0:
            return self.access_token
        else:
            raise NotImplementedError('Unknown OAuth client version.')

    def clean(self):
        if self.client.version == OAuthClient.Version.V1_0 and (not self.oauth_token or not self.oauth_token_secret):
            if not self.oauth_token:
                raise ValidationError(_('OAuth token cannot be blank when using OAuth 1.0'), code='blank')
            if not self.oauth_token_secret:
                raise ValidationError(_('OAuth token secret cannot be blank when using OAuth 1.0'), code='blank')
        if self.client.version == OAuthClient.Version.V2_0:
            if not self.token_type:
                raise ValidationError(_('Token type cannot be blank when using OAuth 2.0'), code='blank')
            if not self.access_token:
                raise ValidationError(_('Access token cannot be blank when using OAuth 2.0'), code='blank')

    def save(self, **kwargs):
        self.clean()
        super().save(**kwargs)

    def is_expired(self):
        return self.expires_at and self.expires_at >= timezone.now()

    def to_token(self):
        if self.client.version == OAuthClient.Version.V1_0:
            return {
                'oauth_token': self.oauth_token,
                'oauth_token_secret': self.oauth_token_secret
            }
        elif self.client.version == OAuthClient.Version.V2_0:
            return {
                'token_type': self.token_type,
                'access_token': self.access_token,
                'refresh_token': self.refresh_token,
                'expires_at': self.expires_at
            }
        else:
            raise NotImplementedError('Unknown OAuth client version.')
