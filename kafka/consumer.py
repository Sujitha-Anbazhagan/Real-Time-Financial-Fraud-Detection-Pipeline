from kafka import KafkaConsumer
import json

from fraud_predictor import predict_fraud


# Kafka configuration

KAFKA_SERVER = "localhost:9092"
TOPIC_NAME = "transactions"


# Create Kafka Consumer

consumer = KafkaConsumer(
    TOPIC_NAME,
    bootstrap_servers=[KAFKA_SERVER],
    auto_offset_reset="earliest",
    enable_auto_commit=True,
    value_deserializer=lambda x: json.loads(x.decode("utf-8"))
)


print("Listening for transactions...")


# Receive transactions

for message in consumer:

    transaction = message.value


    print("=" * 60)
    print("Transaction Received")
    print("=" * 60)


    print("Step:", transaction["step"])
    print("Type:", transaction["type"])
    print("Amount:", transaction["amount"])
    print("Sender:", transaction["nameOrig"])
    print("Receiver:", transaction["nameDest"])


    # Model Prediction

    result = predict_fraud(transaction)


    print("\nPrediction Result")
    print("------------------")
    print("Status:", result["status"])
    print("Fraud Probability:", result["fraud_probability"])


    if result["prediction"] == 1:
        print("🚨 FRAUD TRANSACTION DETECTED")
    else:
        print("✅ NORMAL TRANSACTION")


    if "timestamp" in transaction:
        print("Timestamp:", transaction["timestamp"])


    print()