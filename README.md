<a id="top"></a>
<div align="center">

# `❯ Stock Prediction Pipeline`

Real-time stock prediction pipeline using **Kafka**, **Spark Structured Streaming**, **HDFS**, **Cassandra**, and a **Streamlit** dashboard – fully containerized with **Docker Compose**, instrumented with **Prometheus + Grafana**, and backed by integration tests.

<br />

<em>Built with the tools and technologies:</em>

<br />

<img src="https://img.shields.io/badge/Python-3776AB.svg?style=flat&logo=Python&logoColor=white" alt="Python" />
<img src="https://img.shields.io/badge/Apache%20Kafka-231F20.svg?style=flat&logo=Apache-Kafka&logoColor=white" alt="Kafka" />
<img src="https://img.shields.io/badge/Apache%20Spark-E25A1C.svg?style=flat&logo=apachespark&logoColor=white" alt="Spark" />
<img src="https://img.shields.io/badge/Apache%20Cassandra-1287B1.svg?style=flat&logo=apachecassandra&logoColor=white" alt="Cassandra" />
<img src="https://img.shields.io/badge/HDFS-FFB000.svg?style=flat&logo=apache&logoColor=white" alt="HDFS" />
<br />
<img src="https://img.shields.io/badge/Streamlit-FF4B4B.svg?style=flat&logo=Streamlit&logoColor=white" alt="Streamlit" />
<img src="https://img.shields.io/badge/Docker-2496ED.svg?style=flat&logo=Docker&logoColor=white" alt="Docker" />
<img src="https://img.shields.io/badge/Prometheus-E6522C.svg?style=flat&logo=Prometheus&logoColor=white" alt="Prometheus" />
<img src="https://img.shields.io/badge/Grafana-F46800.svg?style=flat&logo=Grafana&logoColor=white" alt="Grafana" />
<img src="https://img.shields.io/badge/Bash-4EAA25.svg?style=flat&logo=GNU-Bash&logoColor=white" alt="Bash" />
<img src="https://img.shields.io/badge/pandas-150458.svg?style=flat&logo=pandas&logoColor=white" alt="pandas" />
<img src="https://img.shields.io/badge/NumPy-013243.svg?style=flat&logo=NumPy&logoColor=white" alt="NumPy" />

</div>



## Table of Contents

- [Overview](#overview)
- [Architecture Overview](#architecture-overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Documentation Map](#documentation-map)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Quick Start (recommended)](#quick-start-recommended)
  - [Manual Startup (advanced)](#manual-startup-advanced)
- [Services & Ports](#services--ports)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Roadmap & Next Steps](#roadmap--next-steps)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)




## Overview

This project is a **real-time stock prediction pipeline** designed as a portfolio-grade example of:

- **Streaming ETL** with Kafka + Spark Structured Streaming  
- **Feature engineering** and **ML batch training** on Spark  
- **Data lake + feature store-style storage** (HDFS + Cassandra)  
- A simple **Streamlit dashboard** for visualization  
- **Monitoring & observability** with Prometheus + Grafana  

It is fully containerized with **Docker Compose** and comes with **operational scripts** and **documentation** so that other engineers can run, inspect, and extend it easily.



## Architecture Overview

```text
Producer (Python)  →  Kafka  →  Spark Streaming  →  HDFS (raw ticks)
                                          ↓
                                 Cassandra (features)
                                          ↓
                                 Spark Batch (ML)
                                          ↓
                                Cassandra (predictions)
                                          ↓
                                Streamlit Dashboard
````

**High-level flow:**

* A Python **producer** generates synthetic stock ticks and pushes them to **Kafka**.
* **Spark Structured Streaming**:

  * Consumes ticks from Kafka
  * Writes **raw data to HDFS** (Parquet)
  * Computes **technical indicators** (SMA-5, SMA-20) and writes **features to Cassandra**
* A **Spark batch job** trains a **Random Forest** model and writes predictions back into Cassandra.
* A **Streamlit** app visualizes predictions and features in near real-time.
* **Prometheus + Grafana** monitor Spark and service metrics.



## Features

* 🔄 **End-to-end streaming pipeline**

  * Kafka → Spark Structured Streaming → HDFS + Cassandra
* 📈 **Technical indicators**

  * SMA-5 & SMA-20 windows over recent ticks
* 🤖 **ML Batch Training**

  * Random Forest regression trained on historical features
  * Metrics like RMSE / MAE / R² recorded (see `BATCH_SUCCESS.md`)
* 📊 **Streamlit dashboard**

  * Live view of predictions and features by symbol
* 🧰 **Strong DevEx**

  * `manage.sh` and helper scripts for one-command startup
  * `.env.example` for configuration
* 📡 **Observability**

  * Prometheus scrape config + Grafana dashboard (`spark-overview.json`)
* ✅ **Testing**

  * Pytest-based integration tests under `tests/`
* 📚 **Rich documentation**

  * Separate docs for onboarding, integration, monitoring, and production-readiness



## Tech Stack

**Data & Compute**

* Apache Kafka
* Apache Spark (Structured Streaming + batch)
* HDFS
* Apache Cassandra

**Application**

* Python (producer, Spark jobs, tests)
* Streamlit (dashboard)

**Platform / Ops**

* Docker & Docker Compose
* Prometheus & Grafana
* Bash scripts for orchestration



## Documentation Map

If you’re new to the repo, follow this reading path:

1. **Overview & story**

   * [`SUMMARY.md`](SUMMARY.md) – high-level project summary
   * [`ROADMAP.md`](ROADMAP.md) – how the project is expected to evolve

2. **First run**

   * [`START_HERE.md`](START_HERE.md) – **main onboarding guide**
   * [`GETTING_STARTED.md`](GETTING_STARTED.md) – environment + detailed setup
   * [`QUICK_START_COMMANDS.txt`](QUICK_START_COMMANDS.txt) – all key commands in one place

3. **Visual expectations**

   * [`VISUAL_GUIDE.md`](VISUAL_GUIDE.md) – screenshots of dashboards and UIs
   * [`BATCH_SUCCESS.md`](BATCH_SUCCESS.md) – example batch metrics and analysis

4. **Integration & operations**

   * [`INTEGRATION_GUIDE.md`](INTEGRATION_GUIDE.md) – how to integrate this pipeline into other systems
   * [`MONITORING_ANALYSIS.md`](MONITORING_ANALYSIS.md) – Prometheus / Grafana + Spark metrics
   * [`PRODUCTION_READY.md`](PRODUCTION_READY.md) – production-readiness checklist
   * [`NEXT_STEPS.md`](NEXT_STEPS.md) – suggested improvements and extensions



## Project Structure

```text
.
├── README.md                    # You are here
├── docker-compose.yml           # Service orchestration (Kafka, Spark, HDFS, Cassandra, Streamlit, monitoring)
├── .env.example                 # Sample configuration (dev-friendly defaults)
├── BATCH_SUCCESS.md             # Example batch metrics and analysis
├── GETTING_STARTED.md           # Setup and first run (detailed)
├── INTEGRATION_GUIDE.md         # Integration with other systems
├── MONITORING_ANALYSIS.md       # Monitoring & metrics interpretation
├── NEXT_STEPS.md                # Suggested improvements
├── PRODUCTION_READY.md          # Production-readiness notes
├── QUICK_START_COMMANDS.txt     # High-level command cheatsheet
├── QUICK_TEST.sh                # Script to run tests / checks
├── ROADMAP.md                   # Roadmap & evolution
├── START_HERE.md                # Main onboarding entrypoint
├── SUMMARY.md                   # High-level summary of the project
├── VISUAL_GUIDE.md              # Screenshots and visual cues
├── init/
│   ├── cassandra-init.cql       # Keyspace + tables for features & predictions
│   ├── hdfs-bootstrap.sh        # HDFS directory setup for raw + checkpoints
│   └── kafka-create-topics.sh   # Kafka topic(s) (e.g. ticks)
├── monitoring/
│   ├── README.md
│   ├── prometheus.yml           # Prometheus scrape configuration
│   ├── spark-metrics.properties # Spark metrics → JMX bridge
│   └── grafana/
│       ├── dashboards/
│       │   └── spark-overview.json
│       └── provisioning/
│           ├── dashboards/
│           │   └── dashboards.yml
│           └── datasources/
│               └── prometheus.yml
├── scripts/
│   ├── docker-compose-wrapper.sh
│   ├── manage.sh                # Main entrypoint for starting/stopping pipeline
│   ├── reset-streaming.sh
│   ├── start-batch.sh
│   ├── start-pipeline.sh
│   ├── start-streaming.sh
│   └── stop-streaming.sh
├── services/
│   ├── producer/
│   │   ├── Dockerfile
│   │   ├── producer.py
│   │   └── requirements.txt
│   ├── spark/
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── submit.sh
│   │   ├── jmx/
│   │   │   ├── download-agent.sh
│   │   │   └── jmx_spark.yaml
│   │   └── jobs/
│   │       ├── batch_train_predict.py
│   │       ├── common.py
│   │       └── streaming_ingest.py
│   └── streamlit/
│       ├── Dockerfile
│       ├── app.py
│       └── requirements.txt
└── tests/
    ├── conftest.py
    ├── requirements.txt
    └── test_pipeline.py
```


## Configuration

Configuration is driven via environment variables. A template is provided:

```bash
cp .env.example .env
```

Then edit `.env` as needed. Typical defaults:

```bash
# Kafka
KAFKA_BOOTSTRAP=kafka:9092
TOPIC_IN=ticks

# HDFS
HDFS_URI=hdfs://namenode:8020
RAW_DIR=/data/raw/ticks
CHECKPOINT_DIR=/data/checkpoints/ingest

# Cassandra
CASSANDRA_HOST=cassandra
CASSANDRA_PORT=9042
KEYSPACE=market
TABLE_FEATURES=features
TABLE_PRED=predictions

# Streaming windows (dev-friendly)
WIN5_DURATION=15 seconds
WIN5_SLIDE=5 seconds
WIN20_DURATION=60 seconds
WIN20_SLIDE=15 seconds
WATERMARK=5 seconds
STREAM_TRIGGER=5 seconds
DRIVER_TRIGGER=20 seconds
TIME_FILTER_MINUTES=10
```

> Note: `.env` and `.env.test` are **not** committed. Only `.env.example` lives in the repo.



## Getting Started

### Prerequisites

* Docker & Docker Compose
* At least **8 GB RAM** available
* Linux / WSL2 / macOS recommended

### Quick Start (recommended)

From the repo root:

```bash
# 0. Configure environment (one time)
cp .env.example .env

# 1. Start all core services (Kafka, Spark, HDFS, Cassandra, Streamlit, monitoring, producer...)
./scripts/manage.sh start

# 2. Open the Streamlit dashboard
# Linux:
xdg-open http://localhost:8501 || true
# macOS:
open http://localhost:8501 || true

# 3. Start Spark Streaming (new terminal)
./scripts/manage.sh start-streaming

# 4. After a few minutes of data, run the batch ML job (new terminal)
./scripts/manage.sh start-batch
```

For a guided walkthrough, see:

* [`START_HERE.md`](START_HERE.md)
* [`GETTING_STARTED.md`](GETTING_STARTED.md)

### Manual Startup (advanced)

If you prefer full control:

```bash
# 1. Start the full stack
docker-compose up -d
docker-compose ps

# 2. Initialize Kafka topics
bash init/kafka-create-topics.sh

# 3. Initialize HDFS directories
bash init/hdfs-bootstrap.sh

# 4. Initialize Cassandra schema
docker exec -i cassandra cqlsh < init/cassandra-init.cql

# 5. Start Spark Streaming job
docker exec -it spark-submit bash -c "cd /opt/spark/app && /opt/spark/bin/spark-submit \
  --master spark://spark-master:7077 \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1,com.datastax.spark:spark-cassandra-connector_2.12:3.5.1 \
  --conf spark.cassandra.connection.host=cassandra \
  --conf spark.hadoop.fs.defaultFS=hdfs://namenode:8020 \
  streaming_ingest.py"

# 6. Run batch training job (after some data is collected)
docker exec -it spark-submit bash -c "cd /opt/spark/app && /opt/spark/bin/spark-submit \
  --master spark://spark-master:7077 \
  --packages com.datastax.spark:spark-cassandra-connector_2.12:3.5.1 \
  --conf spark.cassandra.connection.host=cassandra \
  --conf spark.hadoop.fs.defaultFS=hdfs://namenode:8020 \
  batch_train_predict.py"
```



## Services & Ports

| Service              | URL / Port                                     | Description                               |
| -------------------- | ---------------------------------------------- | ----------------------------------------- |
| Streamlit            | [http://localhost:8501](http://localhost:8501) | Predictions & features dashboard          |
| Spark Master UI      | [http://localhost:8080](http://localhost:8080) | Spark cluster overview                    |
| Spark Worker 1 UI    | [http://localhost:8081](http://localhost:8081) | Worker 1                                  |
| Spark Worker 2 UI    | [http://localhost:8082](http://localhost:8082) | Worker 2                                  |
| Prometheus           | [http://localhost:9090](http://localhost:9090) | Metrics scraping                          |
| Grafana              | [http://localhost:3000](http://localhost:3000) | Dashboards (`admin` / `admin` by default) |
| Kafka (internal)     | `kafka:9092`                                   | Tick ingestion                            |
| Cassandra (internal) | `cassandra:9042`                               | Features & predictions storage            |

See `MONITORING_ANALYSIS.md` for how Prometheus & Grafana are wired and how to interpret Spark metrics.



## Testing

Tests are in `tests/` and focus on core behavior and metrics.

You can run them manually or via the helper script.

### Option 1 – Manual

```bash
cd /path/to/stock-prediction-pipeline

python3 -m venv .venv
source .venv/bin/activate

# Use a dedicated env file derived from .env.example
cp .env.example .env.test  # adjust values as needed

set -a
source .env.test
set +a

pip install -r tests/requirements.txt

pytest tests/test_pipeline.py -v
```

### Option 2 – Quick test script

```bash
# From repo root
bash QUICK_TEST.sh
```

Check `BATCH_SUCCESS.md` for an example of expected ML metrics (RMSE / MAE / R²) for the batch job.



## Troubleshooting

### Spark job fails to start

* Check Spark Master logs:

  ```bash
  docker logs spark-master
  ```

* Verify workers in UI: [http://localhost:8080](http://localhost:8080)

* Check Spark submit container:

  ```bash
  docker logs spark-submit
  ```

### No data in Cassandra

* Confirm the streaming job is running and not erroring.

* Inspect Kafka:

  ```bash
  docker exec -it kafka kafka-console-consumer \
    --bootstrap-server localhost:9092 \
    --topic ticks \
    --from-beginning
  ```

* Inspect Cassandra:

  ```bash
  docker exec -it cassandra cqlsh -e "SELECT COUNT(*) FROM market.features;"
  docker exec -it cassandra cqlsh -e "SELECT COUNT(*) FROM market.predictions;"
  ```

### Streamlit shows no data

* Check that `market.predictions` has rows:

  ```bash
  docker exec -it cassandra cqlsh -e "SELECT * FROM market.predictions LIMIT 10;"
  ```

* Check Streamlit logs:

  ```bash
  docker logs streamlit
  ```

For deeper scenarios, refer to:

* [`START_HERE.md`](START_HERE.md)
* [`GETTING_STARTED.md`](GETTING_STARTED.md)
* [`MONITORING_ANALYSIS.md`](MONITORING_ANALYSIS.md)



## Roadmap & Next Steps

High-level planning and future improvements are tracked in:

* [`ROADMAP.md`](ROADMAP.md) – long-term evolution
* [`NEXT_STEPS.md`](NEXT_STEPS.md) – prioritized improvements and ideas
* [`PRODUCTION_READY.md`](PRODUCTION_READY.md) – hardening & productionization checklist

These documents cover topics such as:

* Automating Spark job submission (Airflow / Prefect / init containers)
* Health checks & readiness probes
* Advanced data validation and retries
* Model versioning and potential feature store integration
* Better security, performance tuning, and observability



## Contributing

Contributions, feedback, and ideas are welcome.

1. **Fork** the repository

2. **Create a feature branch**:

   ```bash
   git checkout -b feature/my-improvement
   ```

3. **Commit** your changes:

   ```bash
   git commit -m "Improve X / Fix Y"
   ```

4. **Push** your branch:

   ```bash
   git push origin feature/my-improvement
   ```

5. **Open a Pull Request** with a clear description and context



## License

This project is licensed under the **MIT License**.
See the [`LICENSE`](LICENSE) file (or add one) for details.



## Acknowledgments

* Apache Kafka, Spark, Cassandra, HDFS, Streamlit, Prometheus, Grafana
* The broader open-source community for the ecosystem around these tools
  
<div align="right">
  <a href="#top">
    <img src="https://img.shields.io/badge/-BACK_TO_TOP-151515?style=flat-square" alt="Back to top" />
  </a>
</div>


[back-to-top]: https://img.shields.io/badge/-BACK_TO_TOP-151515?style=flat-square
