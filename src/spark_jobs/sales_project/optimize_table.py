from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("optimize-sales").getOrCreate()

spark.sql("""
  CALL iceberg.system.rewrite_data_files(
    table => 'iceberg.db.sales',
    options => map(
      'zorder-by', 'PRODUCTLINE,ORDERDATE'
    )
  )
""")
