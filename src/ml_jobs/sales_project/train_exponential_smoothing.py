import os
import pandas as pd
import boto3
import pickle
from statsmodels.tsa.api import ExponentialSmoothing
from io import BytesIO
import pyarrow.dataset as ds
import pyarrow.fs

from s3fs import S3FileSystem

S3_BUCKET = "machine-learning"
FEATURE_PATH = "features/monthly_sales"
MODEL_PATH = "models/exponential_smoothing/"

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
    # Check if there are at least two seasonal cycles (e.g., 24 months for monthly data with yearly seasonality)
    if len(group_df) >= 24:
        model = ExponentialSmoothing(
            group_df["y"], seasonal_periods=12, trend="add", seasonal="add"
        ).fit()
    else:
        # If not enough data for seasonal model, use a simpler model without seasonality
        model = ExponentialSmoothing(group_df["y"], trend="add", seasonal=None).fit()

    # Save model to MinIO
    with fs.open(f"{S3_BUCKET}/{MODEL_PATH}{productline}_model.pkl", "wb") as f:
        pickle.dump(model, f)
