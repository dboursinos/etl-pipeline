# Data Pipeline with Spark, Iceberg, Hive, Trino & Airflow

## 📋 Overview

This project implements a modern, scalable ETL pipeline using Apache Spark, Apache Iceberg, Hive Metastore, and Trino — all orchestrated with Apache Airflow and powered by object storage via MinIO. It enables structured data ingestion, transformation, and analysis with support for large-scale queries and dashboarding tools like Superset.

---

## 🔁 Pipeline Flow

### 1. **Extract CSV Data from MinIO**
- Raw sales data is stored as CSV files in a MinIO bucket.
- A Spark job reads these files (`extract.py`).
- Additional metadata is added (e.g., `ingestion_date`, `source_file`).
- Output is written as partitioned **Parquet** files to a *warehouse* bucket.

### 2. **Transform & Structure**
- Spark reads the previously generated Parquet files (`transform.py`).
- Schema is explicitly defined with typed columns (e.g., `INT`, `STRING`, `DATE`).
- Simple transformations and cleanups are applied (e.g., date parsing, formatting).
- The output is written to an **Apache Iceberg** table using the **HiveCatalog**.

### 3. **Catalog with Hive Metastore**
- Tables are registered in Hive Metastore, enabling query engines like Trino to discover them.
- The warehouse path is configured as an S3-compatible bucket in MinIO.

### 4. **Query & Analyze with Trino**
- Trino connects to Hive Metastore and reads Iceberg tables directly.
- Business logic and aggregation queries (e.g., sales per product per month) are executed.
- Results can be consumed by visualization tools like **Apache Superset**.

---

## 🧰 Technologies Used

| Component        | Purpose                                      |
|------------------|----------------------------------------------|
| **Apache Spark** | ETL: Reading, transforming, and writing data |
| **MinIO**        | S3-compatible object storage for raw & parquet data |
| **Apache Iceberg** | Table format with support for versioning, partitioning |
| **Hive Metastore** | Catalog and schema registry for Iceberg    |
| **Trino**        | Distributed SQL engine for analytics         |
| **Apache Airflow** | Workflow orchestration of the entire pipeline |
| **Superset**     | Dashboarding and visualization (optional)    |

---

## 🧪 Example Query in Trino

```sql
SELECT
  PRODUCTLINE,
  MONTH(orderDate) AS order_month,
  SUM(sales) AS total_sales
FROM iceberg.db.sales
GROUP BY PRODUCTLINE, MONTH(orderDate);
```

## 📦 Airflow DAG Structure

```yaml
extract_csv_minio     ->   write_parquet_warehouse
                            |
                          ↓
            transform_parquet_and_write_iceberg
                            |
                          ↓
                 trino_query_business_logic

```
