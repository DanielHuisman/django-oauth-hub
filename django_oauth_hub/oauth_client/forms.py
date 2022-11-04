from django import forms

from ..settings import Settings
from .models import OAuthClient


class OAuthClientModelForm(forms.ModelForm):

    class Meta:
        model = OAuthClient
        exclude = ()

    provider = forms.ChoiceField(
        choices=((None, 'None'), ) + tuple(((provider['slug'], provider['name']) for provider in Settings.get_client_backend().get_providers().values())),
        required=False,
        initial=None
    )

    def full_clean(self):
        # Fill form from OAuth provider template
        if self.data.get('provider'):
            provider = Settings.get_client_backend().get_providers().get(self.data.get('provider'))

            self.data = self.data.copy()
            self.data.update(provider)

        super().full_clean()
