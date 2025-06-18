DOCKER_COMPOSE_FILE := compose.yaml

# Target to run Docker Compose for the mlflow, postgres and minio services
up:
	docker compose -f ./docker/$(DOCKER_COMPOSE_FILE) up -d

# Target to stop Docker Compose and remove mlflow, postgres and minio services
down:
	docker compose -f ./docker/$(DOCKER_COMPOSE_FILE) down --rmi 'all'

logs:
	docker compose -f ./docker/$(DOCKER_COMPOSE_FILE) logs

build_ml_train_image:
	docker build . -f ./src/ml_jobs/sales_project/Dockerfile -t airflow-ml-training:latest
	docker tag airflow-ml-training:latest 192.168.1.67:5050/airflow-ml-training:latest
	docker push 192.168.1.67:5050/airflow-ml-training:latest
