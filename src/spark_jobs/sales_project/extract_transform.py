from pyspark.sql import SparkSession
from pyspark.sql.types import *

schema = StructType(
    [
        StructField("ORDERNUMBER", IntegerType(), True),
        StructField("QUANTITYORDERED", IntegerType(), True),
        StructField("PRICEEACH", DoubleType(), True),
        StructField("ORDERLINENUMBER", IntegerType(), True),
        StructField("SALES", DoubleType(), True),
        StructField("ORDERDATE", StringType(), True),
        StructField("STATUS", StringType(), True),
        StructField("QTR_ID", IntegerType(), True),
        StructField("MONTH_ID", IntegerType(), True),
        StructField("YEAR_ID", IntegerType(), True),
        StructField("PRODUCTLINE", StringType(), True),
        StructField("MSRP", IntegerType(), True),
        StructField("PRODUCTCODE", StringType(), True),
        StructField("CUSTOMERNAME", StringType(), True),
        StructField("PHONE", StringType(), True),
        StructField("ADDRESSLINE1", StringType(), True),
        StructField("ADDRESSLINE2", StringType(), True),
        StructField("CITY", StringType(), True),
        StructField("STATE", StringType(), True),
        StructField("POSTALCODE", StringType(), True),
        StructField("COUNTRY", StringType(), True),
        StructField("TERRITORY", StringType(), True),
        StructField("CONTACTLASTNAME", StringType(), True),
        StructField("CONTACTFIRSTNAME", StringType(), True),
        StructField("DEALSIZE", StringType(), True),
    ]
)

spark = (
    SparkSession.builder.appName("ExtractTransformSales")
    .config(
        "spark.sql.catalog.iceberg.catalog-impl",
        "org.apache.iceberg.hadoop.HadoopCatalog",
    )
    .config("spark.sql.parquet.compression.codec", "snappy")
    .getOrCreate()
)

df = spark.read.csv("s3a://sales/sales_data.csv", schema=schema, header=True)

df = df.na.fill(0)  # Example: fill numeric nulls with 0


# Convert ORDERDATE to date
from pyspark.sql.functions import to_date

df = df.withColumn("ORDERDATE", to_date("ORDERDATE", "M/d/yyyy H:mm"))

# Option B: Extract just date portion if you don't need time
# df = df.withColumn("ORDERDATE", to_date(substring("ORDERDATE", 1, 10), "M/d/yyyy"))

# Save to Iceberg table
df.writeTo("iceberg.db.sales").using("iceberg").createOrReplace()

# Write as Parquet to MinIO
output_path = "s3a://warehouse/sales_parquet"
df.write.mode("overwrite").parquet(output_path)


# Read the Parquet files
parquet_df = spark.read.parquet("s3a://warehouse/sales_parquet")

# Show the first 10 rows
parquet_df.show(10, truncate=False)

# Print schema
parquet_df.printSchema()

spark.stop()
