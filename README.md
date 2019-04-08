#### Local Dev Environment with Docker

The application requires the following containers:
- Main Application
- Crawler Manger
- Crawler
- MySQL
- Redis

In production, MySQL and Redis will not be ran on containers.   
Crawler Manager container also has an internal Redis service.


### Dependencies

- Docker Desktop (2.x)


### Steps

1. Build and start the containers from the root of the repository:
    ```
    touch main/kubeconfig; touch crawler-manager/kubeconfig
    docker-compose -f docker-compose.yml up --build --no-start
    docker-compose -f docker-compose.yml start
    ```

2. All three containers will be started, but only the main container will have a permanent webserver running, this is the access route:
    ```
    Main: `http://localhost:8001/`   
    ```

    If the main application is not loading, then likely the database isn't created properly. Enter the shell
    for the mysql container and create the test database
    ```
    docker exec -it webcrawler_crawler-mysql5_1 bash
    $ mysql -u root -proot

    mysql> CREATE DATABASE test;
    ```

3. For running the crawler-manager (No Longer Required. Crawler manager is also getting started in step 1): 
   
    This does not need to be built, it's done already in the `docker-compose` command, but to simulate a new crawler manager, run the following:      
    ```
    docker exec -i crawler-manager /bin/bash -c "export JOB_ID=123; service redis-server start && python app.py"  
    ```
    
    That will start the webserver for 60s, like is done in kubernetes
    
3. For running the crawler, is like the manager (No Longer Required. Crawler is also getting started in step 1)
   
    Sames as above, does not need to be built.

    For processing urls
    ```
    docker exec -i crawler /bin/bash -c "export URLS='http://google.com,https://cnn.com'; export ENVIRONMENT=prod && python app.py" 
    ```

    To clear Redis cache
    ```
    docker exec -it web-crawler_crawler-redis_1 redis-cli FLUSHALL
    ```

    Crawler runs for 15s  

    Note: Change the value in the `export` command, for the URLS you want to process

4. In order to reload code changes into the containers, run these comands:

    Main:
    ```
    docker cp main/. main-app:/srv/www/web-crawler/
    docker-compose -f docker-compose.yml restart main
    ```  

    Crawler Manager:
    ```
    docker cp crawler-manager/. crawler-manager:/srv/www/web-crawler/    
    docker-compose -f docker-compose.yml restart crawler-manager
    ```  

    Crawler:
    ```
    docker cp crawler/. crawler:/srv/www/web-crawler/
    docker-compose -f docker-compose.yml restart crawler
    ```  

5. After all containers are running, you need to run the `initialize-django.sh` script,
    to initialize the DB and set up a super user, so you can use the admin UI to create more users.

    ```
    docker exec -it main-app bash -c "./initialize-django.sh"
    ```
