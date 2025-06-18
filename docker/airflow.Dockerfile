FROM apache/airflow:2.11.0

USER root
RUN sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys B7B3B788A8D3785C
RUN sudo apt-get update
RUN sudo apt-get install -y --no-install-recommends \
  git \
  openjdk-17-jre-headless \
  libaio1 \
  unzip \
  tar \
  iputils-ping \
  procps \
  && apt-get autoremove -yqq --purge \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

USER airflow

RUN pip install --no-cache-dir dbt-postgres \
  && pip install pyspark==3.5.6 \
  && pip install markupsafe==2.0.1 \
  && pip install apache-airflow-providers-postgres \
  && pip install apache-airflow-providers-odbc \
  && pip install psycopg2-binary \
  && pip install gitpython \
  && pip install dbt-airflow \
  && pip install plyvel \
  && pip install --upgrade cmake \
  && pip install --upgrade pyarrow==14.0.0 \
  && pip install apache-airflow-providers-trino==5.9.0 \
  && pip install apache-airflow-providers-apache-spark \
  && pip install apache-airflow-providers-cncf-kubernetes==10.4.3 \
  && pip install dbt-trino \
  && pip uninstall dbt \
  && pip install dbt-core

COPY --chown=airflow:airflow .kube/config /home/airflow/.kube/config

RUN airflow db migrate
#RUN airflow db init
#RUN airflow db upgrade
