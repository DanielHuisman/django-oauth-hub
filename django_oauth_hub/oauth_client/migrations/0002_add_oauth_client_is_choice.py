# Generated by Django 4.1.4 on 2022-12-25 13:33

from django.db import migrations, models
import django_oauth_hub.settings


class Migration(migrations.Migration):

    dependencies = [
        ('oauth_client', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='oauthclient',
            name='is_choice',
            field=models.BooleanField(default=django_oauth_hub.settings.Settings.get_client_is_choice_default, verbose_name='is choice'),
        ),
        migrations.AlterField(
            model_name='oauthclient',
            name='parameters',
            field=models.JSONField(blank=True, default=dict, verbose_name='parameters'),
        ),
    ]
