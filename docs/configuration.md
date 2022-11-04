# Configuration

The settings for Django OAuth Hub need to be defined with a dictionary named `DJANGO_OAUTH_HUB`:
```python
# Django OAuth Hub

DJANGO_OAUTH_HUB = {
    # ...
    'client': {
        # ...
    },
    'server': {
        # ...
    }
}
```

The settings are separated per module:
- [Common](#common)
- [Client](#client)
- [Server](#server)

**Note:** Several settings can only be configured before the first migration.

See [`example/settings.py`](../example/example/settings.py) for an example.

## Common
These settings apply to all modules and can be configured directly under the root:
```python
DJANGO_OAUTH_HUB = {
    # ...
}
```

### Before migration
These settings can only be changed before the first migration.

| Name       | Description                                                                                                                                                                                                                                                                                                                                                | Type   | Default Value |
|------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------|---------------|
| `use_uuid` | Whether the models should use [`UUIDField`](https://docs.djangoproject.com/en/4.1/ref/models/fields/#uuidfield) as primary key, otherwise [`BigAutoField`](https://docs.djangoproject.com/en/4.1/ref/models/fields/#bigautofield) is used. It uses [`uuid.uuid4`](https://docs.python.org/3/library/uuid.html#uuid.uuid4) to generate random primary keys. | `bool` | `False`       |

### After migration
These settings can be changed at any time.

| Name | Description | Type | Default Value |
|------|-------------|------|---------------|

## Client
These settings are for the OAuth client module and can be configured under the `client` key:
```python
DJANGO_OAUTH_HUB = {
    'client': {
        # ...
    }
}
```

### Before migration
These settings can only be changed before the first migration.

| Name                   | Description                                                                                                                                     | Type   | Default Value                                                     |
|------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------|--------|-------------------------------------------------------------------|
| `backend`              | Backend used for OAuth clients. Override this to customize the default behaviour. See [client backend](client/backend.md) for more information. | `str`  | `django_oauth_hub.oauth_client.backend.DefaultOAuthClientBackend` |
| `use_email`            | Whether an email address field should be used for OAuth users                                                                                   | `bool` | `True`                                                            |
| `use_username`         | Whether a username field should be used for OAuth users.                                                                                        | `bool` | `False`                                                           |
 | `allow_blank_email`    | Whether the email address field can be blank.                                                                                                   | `bool` | `False`                                                           |
| `allow_blank_username` | Whether the username field can be blank.                                                                                                        | `bool` | `False`                                                           |
| `max_length_username`  | Maximum length of the username field.                                                                                                           | `int`  | `150`                                                             |

### After migration
These settings can be changed at any time.

| Name | Description | Type | Default Value |
|------|-------------|------|---------------|


## Server
These settings are for the OAuth server module and can be configured under the `server` key:
```python
DJANGO_OAUTH_HUB = {
    'server': {
        # ...
    }
}
```

### Before migration
These settings can only be changed before the first migration.

| Name | Description | Type | Default Value |
|------|-------------|------|---------------|

### After migration
These settings can be changed at any time.

| Name | Description | Type | Default Value |
|------|-------------|------|---------------|
