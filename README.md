
### Project Structure
```
web-crawler/
    /backend
        /app_configure.py
        /app.py
        /requirements.txt
        /DockerFile-backend
        /static
        /tests
            /testMain.py
        /templates/
            /index.html
    /docker-compose.yml
    /.gitlab-ci.yml
    /.gitignore
```
### Start web-crawler

``` docker-compose -f docker-compose.yml up -d web-crawler```
