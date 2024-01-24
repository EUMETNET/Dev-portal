# Dev-portal

Steps to run whole stack:
1. navigate to root folder of project and run:
```sh
docker-compose up
```
This will start all containers requred for dev portal
2. run command:
```sh
docker exec -it vault_test sh /vault/config/setup.sh
```
This will run setup script inside vault container so we can save new entries
3. 