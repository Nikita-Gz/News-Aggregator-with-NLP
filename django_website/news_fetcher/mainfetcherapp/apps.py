from django.apps import AppConfig


class MainfetcherappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mainfetcherapp'

    # create user for default serving
    def ready(self):
        from django.contrib.auth.models import User
        from .models import Source
        from .constants import default_serving_username
        import string
        import random

        # checks if default user exists
        default_serving_user_collection = User.objects.filter(username=default_serving_username)
        if len(default_serving_user_collection) == 0:
            # creates default servings user
            password = ''.join(
                random.choices(
                    string.ascii_uppercase +
                    string.digits +
                    string.ascii_lowercase,
                    k=30))
            default_serving_user = User.objects.create_user(
                username=default_serving_username,
                email='test@test.test',
                password=password)
            default_serving_user.save()
        else:
            default_serving_user = default_serving_user_collection[0]

        # add default sources to it
        for source in Source.objects.filter(assigned_to_user_by_default=True):
            source_already_selected = len(source.selected_by_users.filter(username=default_serving_user.username)) > 0
            if not source_already_selected:
                source.selected_by_users.add(default_serving_user)
