FROM python:3.12-slim

# Set environment variables to prevent Python from writing .pyc files and buffering stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
  build-essential \
  python3-dev \
  git \
  curl \
  libatlas-base-dev \
  && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

RUN pip install \
  pandas==2.3.0 \
  s3fs==2025.5.1 \
  boto3 \
  prophet==1.1.7 \
  statsmodels==0.14.4 \
  pyarrow==20.0.0 \
  fastparquet==2024.11.0

WORKDIR /app

# Copy the script to container
COPY ./src/ml_jobs/sales_project/train_prophet.py .
COPY ./src/ml_jobs/sales_project/train_exponential_smoothing.py .

# Default command to run
#CMD ["python", "train_prophet.py"]
