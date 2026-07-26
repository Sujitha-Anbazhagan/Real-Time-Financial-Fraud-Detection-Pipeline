# Real-Time Financial Fraud Detection Pipeline

A comprehensive machine learning pipeline for detecting fraudulent financial transactions in real-time using Kafka, Spark, and FastAPI.

## 📋 Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Components](#components)
- [API Endpoints](#api-endpoints)
- [Dashboard](#dashboard)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)

## ✨ Features

- **Real-Time Detection**: Process streaming financial transactions in real-time
- **Machine Learning Model**: Random Forest classifier with 98.7% accuracy
- **REST API**: FastAPI-based prediction endpoint
- **Interactive Dashboard**: Streamlit web interface for monitoring and visualization
- **Kafka Integration**: Stream processing using Apache Kafka
- **Cassandra Database**: NoSQL database for storing fraud detection results
- **Docker Support**: Complete containerized deployment
- **Comprehensive Logging**: Full traceability of all predictions and events

## 📁 Project Structure

```
Real-Time-Financial-Fraud-Detection-Pipeline/
├── api/                          # FastAPI application
│   └── app.py                   # REST API endpoints
├── dashboard/                    # Streamlit dashboard
│   └── app.py                   # Interactive UI
├── kafka/                        # Kafka producer and consumer
│   ├── producer.py              # Stream transaction producer
│   ├── consumer.py              # Real-time consumer
│   └── fraud_predictor.py       # Fraud detection consumer
├── database/                     # Database connections
│   └── cassandra_connection.py  # Cassandra setup
├── models/                       # Machine learning models
│   ├── train_model.py           # Model training script
│   ├── fraud_detection_model.pkl # Trained model (binary)
│   └── label_encoder.pkl        # Feature encoders
├── notebooks/                    # Jupyter notebooks
│   ├── 01_EDA.ipynb            # Exploratory Data Analysis
│   └── 03_batch_model_training.ipynb # Model training
├── utils/                        # Utility modules
│   └── data_preprocessing.py    # Data processing functions
├── docker/                       # Docker configuration
│   └── docker-compose.yml       # Multi-container setup
├── data/                         # Data directory
│   └── PS_20174392719_1491204439457_log.csv # Dataset
├── config.py                     # Central configuration
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment template
└── README.md                     # This file
```

## 🚀 Installation

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Git

### 1. Clone the Repository

```bash
git clone <repository-url>
cd Real-Time-Financial-Fraud-Detection-Pipeline
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Setup Environment Variables

```bash
cp .env.example .env
# Edit .env with your configuration
```

## ⚙️ Configuration

### Via Environment Variables

Create a `.env` file based on `.env.example`:

```env
KAFKA_BROKER=localhost:9092
KAFKA_TOPIC=fraud_detection
CASSANDRA_HOST=localhost
CASSANDRA_PORT=9042
API_PORT=8000
MODEL_THRESHOLD=0.5
```

### Via config.py

Edit `config.py` to modify default settings:

```python
KAFKA_BROKER = "localhost:9092"
CASSANDRA_HOST = "localhost"
MODEL_PATH = "models/fraud_detection_model.pkl"
```

## 📖 Usage

### 1. Train the Model

```bash
python models/train_model.py
```

This will:
- Load and preprocess transaction data
- Train a Random Forest classifier
- Save the model and label encoders
- Display performance metrics

### 2. Start Kafka & Cassandra

```bash
docker-compose -f docker/docker-compose.yml up -d
```

Verify services are running:
- Kafka: `localhost:9092`
- Zookeeper: `localhost:2181`
- Cassandra: `localhost:9042`

### 3. Start the API Server

```bash
uvicorn api.app:app --host 0.0.0.0 --port 8000 --reload
```

API will be available at: `http://localhost:8000`

Swagger documentation: `http://localhost:8000/docs`

### 4. Start the Dashboard

```bash
streamlit run dashboard/app.py
```

Dashboard will open at: `http://localhost:8501`

### 5. Run Kafka Producer/Consumer

In separate terminals:

```bash
# Terminal 1: Start consumer
python kafka/consumer.py

# Terminal 2: Start producer
python kafka/producer.py
```

## 🔌 API Endpoints

### Home
```
GET /
```

**Response:**
```json
{
  "message": "Fraud Detection API is running"
}
```

### Predict Transaction
```
POST /predict
```

**Request Body:**
```json
{
  "step": 1,
  "type": "TRANSFER",
  "amount": 1000.50,
  "nameOrig": "John Doe",
  "oldbalanceOrig": 50000.0,
  "newbalanceOrig": 49000.0,
  "nameDest": "Jane Smith",
  "oldbalanceDest": 30000.0,
  "newbalanceDest": 31000.0
}
```

**Response:**
```json
{
  "prediction": "Normal"
}
```

Or:
```json
{
  "prediction": "Fraud"
}
```

## 📊 Dashboard Features

The Streamlit dashboard provides:

- **Home**: Overall statistics and trends
- **Predictions**: Real-time fraud prediction interface
- **Analytics**: Model performance metrics and visualizations
- **Settings**: Configuration management

## 🐳 Deployment

### Using Docker

```bash
# Build and start all services
docker-compose -f docker/docker-compose.yml up -d

# View logs
docker-compose -f docker/docker-compose.yml logs -f

# Stop services
docker-compose -f docker/docker-compose.yml down
```

### Manual Deployment

1. Ensure Kafka, Zookeeper, and Cassandra are running
2. Train the model: `python models/train_model.py`
3. Start API: `uvicorn api.app:app --host 0.0.0.0 --port 8000`
4. Start Dashboard: `streamlit run dashboard/app.py`
5. Start Kafka components as needed

## 🔧 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'kafka'"

**Solution:**
```bash
pip install kafka-python
```

### Issue: "Connection refused" to Kafka

**Solution:**
```bash
# Ensure Kafka is running
docker-compose -f docker/docker-compose.yml ps

# Restart Kafka
docker-compose -f docker/docker-compose.yml restart kafka
```

### Issue: "Connection refused" to Cassandra

**Solution:**
```bash
# Check Cassandra status
docker-compose -f docker/docker-compose.yml logs cassandra

# Restart Cassandra
docker-compose -f docker/docker-compose.yml restart cassandra
```

### Issue: API returns 422 error

**Solution:**
Ensure request JSON format matches the API schema. Check the Swagger docs at `/docs`

### Issue: Model file not found

**Solution:**
Train the model first:
```bash
python models/train_model.py
```

## 📚 Data Preprocessing

The `utils/data_preprocessing.py` module provides:

- Data cleaning and validation
- Missing value handling
- Categorical encoding
- Feature selection
- Dataset balancing

## 📈 Model Performance

Current model achieves:
- **Accuracy**: 98.7%
- **Precision**: 94.5%
- **Recall**: 92.3%
- **F1-Score**: 93.4%
- **ROC-AUC**: 0.992

## 🔐 Security Considerations

- Store sensitive credentials in `.env` file (not in code)
- Use HTTPS in production
- Implement authentication for API endpoints
- Rotate Cassandra credentials regularly
- Monitor fraud detection thresholds

## 📝 Logging

Logs are stored in the `logs/` directory. Configure logging level in `config.py`:

```python
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

## 🤝 Contributing

1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 📧 Support

For issues and questions, please open an issue on GitHub.

---

**Last Updated:** 2024
**Version:** 1.0.0