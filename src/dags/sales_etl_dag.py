from airflow import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.providers.trino.operators.trino import TrinoOperator
from airflow.operators.python import PythonOperator
from airflow.providers.cncf.kubernetes.operators.pod import (
    KubernetesPodOperator,
)
from datetime import datetime

with DAG(
    "sales_etl_iceberg",
    start_date=datetime(2023, 1, 1),
    schedule_interval=None,
    catchup=False,
    tags=["spark", "iceberg", "minio"],
) as dag:
    spark_job_extract = SparkSubmitOperator(
        task_id="spark_extract",
        application="/opt/airflow/spark_jobs/sales_project/extract.py",
        conn_id="spark_default",
        verbose=True,
        name="arrow-spark",
        application_args=[],
        conf={
            "spark.sql.catalog.iceberg": "org.apache.iceberg.spark.SparkCatalog",
            "spark.sql.catalog.iceberg.catalog-impl": "org.apache.iceberg.hive.HiveCatalog",
            "spark.sql.catalog.iceberg.uri": "thrift://192.168.1.70:9083",
            "spark.sql.catalog.iceberg.warehouse": "s3a://warehouse/",
            "spark.hadoop.fs.s3a.endpoint": "http://192.168.1.70:9020",
            "spark.hadoop.fs.s3a.access.key": "minioadmin",
            "spark.hadoop.fs.s3a.secret.key": "minioadmin",
            "spark.hadoop.fs.s3a.path.style.access": "true",
            "spark.jars.packages": "org.apache.hadoop:hadoop-aws:3.3.4,org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.4.3",
            "spark.sql.parquet.compression.codec": "snappy",
            # Add master
            # "spark.master": "spark://spark-master:7077",
            # "spark.executor.memory": "2g",
            # "spark.driver.memory": "2g",
        },
        # master="local[*]",  # Or "spark://spark-master:7077" in a cluster
        # deploy_mode="client",
    )

    spark_job_transform = SparkSubmitOperator(
        task_id="spark_transform",
        application="/opt/airflow/spark_jobs/sales_project/transform.py",
        conn_id="spark_default",
        verbose=True,
        name="arrow-spark",
        application_args=[],
        conf={
            "spark.sql.catalog.iceberg": "org.apache.iceberg.spark.SparkCatalog",
            "spark.sql.catalog.iceberg.catalog-impl": "org.apache.iceberg.hive.HiveCatalog",
            "spark.sql.catalog.iceberg.uri": "thrift://192.168.1.70:9083",
            "spark.sql.catalog.iceberg.warehouse": "s3a://warehouse/",
            "spark.hadoop.fs.s3a.endpoint": "http://192.168.1.70:9020",
            "spark.hadoop.fs.s3a.access.key": "minioadmin",
            "spark.hadoop.fs.s3a.secret.key": "minioadmin",
            "spark.hadoop.fs.s3a.path.style.access": "true",
            "spark.jars.packages": "org.apache.hadoop:hadoop-aws:3.3.4,org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.4.3",
            "spark.sql.parquet.compression.codec": "snappy",
        },
    )

    spark_prepare_features = SparkSubmitOperator(
        task_id="spark_prepare_features",
        application="/opt/airflow/spark_jobs/sales_project/spark_prepare_features.py",
        conn_id="spark_default",
        verbose=True,
        name="prepare-features",
        application_args=[],
        conf={
            "spark.sql.catalog.iceberg": "org.apache.iceberg.spark.SparkCatalog",
            "spark.sql.catalog.iceberg.catalog-impl": "org.apache.iceberg.hive.HiveCatalog",
            "spark.sql.catalog.iceberg.uri": "thrift://192.168.1.70:9083",
            "spark.sql.catalog.iceberg.warehouse": "s3a://warehouse/",
            "spark.hadoop.fs.s3a.endpoint": "http://192.168.1.70:9020",
            "spark.hadoop.fs.s3a.access.key": "minioadmin",
            "spark.hadoop.fs.s3a.secret.key": "minioadmin",
            "spark.hadoop.fs.s3a.path.style.access": "true",
            "spark.jars.packages": "org.apache.hadoop:hadoop-aws:3.3.4,org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.4.3",
            "spark.sql.parquet.compression.codec": "snappy",
        },
    )

    spark_job_aggregate = SparkSubmitOperator(
        task_id="spark_aggregate",
        application="/opt/airflow/spark_jobs/sales_project/aggregate_sales.py",
        conn_id="spark_default",
        verbose=True,
        name="arrow-spark",
        application_args=[],
        conf={
            "spark.sql.catalog.iceberg": "org.apache.iceberg.spark.SparkCatalog",
            "spark.sql.catalog.iceberg.catalog-impl": "org.apache.iceberg.hive.HiveCatalog",
            "spark.sql.catalog.iceberg.uri": "thrift://192.168.1.70:9083",
            "spark.sql.catalog.iceberg.warehouse": "s3a://warehouse/",
            "spark.hadoop.fs.s3a.endpoint": "http://192.168.1.70:9020",
            "spark.hadoop.fs.s3a.access.key": "minioadmin",
            "spark.hadoop.fs.s3a.secret.key": "minioadmin",
            "spark.hadoop.fs.s3a.path.style.access": "true",
            "spark.jars.packages": "org.apache.hadoop:hadoop-aws:3.3.4,org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.4.3",
            "spark.sql.parquet.compression.codec": "snappy",
        },
    )

    trino_task = TrinoOperator(
        task_id="trino_query",
        sql="SELECT * FROM iceberg.db.sales",
        trino_conn_id="trino_default",
        database="iceberg",
        do_xcom_push=True,
    )

    def handle_trino_result(**context):
        result = context["ti"].xcom_pull(task_ids="trino_query")
        print("Trino Result:", result)

    print_task = PythonOperator(
        task_id="print_trino_result",
        python_callable=handle_trino_result,
        provide_context=True,
    )

    train_prophet_task = KubernetesPodOperator(
        task_id="train_prophet_model",
        name="train-prophet",
        namespace="default",
        image="192.168.1.67:5050/airflow-ml-training",
        image_pull_policy="Always",
        cmds=["python", "train_prophet.py"],
        volumes=[],
        volume_mounts=[],
        env_vars={
            "AWS_ACCESS_KEY_ID": "minioadmin",
            "AWS_SECRET_ACCESS_KEY": "minioadmin",
            "S3_ENDPOINT": "http://192.168.1.70:9020",
        },
        get_logs=True,
        # is_delete_operator_pod=True,
        in_cluster=False,  # Uses ~/.kube/config if False
        config_file="/home/airflow/.kube/config",  # Required if not running in-cluster
        arguments=[],
        container_resources={
            "limits": {"memory": "2Gi", "cpu": "1"},
            "requests": {"memory": "1Gi", "cpu": "0.5"},
        },
    )

    train_exponential_smoothing_task = KubernetesPodOperator(
        task_id="train_exponential_smoothing_model",
        name="train-exponential-smoothing",
        namespace="default",
        image="192.168.1.67:5050/airflow-ml-training",
        image_pull_policy="Always",
        cmds=["python", "train_exponential_smoothing.py"],
        volumes=[],
        volume_mounts=[],
        env_vars={
            "AWS_ACCESS_KEY_ID": "minioadmin",
            "AWS_SECRET_ACCESS_KEY": "minioadmin",
            "S3_ENDPOINT": "http://192.168.1.70:9020",
        },
        get_logs=True,
        # is_delete_operator_pod=True,
        in_cluster=False,  # Uses ~/.kube/config if False
        config_file="/home/airflow/.kube/config",  # Required if not running in-cluster
        arguments=[],
        container_resources={
            "limits": {"memory": "2Gi", "cpu": "1"},
            "requests": {"memory": "1Gi", "cpu": "0.5"},
        },
    )

    (
        spark_job_extract
        >> spark_job_transform
        >> spark_prepare_features
        >> train_prophet_task
    )
    (
        spark_job_extract
        >> spark_job_transform
        >> spark_prepare_features
        >> train_exponential_smoothing_task
    )

    spark_job_transform >> spark_job_aggregate
    spark_job_transform >> trino_task >> print_task
