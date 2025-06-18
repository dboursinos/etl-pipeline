import os
import pandas as pd
import boto3
import pickle
from prophet import Prophet
from io import BytesIO
import pyarrow.dataset as ds
import pyarrow.fs

from s3fs import S3FileSystem

S3_BUCKET = "machine-learning"
FEATURE_PATH = "features/monthly_sales"
MODEL_PATH = "models/"

# Configure S3
fs = S3FileSystem(
    client_kwargs={
        "endpoint_url": os.environ["S3_ENDPOINT"],
    },
    key=os.environ["AWS_ACCESS_KEY_ID"],
    secret=os.environ["AWS_SECRET_ACCESS_KEY"],
)

dataset = ds.dataset(
    source=f"{S3_BUCKET}/{FEATURE_PATH}", filesystem=fs, format="parquet"
)

# Load the dataset
df = dataset.to_table().to_pandas()

# Group by productline and train a model per group
for productline, group_df in df.groupby("PRODUCTLINE"):
    group_df = group_df.rename(columns={"month": "ds", "monthly_sales": "y"})
    model = Prophet()
    model.fit(group_df)

    # Save model to MinIO
    with fs.open(f"{S3_BUCKET}/{MODEL_PATH}{productline}_model.pkl", "wb") as f:
        pickle.dump(model, f)
