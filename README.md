EPHEMERAL MESSAGING SERVICE
============================
PRE-REQUISITES
--------------
- Postgres instance (9.x)
- Redis instance (3.x)
- Django version (1.8)
- Nginx (1.8)
- Gunicorn (19.x)
- Python (3.4)


INSTALLATION
------------

- Clone git repo:
https://github.com/kiranp/ephemeral_message_service
After cloning repo under /<my_dir>, this is how your directory structure should look like:

```
tree /<my_dir>/ephemeral_message_service
```

```
EphemeralMessages
     media
     settings.py
     static
     urls.py
     wsgi.py
manage.py
requirements.txt
restapi
     admin.py
     exceptions.py
     models.py
     urls.py
     utils.py
     views.py
     wsgi.py
```

- Configure nginx and gunicorn. Make them point to the Django project.
For reference, please see the following document:
https://www.digitalocean.com/community/tutorials/how-to-set-up-django-with-postgres-nginx-and-gunicorn-on-ubuntu-14-04

- Install dependencies

```
cd /<my_dir>/ephemeral_message_service
pip3 install -r requirements.txt
```

- Edit EphemeralMessages/settings.py
Update Postgres server settings
Update Redis server settings

- Run database Migrations:
```
python3 manage.py makemigrations restapi
python3 manage.py migrate
```

- If you are deploying to a production server, be sure to update STATIC file configuration in settings.py file and run:
```
python3 manage.py collectstatic
```
Reference:
https://www.digitalocean.com/community/tutorials/how-to-deploy-a-local-django-app-to-a-vps

- Start the service:
Dev mode:
```
python3 manage.py runserver localhost:9000
```

Prod mode:
```
service gunicorn restart
```

TESTS
-----
- Several test cases are included in Django project (tests.py). To execute these tests:
```
cd /<my_dir>/ephemeral_message_service
nosetests restapi
```

LOGGING
-------
- A 'chat_server.log' file will be created by this service.  It will track django, db and cache related messages. 
Logging confguration is in settings.py


DESIGN
------
- See 


IMPLEMENTATION SPECIFICS:


ADDITIONAL CONSIDERATIONS:


