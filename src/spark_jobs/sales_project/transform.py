from pyspark.sql import SparkSession
from pyspark.sql.types import *
from pyspark.sql.functions import to_date, col, months

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

spark = SparkSession.builder.appName("TransformSales").getOrCreate()

# Read the Parquet files
df = spark.read.parquet("s3a://warehouse/bronze/sales", schema=schema, header=True)

df = df.na.fill(0)  # Example: fill numeric nulls with 0


# Convert ORDERDATE to date
df = df.withColumn("ORDERDATE", to_date("ORDERDATE", "M/d/yyyy H:mm"))

# Option B: Extract just date portion if you don't need time
# df = df.withColumn("ORDERDATE", to_date(substring("ORDERDATE", 1, 10), "M/d/yyyy"))

# print all unique values in PRODUCTLINE
df.select("PRODUCTLINE").distinct().show()

try:
    spark.sql("DROP TABLE IF EXISTS iceberg.db.sales")
    print("Table iceberg.db.sales dropped (if it existed)")
except Exception as e:
    print(f"Error dropping table: {e}")

spark.sql("CREATE DATABASE IF NOT EXISTS iceberg.db")

# Save to Iceberg table
df.writeTo("iceberg.db.sales").partitionedBy(
    col("PRODUCTLINE"), months("ORDERDATE")
).using("iceberg").createOrReplace()

spark.stop()
