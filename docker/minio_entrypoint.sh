#!/bin/sh

# Set MinIO client alias
mc alias set minio http://localhost:9000 "$MINIO_ROOT_USER" "$MINIO_ROOT_PASSWORD"

# Create the 'warehouse' bucket if it doesn't exist
mc mb minio/warehouse --ignore-existing

# Set the bucket to be publicly accessible
mc anonymous set public minio/warehouse

# Execute the main command passed to the container (e.g., minio server)
exec "$@"
