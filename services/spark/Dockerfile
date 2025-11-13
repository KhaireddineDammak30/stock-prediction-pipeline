FROM apache/spark:3.5.1

USER root

# Basic tools
RUN apt-get update && apt-get install -y curl ca-certificates zip unzip && rm -rf /var/lib/apt/lists/*

# Spark local ivy cache dir (sometimes useful)
RUN mkdir -p /opt/spark/.ivy2 && chmod -R 777 /opt/spark/.ivy2

# ===== Kafka + Cassandra connectors (you already had these) =====
RUN set -ex && \
  echo ">>> Installing Spark Kafka connectors..." && \
  curl -fL -o /opt/spark/jars/spark-sql-kafka-0-10_2.12-3.5.1.jar \
    https://repo1.maven.org/maven2/org/apache/spark/spark-sql-kafka-0-10_2.12/3.5.1/spark-sql-kafka-0-10_2.12-3.5.1.jar && \
  curl -fL -o /opt/spark/jars/spark-streaming-kafka-0-10_2.12-3.5.1.jar \
    https://repo1.maven.org/maven2/org/apache/spark/spark-streaming-kafka-0-10_2.12/3.5.1/spark-streaming-kafka-0-10_2.12-3.5.1.jar && \
  curl -fL -o /opt/spark/jars/kafka-clients-3.6.1.jar \
    https://repo1.maven.org/maven2/org/apache/kafka/kafka-clients/3.6.1/kafka-clients-3.6.1.jar && \
  curl -fL -o /opt/spark/jars/spark-token-provider-kafka-0-10_2.12-3.5.1.jar \
    https://repo1.maven.org/maven2/org/apache/spark/spark-token-provider-kafka-0-10_2.12/3.5.1/spark-token-provider-kafka-0-10_2.12-3.5.1.jar && \
  echo ">>> Installing Kafka dependency: commons-pool2..." && \
  curl -fL -o /opt/spark/jars/commons-pool2-2.12.0.jar \
    https://repo1.maven.org/maven2/org/apache/commons/commons-pool2/2.12.0/commons-pool2-2.12.0.jar && \
  echo ">>> Installing Spark Cassandra Connector (assembly)..." && \
  curl -fL -o /opt/spark/jars/spark-cassandra-connector-assembly_2.12-3.5.1.jar \
    https://repo1.maven.org/maven2/com/datastax/spark/spark-cassandra-connector-assembly_2.12/3.5.1/spark-cassandra-connector-assembly_2.12-3.5.1.jar && \
  echo ">>> Validate connector JAR presence..." && \
  test -s /opt/spark/jars/spark-cassandra-connector-assembly_2.12-3.5.1.jar && \
  SIZE=$(stat -c%s /opt/spark/jars/spark-cassandra-connector-assembly_2.12-3.5.1.jar) && \
  echo "Connector size: $SIZE bytes" && \
  if [ "$SIZE" -lt 5000000 ]; then echo "Connector JAR too small; download likely failed." && exit 1; fi && \
  (unzip -l /opt/spark/jars/spark-cassandra-connector-assembly_2.12-3.5.1.jar | grep -q 'org/apache/spark/sql/cassandra/DefaultSource.class') || \
  (echo 'DefaultSource not found inside connector JAR!'; exit 1)

# ===== Prometheus JMX Java Agent + config =====
COPY jmx/download-agent.sh /opt/jmx/download-agent.sh
COPY jmx/jmx_spark.yaml /opt/jmx/jmx_spark.yaml
RUN chmod +x /opt/jmx/download-agent.sh && /opt/jmx/download-agent.sh

# ===== Install Python dependencies =====
# Install Python 3 and pip if not already available
RUN apt-get update && apt-get install -y python3 python3-pip && rm -rf /var/lib/apt/lists/*

# Copy and install Python requirements
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

WORKDIR /opt/spark
