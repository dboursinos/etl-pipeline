from pyspark.sql import SparkSession
from pyspark.sql.functions import col, month, year, sum, round


def main():
    spark = SparkSession.builder.appName("GoldLayer").getOrCreate()

    # Read from Iceberg silver layer
    df = spark.read.format("iceberg").load("iceberg.db.sales")

    agg_df = (
        df.withColumn("year", year("ORDERDATE"))
        .withColumn("month", month("ORDERDATE"))
        .groupBy("PRODUCTLINE", "year", "month")
        .agg(
            round(sum("SALES"), 2).alias("total_sales"),
            sum("QUANTITYORDERED").alias("total_quantity"),
        )
        .orderBy("PRODUCTLINE", "year", "month")
    )

    agg_df.writeTo("iceberg.db.sales_gold").using("iceberg").createOrReplace()

    spark.stop()


if __name__ == "__main__":
    main()
