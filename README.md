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
docker-compose -f docker-compose.yml up --build --no-start
docker-compose -f docker-compose.yml start
```

2. Once all container are runing, container will run on these endpoints:

Main: `http://localhost:8001/`
Crawler Manager: `http://localhost:8002/`
Crawler: `http://localhost:8003/`

3. In order to reload code changes into the containers, run these comands:

Main:
```
docker cp  main/. main-crawler:/srv/www/web-crawler/
docker-compose -f docker-compose.yml restart main
```  

Crawler Manager:
```
docker cp  crawler-manager/. crawler-manager:/srv/www/web-crawler/
docker-compose -f docker-compose.yml restart crawler-manager
```  

Crawler:
```
docker cp  crawler/. crawler:/srv/www/web-crawler/
docker-compose -f docker-compose.yml restart crawler
```  
