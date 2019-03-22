## Django Backend and User Interface

### Virtual Python environment
To make sure all dependencies are met and installed in their correct version, please use Python3 and a virtual environment for the project.<br>
Clone the project and change into the `django` directory. After following the instructions below, you can use the application, create users,
log in and out and also create CrawlRequests from within the `admin/` interface. There is currently only one admin (superuser) created. The credentials are `admin:secretpass!`

##### Set up and activate virtual environment:
```sh
$ python3 -m virtualenv webcrawler-env
$ source webcrawler-env/bin/activate
```

##### Requirements:
- [requirements.txt](requirements.txt):<br>
This file contains all the required packages. Install using:
```sh
$ pip install -r requirements.txt
```

##### HTML Template Files:
ToDo. Documentation of the HTML files.

##### Python Files:
ToDo. Documentation of the Python files.

##### Run application:
$ cd project
$ python manage.py runserver
