# Generated by Django 4.0.2 on 2022-02-21 15:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainfetcherapp', '0014_alter_articlekeyword_article'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='download_date',
            field=models.DateTimeField(null=True),
        ),
    ]
