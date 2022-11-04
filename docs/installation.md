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
    'django_oauth_hub.client',
    'django_oauth_hub.server',
]
```
3. Configure the settings:
```python
# TODO
```
