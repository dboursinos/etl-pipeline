FROM bitnami/spark:3.5.6

USER root

# Instalar curl (Bitnami usa install_packages)
RUN apt-get update \
  && apt-get install -y iputils-ping
RUN install_packages curl

RUN mkdir -p /opt/spark/jars

# Instalar dependencias necesarias para S3A (ajustar según Hadoop/Spark version)
RUN curl -o /opt/spark/jars/hadoop-aws-3.3.1.jar https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.3.1/hadoop-aws-3.3.1.jar && \
  curl -o /opt/spark/jars/aws-java-sdk-bundle-1.11.1026.jar https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.11.1026/aws-java-sdk-bundle-1.11.1026.jar

ENV SPARK_EXTRA_CLASSPATH="/opt/spark/jars/*"
