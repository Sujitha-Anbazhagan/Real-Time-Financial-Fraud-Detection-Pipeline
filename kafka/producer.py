from kafka import KafkaProducer
import pandas as pd
import json
import time


# Kafka configuration
KAFKA_SERVER = "localhost:9092"
TOPIC_NAME = "transactions"


# Create Kafka Producer
producer = KafkaProducer(
    bootstrap_servers=KAFKA_SERVER,
    value_serializer=lambda x: json.dumps(x).encode("utf-8")
)


# Dataset path
DATA_PATH = "data/PS_20174392719_1491204439457_log.csv"


print("Loading dataset...")

# Read dataset in chunks (important because file is 493 MB)
count = 0

for chunk in pd.read_csv(DATA_PATH, chunksize=1000):

    for _, row in chunk.iterrows():

        transaction = row.to_dict()

        producer.send(
            TOPIC_NAME,
            value=transaction
        )

        count += 1
        print("Sent transaction:", count)

        if count == 1000:
            break

    if count == 1000:
        break

producer.flush()

print("All transactions sent successfully!")

producer.close()