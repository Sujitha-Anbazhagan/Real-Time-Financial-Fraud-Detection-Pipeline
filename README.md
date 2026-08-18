# 🔐 Real-Time Financial Fraud Detection Pipeline

An end-to-end real-time fraud detection system that streams financial transactions through Kafka, processes them with Spark Structured Streaming, predicts fraud using Machine Learning, stores results in Cassandra, and visualizes analytics through FastAPI and Streamlit.

## Architecture

```text
PaySim Dataset
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

## Features

- Real-time transaction streaming with Apache Kafka
- Stream processing with Apache Spark Structured Streaming
- Fraud prediction using a Random Forest model
- Transaction storage in Apache Cassandra
- REST API built with FastAPI
- Interactive analytics dashboard using Streamlit
- Fraud statistics and transaction analytics

## Tech Stack

**Python · Apache Kafka · Apache Spark · Scikit-learn · Cassandra · FastAPI · Streamlit · Docker**

## Project Structure

```text
├── api/             # FastAPI backend
├── dashboard/       # Streamlit dashboard
├── data/            # PaySim dataset
├── kafka/           # Producer and consumer
├── models/          # Trained ML model
├── notebooks/       # Model training
├── streaming/       # Spark streaming pipeline
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Model Performance

| Metric | Score |
|---|---:|
| Accuracy | 99.97% |
| Fraud Precision | 98% |
| Fraud Recall | 79% |
| Fraud F1-Score | 87% |

**Model:** Random Forest Classifier

## Getting Started

### 1. Clone and install

```bash
git clone <repository-url>
cd Real-Time-Financial-Fraud-Detection-Pipeline
pip install -r requirements.txt
```

### 2. Start infrastructure

```bash
docker compose up -d
```

### 3. Start Kafka Producer

```bash
python kafka/producer.py
```

### 4. Start Spark Streaming

```bash
spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.9,com.datastax.spark:spark-cassandra-connector_2.12:3.5.1 streaming/spark_fraud_stream.py
```

### 5. Start FastAPI

```bash
uvicorn api.app:app --reload --port 8000
```

API Docs: `http://localhost:8000/docs`

### 6. Start Dashboard

```bash
streamlit run dashboard/app.py
```

## API

| Method | Endpoint | Description |
|---|---|---|
| GET | `/stats` | Fraud statistics |
| GET | `/transactions` | Transaction data |
| POST | `/predict` | Fraud prediction |

## Results

The pipeline successfully processes real-time transactions, predicts fraudulent activity, stores predictions in Cassandra, and displays fraud analytics through an interactive dashboard.

## Future Improvements

- Real-time fraud alerts
- Prometheus and Grafana monitoring
- Model performance monitoring
- Automated model retraining
- Cloud deployment

## Author

**Sujitha A**  
MCA Graduate | Aspiring Data Analyst / Data Engineer