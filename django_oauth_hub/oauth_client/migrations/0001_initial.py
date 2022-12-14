# Generated by Django 4.1.3 on 2022-11-04 14:16

import uuid

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

from django_oauth_hub.fields import UUID4Field
from django_oauth_hub.settings import Settings


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='OAuthClient',
            fields=[
                ('id', UUID4Field(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='ID') if Settings.USE_UUID else models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated at')),
                ('version', models.CharField(choices=[('V1_0', '1.0'), ('V2_0', '2.0')], max_length=4, verbose_name='version')),
                ('type', models.CharField(choices=[('GENERIC', 'Generic')], max_length=32, verbose_name='type')),
                ('name', models.TextField(verbose_name='name')),
                ('slug', models.SlugField(blank=True, max_length=255, verbose_name='slug')),
                ('client_id', models.TextField(default='placeholder', verbose_name='client ID')),
                ('client_secret', models.TextField(default='placeholder', verbose_name='client secret')),
                ('request_token_url', models.URLField(blank=True, verbose_name='request token URL')),
                ('access_token_url', models.URLField(blank=True, verbose_name='access token URL')),
                ('authorize_url', models.URLField(blank=True, verbose_name='authorize URL')),
                ('scope', models.TextField(blank=True, verbose_name='scope')),
                ('parameters', models.JSONField(default=dict, verbose_name='parameters')),
                ('openid_url', models.URLField(blank=True, verbose_name='OpenID Connect Discovery URL')),
                ('user_api_url', models.URLField(blank=True, verbose_name='user API URL')),
                ('user_api_key', models.TextField(blank=True, verbose_name='user API key')),
                ('user_id_key', models.TextField(verbose_name='user ID key')),
            ] + ([
                ('user_email_key', models.TextField(verbose_name='user email key')),
            ] if Settings.CLIENT_USE_EMAIL else []) + ([
                ('user_username_key', models.TextField(blank=True, verbose_name='user username key')),
            ] if Settings.CLIENT_USE_USERNAME else []),
            options={
                'verbose_name': 'OAuth client',
                'verbose_name_plural': 'OAuth clients',
            },
        ),
        migrations.CreateModel(
            name='OAuthClientConnection',
            fields=[
                ('id', UUID4Field(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='ID') if Settings.USE_UUID else models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated at')),
                ('identifier', models.TextField(verbose_name='identifier')),
                ('data', models.JSONField(verbose_name='data')),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='connections', to='oauth_client.oauthclient', verbose_name='client')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='connections', to=settings.AUTH_USER_MODEL, verbose_name='user')),
            ] + ([
                ('email', models.EmailField(blank=Settings.CLIENT_ALLOW_BLANK_EMAIL, max_length=254, verbose_name='email address')),
            ] if Settings.CLIENT_USE_EMAIL else []) + ([
                ('username', models.CharField(blank=Settings.CLIENT_ALLOW_BLANK_USERNAME, max_length=Settings.CLIENT_MAX_LENGTH_USERNAME, verbose_name='username')),
            ] if Settings.CLIENT_USE_USERNAME else []),
            options={
                'verbose_name': 'OAuth client connection',
                'verbose_name_plural': 'OAuth client connections',
                'unique_together': {('client', 'identifier')},
            },
        ),
        migrations.CreateModel(
            name='OAuthClientToken',
            fields=[
                ('id', UUID4Field(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='ID') if Settings.USE_UUID else models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated at')),
                ('oauth_token', models.TextField(blank=True, null=True, verbose_name='OAuth token')),
                ('oauth_token_secret', models.TextField(blank=True, null=True, verbose_name='OAuth token secret')),
                ('token_type', models.TextField(blank=True, null=True, verbose_name='token type')),
                ('access_token', models.TextField(blank=True, null=True, verbose_name='access token')),
                ('refresh_token', models.TextField(blank=True, null=True, verbose_name='refresh token')),
                ('expires_at', models.DateTimeField(blank=True, null=True, verbose_name='expires at')),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tokens', to='oauth_client.oauthclient', verbose_name='client')),
                ('connection', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tokens', to='oauth_client.oauthclientconnection', verbose_name='connection')),
            ],
            options={
                'verbose_name': 'OAuth client token',
                'verbose_name_plural': 'OAuth client tokens',
            },
        ),
    ]
