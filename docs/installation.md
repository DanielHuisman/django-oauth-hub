# Installation

1. Install the Python package:
```bash
pip install django-oauth-hub
# Or
pipenv install django-oauth-hub
# Or
poetry add django-oauth-hub
```
2. Add the Django applications to the list of installed applications:

```python
INSTALLED_APPS = [
    # ...

    # One or both modules
    'django_oauth_hub.oauth_client',
    'django_oauth_hub.oauth_server',
]
```
3. Configure the settings, see [configuration](configuration.md):
```python
# Django OAuth Hub

DJANGO_OAUTH_HUB = {
    # ...
}
```
**Note:** Some settings can only be configured before the first migration.

4. Migrate the database:
```bash
python manage.py migrate
```
