from django import forms
from django.contrib.admin import register, ModelAdmin
from django.utils.translation import gettext_lazy as _

from ..settings import Settings
from .forms import OAuthClientModelForm
from .models import OAuthClient, OAuthClientConnection, OAuthClientToken

additional_fields = () + (('email', ) if Settings.CLIENT_USE_EMAIL else ()) + (('username', ) if Settings.CLIENT_USE_USERNAME else ())


@register(OAuthClient)
class OAuthClientAdmin(ModelAdmin):
    form = OAuthClientModelForm
    list_display = ('name', 'slug', 'version', 'type')
    list_filter = ('version', 'type')
    ordering = ('name', )

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)

        # Filter out fields from default fieldset
        filter_names = ('provider', ) if obj else ('provider', 'client_id', 'client_secret')
        filtered_fields = [field for field in fieldsets[0][1]['fields'] if field not in filter_names]

        if obj:
            # Return the default fieldsets when updating
            return [(None, {'fields': filtered_fields})]
        else:
            # Return the custom fieldsets when adding
            return [
                (_('From provider template'), {'fields': ('provider', )}),
                (_('From manual configuration'), {'fields': filtered_fields}),
                (_('Credentials'), {'fields': ('client_id', 'client_secret')})
            ]


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
