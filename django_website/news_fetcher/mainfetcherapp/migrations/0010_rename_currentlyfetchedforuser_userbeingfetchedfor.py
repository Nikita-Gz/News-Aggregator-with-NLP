# Generated by Django 4.0.2 on 2022-02-18 20:45

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('mainfetcherapp', '0009_rename_ready_for_users_recommendationserving_ready_for_viewing'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='CurrentlyFetchedForUser',
            new_name='UserBeingFetchedFor',
        ),
    ]
