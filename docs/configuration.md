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

## Common
These settings apply to all modules and can be configured directly under the root:
```python
DJANGO_OAUTH_HUB = {
    # ...
}
```

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

| Name                   | Description                                                   | Default Value |
|------------------------|---------------------------------------------------------------|---------------|
| `use_email`            | Whether an email address field should be used for OAuth users | `True`        |
| `use_username`         | Whether a username field should be used for OAuth users.      | `False`       |
 | `allow_blank_email`    | Whether the email address field can be blank.                 | `False`       |
| `allow_blank_username` | Whether the username field can be blank.                      | `False`       |
| `max_length_username`  | Maximum length of the username field.                         | `150`         |

### After migration
These settings can be changed at any time.

| Name | Description | Default Value |
|------|-------------|---------------|


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

| Name | Description | Default Value |
|------|-------------|---------------|

### After migration
These settings can be changed at any time.

| Name | Description | Default Value |
|------|-------------|---------------|
