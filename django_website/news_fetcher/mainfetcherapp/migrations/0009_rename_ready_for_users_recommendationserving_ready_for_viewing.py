# Generated by Django 4.0.2 on 2022-02-18 20:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mainfetcherapp', '0008_recommendationserving_ready_for_users'),
    ]

    operations = [
        migrations.RenameField(
            model_name='recommendationserving',
            old_name='ready_for_users',
            new_name='ready_for_viewing',
        ),
    ]
