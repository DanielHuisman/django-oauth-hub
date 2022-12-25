# URLs

## Installation
The URLs can be installed in `urls.py` as follows:
```python
from django.urls import path, include

urlspatterns = [
    path('oauth/', include('django_oauth_hub.oauth_client.urls')),
]
```

## Explanation
### `/`
**Name:** `oauth_choice` or `oauth_redirect`

Either shows a choice of available clients or redirects to the only available client. See [the `default_view` option](../configuration.md).

### `/<oauth_client_id>`
### `/<oauth_client_slug`
**Name:** `oauth`

Starts the OAuth flow by redirecting to the provider.

### `/<oauth_client_id>/callback`
### `/<oauth_client_slug/callback`
**Name:** `oauth_callback`

Completes the OAuth flow with the information received from the provider.
