# tests/conftest.py
import os
import json
from datetime import datetime, timezone

import pytest
from dotenv import load_dotenv
from kafka import KafkaProducer
from cassandra.cluster import Cluster

# Force .env.test to override anything in your shell
load_dotenv(dotenv_path=os.path.join(os.getcwd(), ".env.test"), override=True)

@pytest.fixture(scope="session")
def cfg():
    return {
        "kafka_bootstrap": os.environ["KAFKA_BOOTSTRAP"],   # e.g. localhost:29092
        "topic": os.environ["TOPIC"],                       # ticks
        "cassandra_host": os.environ["CASSANDRA_HOST"],     # localhost
        "keyspace": os.environ["KEYSPACE"],                 # market
        "features_table": os.environ["FEATURES_TABLE"],     # features
        "prom": os.environ["PROM"],                         # http://localhost:9090
        "driver_instance": os.environ.get("DRIVER_INSTANCE", "spark-submit:8092"),
    }

@pytest.fixture(scope="session")
def kafka_producer(cfg):
    prod = KafkaProducer(
        bootstrap_servers=cfg["kafka_bootstrap"],
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        linger_ms=0,
        acks="all",
    )
    yield prod
    prod.flush(5)
    prod.close()

@pytest.fixture(scope="session")
def cassandra_session(cfg):
    cluster = Cluster([cfg["cassandra_host"]])
    session = cluster.connect(cfg["keyspace"])
    yield session
    session.shutdown()
    cluster.shutdown()

def iso_utc(ts: float) -> str:
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
