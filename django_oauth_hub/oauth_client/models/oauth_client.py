from django.core.exceptions import ValidationError
from django.db import models
from django.urls import NoReverseMatch, reverse
from django.utils.translation import gettext_lazy as _

from django_oauth_hub.models import BaseModel
from django_oauth_hub.settings import Settings


class OAuthClient(BaseModel):

    class Meta:
        verbose_name = _('OAuth client')
        verbose_name_plural = _('OAuth clients')

    class Version(models.TextChoices):
        V1_0 = 'V1_0', _('1.0')
        V2_0 = 'V2_0', _('2.0')

    # In the future non-compliant OAuth servers can be added to this enum
    class Type(models.TextChoices):
        GENERIC = 'GENERIC', _('Generic')

    version = models.CharField(_('version'), max_length=4, choices=Version.choices)
    type = models.CharField(_('type'), max_length=32, choices=Type.choices)
    name = models.TextField(_('name'))
    slug = models.SlugField(_('slug'), max_length=255, blank=True)
    client_id = models.TextField(_('client ID'), default='placeholder')
    client_secret = models.TextField(_('client secret'), default='placeholder')
    request_token_url = models.URLField(_('request token URL'), blank=True)
    access_token_url = models.URLField(_('access token URL'), blank=True)
    authorize_url = models.URLField(_('authorize URL'), blank=True)
    scope = models.TextField(_('scope'), blank=True)
    parameters = models.JSONField(_('parameters'), blank=True, default=dict)
    openid_url = models.URLField(_('OpenID Connect Discovery URL'), blank=True)
    user_api_url = models.URLField(_('user API URL'), blank=True)
    user_api_key = models.TextField(_('user API key'), blank=True)
    user_id_key = models.TextField(_('user ID key'))
    is_choice = models.BooleanField(_('is choice'), default=Settings.get_client_is_choice_default)

    if Settings.CLIENT_USE_EMAIL:
        user_email_key = models.TextField(_('user email key'), blank=Settings.CLIENT_ALLOW_BLANK_EMAIL)
    if Settings.CLIENT_USE_USERNAME:
        user_username_key = models.TextField(_('user username key'), blank=Settings.CLIENT_ALLOW_BLANK_USERNAME)

    def __str__(self):
        return self.name

    @property
    def oauth_url(self):
        arg = self.slug if self.slug else str(self.id)
        try:
            return reverse('oauth', args=(arg, ))
        except NoReverseMatch:
            # When using integer IDs Django can't distinguish between IDs and slugs, so this is a workaround.
            return reverse('oauth', args=('__slug__', )).replace('__slug__', arg)

    def clean(self):
        # Validate mandatory fields
        if self.version == OAuthClient.Version.V1_0:
            if self.openid_url:
                raise ValidationError(_('OpenID Connect Discovery cannot be used for OAuth 1.0.'), code='openid')
            if not self.request_token_url:
                raise ValidationError(_('Request token URL cannot be blank when using OAuth 1.0.'), code='blank')
        if self.version == OAuthClient.Version.V2_0:
            if not self.openid_url:
                if not self.access_token_url:
                    raise ValidationError(_('Access token URL cannot be blank when using OAuth 2.0 without OpenID Connect Discovery.'), code='blank')
                if not self.authorize_url:
                    raise ValidationError(_('Authorize URL cannot be blank when using OAuth 2.0 without OpenID Connect Discovery.'), code='blank')

        # Ensure parameters is always a dictionary
        if not self.parameters:
            self.parameters = {}

        # Validate user info URL
        if not self.user_api_url and not self.openid_url:
            raise ValidationError(_('User API URL and OpenID Connect Discovery URL cannot both be blank.'), code='blank')

        # Ensure OpenID scope is present when using OpenID Connect
        if self.openid_url and 'openid' not in self.scope:
            self.scope = f'openid,{self.scope}' if self.scope else 'openid'

        # Call backend validation hook
        Settings.get_client_backend().clean_oauth_client(self)

    def save(self, **kwargs):
        self.clean()
        super().save(**kwargs)
