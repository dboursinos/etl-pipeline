FROM apache/superset:4.1.2

USER root

RUN apt-get update && \
  apt-get install -y --no-install-recommends \
  postgresql-client \
  && rm -rf /var/lib/apt/lists/*

# Instala drivers Python
RUN pip install --no-cache-dir \
  sqlalchemy-trino \
  psycopg2-binary \
  pymysql \
  pillow

# USER superset

# COPY init-scripts/superset-init.sh /app/
# RUN chmod +x /app/superset-init.sh
