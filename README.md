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

2. Only the main container will be available with docker compose, this is the access route:
    ```
    Main: `http://localhost:8001/`   
    ```

    If the main application is not loading, then likely the database isn't created properly. Enter the shell
    for the mysql container and create the test database
    ```
    $ mysql -u root -p

    mysql> CREATE DATABASE test;
    ```

3. For running the crawler manager: 
   
    Build the image:   
    ```
    docker build -t crawler-manager -f crawler-manager/DockerFile .
    ```
    
    Once the image is built, create and start the container:  
    ```
    docker create --name crawler-manager --network webcrawler_default -p 8002:8002 crawler-manager
    docker start crawler-manager
    ```

    For processing a job
    ```
    docker exec -i crawler-manager /bin/bash -c "export JOB_ID=123 && python app.py"  
    ```
    Note: Change the value in the `export` command, for the JOB_ID you want to process
    
3. For running the crawler, is like the manager
   
    Build the image:   
    ```
    docker build -t crawler -f crawler/DockerFile .
    ```
    
    Once the image is built, create and start the container
    ```
    docker create --name crawler --network webcrawler_default -p 8003:8003 crawler
    docker start crawler
    ```

    For processing urls
    ```
    docker exec -i crawler /bin/bash -c "export URLS='http://google.com,https://cnn.com' && python app.py" 
    ```
    Note: Change the value in the `export` command, for the URLS you want to process

4. In order to reload code changes into the containers, run these comands:

    Main:
    ```
    docker cp main/. main-crawler:/srv/www/web-crawler/
    docker-compose -f docker-compose.yml restart main
    ```  

    Crawler Manager:
    ```
    docker cp crawler-manager/. crawler-manager:/srv/www/web-crawler/    
    docker restart crawler-manager
    ```  

    Crawler:
    ```
    docker cp crawler/. crawler:/srv/www/web-crawler/
    docker restart crawler
    ```  

5. After all containers are running, you need to run the `initialize-django.sh` script,
    to initialize the DB and set up a super user, so you can use the admin UI to create more users.

    ```
    docker exec -it <your-MAIN-container-ID> bash -c "./initialize-django.sh"
    ```
