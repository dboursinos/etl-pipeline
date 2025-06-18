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
  pandas \
  s3fs \
  boto3 \
  prophet

WORKDIR /app

# Copy the script to container
COPY ./src/ml_jobs/sales_project/train_prophet.py .

# Default command to run
CMD ["python", "train_prophet.py"]
