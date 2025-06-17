from pyspark.sql import SparkSession
from pyspark.sql.types import *
from pyspark.sql.functions import current_timestamp, input_file_name

spark = SparkSession.builder.appName("ExtractSales").getOrCreate()

df = spark.read.csv("s3a://sales/sales_data.csv", header=True)

df = df.withColumn("ingestion_time", current_timestamp()).withColumn(
    "source_file", input_file_name()
)

# Write as Parquet to MinIO
output_path = "s3a://warehouse/bronze/sales"
df.write.mode("overwrite").parquet(output_path)

spark.stop()
