from django.contrib.admin import register, ModelAdmin

from ..settings import Settings
from .models import OAuthClient, OAuthClientConnection, OAuthClientToken

additional_fields = () + (('email', ) if Settings.CLIENT_USE_EMAIL else ()) + (('username', ) if Settings.CLIENT_USE_USERNAME else ())


@register(OAuthClient)
class OAuthClientAdmin(ModelAdmin):
    list_display = ('name', 'slug', 'version', 'type')
    list_filter = ('version', 'type')
    ordering = ('name', )


@register(OAuthClientConnection)
class OAuthClientConnectionAdmin(ModelAdmin):
    list_display = ('client', 'user') + additional_fields
    list_filter = ('client', )
    ordering = ('client__name', 'user__email') + additional_fields


@register(OAuthClientToken)
class OAuthClientTokenAdmin(ModelAdmin):
    list_display = ('id', 'client', 'connection', 'expires_at')
    list_filter = ('client', 'expires_at')
    ordering = ('id', )
