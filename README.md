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

2. Only the main container will be available with docker compose, this is the access route:
    ```
    Main: `http://localhost:8001/`   
    ```

3. For running the crawler manager: 
   
    First the image must be built.   
    ```
    docker build -t crawler-manager -f crawler-manager/DockerFile crawler-manager/
    ```
    
    Once the image is built, create and start the container
    ```
    docker create --name crawler-manager --network webcrawler_default -p 8002:8002 crawler-manager
    docker start crawler-manager
    ```

    For processing a job
    ```
    docker exec -i crawler-manager /bin/bash -c "export JOB_ID=123 && python app.py" # app.py or the script that should process the job
    ```
    Note: anytime you need to process a different job id, change the value in the `export` command
    

4. In order to reload code changes into the containers, run these comands:

    Main:
    ```
    docker cp  main/. main-crawler:/srv/www/web-crawler/
    docker-compose -f docker-compose.yml restart main
    ```  

    Crawler Manager:
    ```
    docker cp  crawler-manager/. crawler-manager:/srv/www/web-crawler/    
    ```  

    Crawler:
    ```
    docker cp  crawler/. crawler:/srv/www/web-crawler/
    docker-compose -f docker-compose.yml restart crawler
    ```  

5. After all containers are running, you need to run the `initialize-django.sh` script,
to initialize the DB and set up a super user, so you can use the admin UI to create more users.

    ```
    docker exec -it <your-MAIN-container-ID> bash -c "./initialize-django.sh"
    ```

### Connecting to Kubernetes in Python

```python
from google.cloud import container_v1
from google.oauth2 import service_account
import base64
import kubernetes
import os

creds = service_account.Credentials.from_service_account_file('/Users/adi/Downloads/WebCrawler-feb11a08e450.json')
client = container_v1.ClusterManagerClient(credentials=creds)
cluster = client.get_cluster('webcrawler-233816', 'us-central1-a', 'web-crawler')
ca_cert = os.path.join(os.environ['HOME'], 'k8s_ca_cert.pem')
client_cert = os.path.join(os.environ['HOME'], 'k8s_client_cert.pem')
client_key = os.path.join(os.environ['HOME'], 'k8s_client_key.pem')
with open(ca_cert, 'wb') as f:
    f.write(base64.base64decode(cluster.master_auth.cluster_ca_certificate))

with open(client_cert, 'wb') as f:
    f.write(base64.base64decode(cluster.master_auth.client_certificate))

with open(client_key, 'wb' as f):
    f.write(base64.base64decode(cluster.master_auth.client_key))

k8s_config = kubernetes.client.Configuration()
k8s_config.host = cluster.endpoint
k8s_config.ssl_ca_cert = ca_cert
k8s_config.cert_file = client_cert
k8s_config.key_file = client_key
k8s_client = kubernetes.client.CoreV1Api(k8_config)
```