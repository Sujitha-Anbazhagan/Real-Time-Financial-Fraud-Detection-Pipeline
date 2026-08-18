# Real-Time Financial Fraud Detection Pipeline

## Project Documentation

---

## 1. Project Overview

The **Real-Time Financial Fraud Detection Pipeline** is an end-to-end machine learning and data engineering project designed to detect potentially fraudulent financial transactions in real time.

The system receives transaction data through **Apache Kafka**, processes the streaming data using **Apache Spark Structured Streaming**, applies a trained **Random Forest machine learning model** for fraud prediction, stores the results in **Apache Cassandra**, and exposes the processed data through a **FastAPI backend**.

A **Streamlit dashboard** provides a visual representation of transaction statistics and detected fraud cases.

---

## 2. Project Objective

The main objective is to develop a real-time fraud detection pipeline that can:

- Stream financial transactions continuously.
- Process streaming transactions using Apache Spark.
- Predict fraudulent transactions using machine learning.
- Store transaction and prediction results in Cassandra.
- Provide transaction statistics through REST APIs.
- Visualize fraud detection results through a dashboard.
- Demonstrate an end-to-end real-time data processing workflow.

---

## 3. Problem Statement

Financial institutions process a large number of transactions every day. Detecting fraudulent transactions manually or through batch-only processing can delay fraud identification.

This project addresses the problem by implementing a real-time pipeline where transactions are continuously streamed, processed, classified, stored, and visualized.

The system aims to provide faster identification of potentially fraudulent transactions and a centralized view of fraud-related statistics.

---

## 4. Technologies Used

| Technology | Purpose |
|---|---|
| Python | Core programming and machine learning |
| Pandas | Data processing |
| Scikit-learn | Machine learning model |
| Apache Kafka | Real-time transaction streaming |
| Apache Spark | Stream processing |
| PySpark | Python interface for Spark |
| Apache Cassandra | NoSQL transaction storage |
| FastAPI | Backend REST API |
| Streamlit | Interactive dashboard |
| Docker | Containerized infrastructure |
| Git & GitHub | Version control |

---

## 5. Dataset

The project uses the **PaySim financial transaction dataset**.

The dataset contains simulated financial transactions with information such as:

- Transaction type
- Transaction amount
- Fraud indicator
- Transaction-related attributes

The dataset is used for model training and for simulating a continuous stream of financial transactions through Kafka.

---

## 6. System Architecture

The overall architecture of the project is:

```text
                 PaySim Dataset
                       |
                       v
               Kafka Producer
                       |
                       v
                Apache Kafka
                       |
                       v
          Spark Structured Streaming
                       |
                       v
             Feature Processing
                       |
                       v
          Random Forest ML Model
                       |
             +---------+---------+
             |                   |
             v                   v
       Prediction = 0      Prediction = 1
          Normal              Fraud
             |                   |
             +---------+---------+
                       |
                       v
                Apache Cassandra
                       |
                       v
                   FastAPI
                       |
                       v
              Streamlit Dashboard