"""Configuration module for the Fraud Detection Pipeline"""

import os
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
MODELS_DIR = PROJECT_ROOT / "models"
NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"

# Model configuration
MODEL_PATH = MODELS_DIR / "fraud_detection_model.pkl"
LABEL_ENCODER_PATH = MODELS_DIR / "label_encoder.pkl"

# Data configuration
RAW_DATA_PATH = DATA_DIR / "PS_20174392719_1491204439457_log.csv"
PROCESSED_DATA_PATH = DATA_DIR / "processed_transactions.parquet"

# Kafka configuration
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "fraud_detection")
KAFKA_GROUP_ID = os.getenv("KAFKA_GROUP_ID", "fraud_detection_group")

# Cassandra configuration
CASSANDRA_HOST = os.getenv("CASSANDRA_HOST", "localhost")
CASSANDRA_PORT = int(os.getenv("CASSANDRA_PORT", 9042))
CASSANDRA_KEYSPACE = os.getenv("CASSANDRA_KEYSPACE", "fraud_detection")

# API configuration
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", 8000))
API_WORKERS = int(os.getenv("API_WORKERS", 4))

# Model configuration
MODEL_THRESHOLD = float(os.getenv("MODEL_THRESHOLD", 0.5))
BATCH_SIZE = int(os.getenv("BATCH_SIZE", 32))

# Feature columns
FEATURE_COLUMNS = [
    "step", "type", "amount", "nameOrig", "oldbalanceOrig", "newbalanceOrig",
    "nameDest", "oldbalanceDest", "newbalanceDest", "isFraud", "isFlaggedFraud"
]

# Logging configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Spark configuration
SPARK_APP_NAME = "FraudDetectionPipeline"
SPARK_MASTER = os.getenv("SPARK_MASTER", "local[*]")
SPARK_MEMORY = os.getenv("SPARK_MEMORY", "4g")
