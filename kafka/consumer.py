from kafka import KafkaConsumer
import json


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


# Receive messages
for message in consumer:

    transaction = message.value

    print(transaction)
