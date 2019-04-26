#!/bin/bash
python project/manage.py makemigrations
python project/manage.py migrate
echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 's3cr3tp4ss')" | python project/manage.py shell
