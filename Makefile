DOCKER_COMPOSE_FILE := compose.yaml

# Target to run Docker Compose for the mlflow, postgres and minio services
up:
	docker compose -f ./docker/$(DOCKER_COMPOSE_FILE) up -d

# Target to stop Docker Compose and remove mlflow, postgres and minio services
down:
	docker compose -f ./docker/$(DOCKER_COMPOSE_FILE) down --rmi 'all'

logs:
	docker compose -f ./docker/$(DOCKER_COMPOSE_FILE) logs
