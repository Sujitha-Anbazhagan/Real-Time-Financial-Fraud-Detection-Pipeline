# Project Report

## Real-Time Financial Fraud Detection Pipeline

### Intern
Sujitha A

### Project
Real-Time Financial Fraud Detection Pipeline

---

## 1. Project Introduction

The project focuses on developing a real-time financial fraud detection system using machine learning and real-time data processing technologies.

The system receives financial transactions through Apache Kafka, processes them using Apache Spark Structured Streaming, predicts fraudulent transactions using a Random Forest model, stores the results in Apache Cassandra, and displays analytics through a FastAPI backend and Streamlit dashboard.

---

## 2. Project Objective

The primary objective is to build an end-to-end pipeline capable of processing financial transactions in real time and identifying potentially fraudulent transactions using machine learning.

---

## 3. Technologies Used

- Python
- Apache Kafka
- Apache Spark Structured Streaming
- PySpark
- Scikit-learn
- Random Forest
- Apache Cassandra
- FastAPI
- Streamlit
- Docker
- Git & GitHub

---

## 4. Work Completed

### Machine Learning

- Prepared the PaySim transaction dataset.
- Performed data preprocessing.
- Trained a Random Forest fraud detection model.
- Evaluated model performance.
- Saved the trained model for real-time prediction.

### Real-Time Data Pipeline

- Configured Apache Kafka.
- Created the transaction Kafka topic.
- Developed the Kafka producer.
- Integrated Kafka with Spark Structured Streaming.
- Processed streaming transaction data.
- Integrated the trained ML model with Spark.

### Database

- Configured Apache Cassandra.
- Created the `fraud_detection` keyspace.
- Created the `transactions` table.
- Stored transaction predictions and timestamps.
- Verified fraudulent transactions in Cassandra.

### Backend

- Developed a FastAPI backend.
- Implemented transaction and statistics APIs.
- Connected FastAPI with Cassandra.
- Tested the `/stats` API successfully.

### Dashboard

- Developed a Streamlit dashboard.
- Connected the dashboard to the FastAPI backend.
- Displayed transaction statistics and fraud metrics.

---

## 5. Current System Workflow

Transaction Dataset
        ↓
Kafka Producer
        ↓
Apache Kafka
        ↓
Spark Structured Streaming
        ↓
Random Forest Model
        ↓
Fraud / Normal Prediction
        ↓
Apache Cassandra
        ↓
FastAPI
        ↓
Streamlit Dashboard

---

## 6. Current Results

The complete pipeline has been tested successfully.

Example API results during testing:

- Total Transactions: 15,397
- Fraud Transactions: 103
- Normal Transactions: 15,294
- Fraud Rate: 0.67%

The transaction count continues to change as new transactions are processed.

---

## 7. Key Achievements

- Developed an end-to-end real-time fraud detection pipeline.
- Integrated Kafka and Spark Structured Streaming.
- Integrated machine learning with streaming data.
- Successfully stored predictions in Cassandra.
- Developed REST APIs using FastAPI.
- Developed a Streamlit dashboard.
- Successfully tested the complete pipeline.
- Verified fraud predictions directly from Cassandra.

---

## 8. Challenges Faced

During development, the following challenges were encountered:

- Spark and Kafka connector configuration.
- Python worker connection issues in Spark.
- Windows-specific Spark filesystem configuration.
- Cassandra query timeout with large datasets.
- Managing multiple services during end-to-end testing.

---

## 9. Solutions Implemented

- Configured the required Spark Kafka connector.
- Configured Spark and Java environment variables.
- Configured the Python virtual environment for Spark.
- Adjusted Spark networking and local execution settings.
- Configured Cassandra integration.
- Tested individual components before performing end-to-end testing.

---

## 10. Current Project Status

The core real-time fraud detection pipeline is completed and operational.

The following components are currently working:

- Kafka transaction streaming
- Spark Structured Streaming
- Machine learning prediction
- Cassandra storage
- FastAPI backend
- Streamlit dashboard

---

## 11. Next Phase

The next phase will focus on:

- Performance and load testing.
- Measuring processing latency.
- Optimizing database queries.
- Improving dashboard analytics.
- Adding monitoring and alerting.
- Preparing the final project documentation.
- Final GitHub cleanup and project presentation.

---

## 12. Conclusion

The project has successfully progressed from machine learning model development to a complete real-time fraud detection pipeline.

The integration of Kafka, Spark, machine learning, Cassandra, FastAPI, and Streamlit demonstrates an end-to-end real-time data processing architecture.

The next phase will focus on optimization, monitoring, documentation, and final project preparation.