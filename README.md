### From folder  `web-crawler`

#### Start web-crawler

```
- docker-compose -f docker-compose.yml up --build --no-start
- docker-compose -f docker-compose.yml start
```

URLS:
```
Main:
    -http://localhost:8001/

Crawler Manager:
    - http://localhost:8001/crawler/manager
    - http://localhost:8002/

Crawler:
    - http://localhost:8001/crawler
    - http://localhost:8003/
```
