from pyspark.sql import SparkSession
from pyspark.sql.functions import sum, year, month, round

spark = SparkSession.builder.appName("prepare-features").getOrCreate()

df = spark.read.format("iceberg").load("iceberg.db.sales")

monthly_sales = (
    df.withColumn("year", year("ORDERDATE"))
    .withColumn("month", month("ORDERDATE"))
    .groupBy("PRODUCTLINE", "year", "month")
    .agg(
        round(sum("SALES"), 2).alias("total_sales"),
        sum("QUANTITYORDERED").alias("total_quantity"),
    )
    .orderBy("PRODUCTLINE", "year", "month")
)

monthly_sales.printSchema()
monthly_sales.show()

monthly_sales.write.mode("overwrite").parquet(
    "s3a://machine-learning/features/monthly_sales"
)
