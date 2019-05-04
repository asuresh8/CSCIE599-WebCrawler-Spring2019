#!/bin/bash

# build docker containers
docker-compose -f docker-compose.yml up --build --no-start

# run crawler unit tests
docker run --name test-crawler web-crawler_crawler /bin/bash -c \
    'pip install -r test_requirements.txt && 
     coverage run -m unittest $(ls | grep _test.py) &&
     coverage report'
docker stop test-crawler && docker rm test-crawler

# run crawler manager unit tests
docker run --name test-crawler-manager web-crawler_crawler-manager /bin/bash -c \
    'pip install -r test_requirements.txt && 
     coverage run -m unittest $(ls | grep _test.py) &&
     cover report'
docker stop test-crawler-manager && docker rm test-crawler-manager

# run main application tests
docker run --name test-main web-crawler_main /bin/bash -c \
    'export ENVIRONMENT=test && 
     pip install -r test_requirements.txt && 
     python project/manage.py test project --settings=webcrawler.test_settings'
docker stop test-main && docker rm test-main