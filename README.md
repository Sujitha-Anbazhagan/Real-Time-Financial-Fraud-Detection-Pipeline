# Real-Time Financial Fraud Detection Pipeline

An end-to-end real-time fraud detection system that processes financial transactions using **Apache Kafka, Spark Structured Streaming, Machine Learning, Cassandra, FastAPI, and Streamlit**.

## Architecture

```text
Transaction Data
      ↓
Kafka Producer
      ↓
Apache Kafka
      ↓
Spark Structured Streaming
      ↓
ML Fraud Detection Model
      ↓
Apache Cassandra
      ↓
FastAPI
      ↓
Streamlit Dashboard
```

## Key Features

* Real-time transaction streaming with Apache Kafka
* Stream processing using Apache Spark
* Fraud prediction using Random Forest
* Transaction storage with Cassandra
* REST API using FastAPI
* Interactive dashboard using Streamlit
* Docker-based infrastructure

## Tech Stack

**Python · Apache Kafka · Apache Spark · Scikit-learn · Cassandra · FastAPI · Streamlit · Docker**

## Model Performance

| Metric    |  Score |
| --------- | -----: |
| Accuracy  | 99.97% |
| Precision |    98% |
| Recall    |    79% |
| F1-Score  |    87% |

**Model:** Random Forest Classifier

## Project Structure

```text
├── api/            # FastAPI backend
├── dashboard/      # Streamlit dashboard
├── kafka/          # Kafka producer
├── models/         # Trained ML model
├── notebooks/      # Data analysis & model development
├── streaming/      # Spark streaming pipeline
├── docker/         # Docker configuration
├── requirements.txt
└── README.md
```

## Run Locally

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Start Docker services

```bash
docker compose -f docker/docker-compose.yml up -d
```

### 3. Start Kafka Producer

```bash
python kafka/producer.py
```

### 4. Start Spark Streaming

```bash
spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.9,com.datastax.spark:spark-cassandra-connector_2.12:3.5.0 streaming/spark_fraud_stream.py
```

### 5. Start FastAPI

```bash
uvicorn api.app:app --reload --port 8000
```

### 6. Start Streamlit

```bash
streamlit run dashboard/app.py
```

## Results

The pipeline successfully streams transactions, generates real-time fraud predictions, stores results in Cassandra, and visualizes fraud analytics through the dashboard.

## Future Enhancements

* Real-time fraud alerts
* Cloud deployment
* Prometheus & Grafana monitoring
* Automated model retraining
* Model performance monitoring

## Author

**Sujitha Anbazhagan**
MCA Graduate | Aspiring Data Analyst / Data Engineer
