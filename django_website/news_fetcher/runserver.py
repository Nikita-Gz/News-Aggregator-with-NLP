from subprocess import Popen

db_init = Popen(['python', 'manage.py', 'loaddata', 'allowed_sources.json'])

# wait for db to finish initing
db_init.communicate()

# start server
Popen(['python', 'manage.py', 'runserver', '0.0.0.0:8000'], close_fds=True)
