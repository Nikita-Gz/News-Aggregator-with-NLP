# add defaultserving user

import os

# does migrations
os.system('python manage.py makemigrations')
os.system('python manage.py migrate')
os.system('python manage.py loaddata allowed_sources')
