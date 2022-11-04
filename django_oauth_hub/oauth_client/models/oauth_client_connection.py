from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from django_oauth_hub.models import BaseModel
from django_oauth_hub.settings import Settings

from .oauth_client import OAuthClient


class OAuthClientConnection(BaseModel):

    class Meta:
        verbose_name = _('OAuth client connection')
        verbose_name_plural = _('OAuth client connections')
        unique_together = ('client', 'identifier')

    identifier = models.TextField(_('identifier'))
    data = models.JSONField(_('data'))

    if Settings.CLIENT_USE_EMAIL:
        email = models.EmailField(_('email address'), blank=Settings.CLIENT_ALLOW_BLANK_EMAIL)
    if Settings.CLIENT_USE_USERNAME:
        username = models.CharField(_('username'), max_length=Settings.CLIENT_MAX_LENGTH_USERNAME, blank=Settings.CLIENT_ALLOW_BLANK_USERNAME)

    client = models.ForeignKey(OAuthClient, verbose_name=_('client'), related_name='connections', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('user'), related_name='connections', on_delete=models.CASCADE)

    def __str__(self):
        return self.identifier
