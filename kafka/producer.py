from kafka import KafkaProducer
import pandas as pd
import json
import time
from datetime import datetime
import random
from pathlib import Path


KAFKA_SERVER = "localhost:9092"
TOPIC_NAME = "transactions"


BASE_DIR = Path(__file__).resolve().parents[1]

DATA_PATH = (
    BASE_DIR
    / "data"
    / "PS_20174392719_1491204439457_log.csv"
)


producer = KafkaProducer(
    bootstrap_servers=KAFKA_SERVER,
    value_serializer=lambda x: json.dumps(x).encode("utf-8")
)


print("Loading PaySim dataset...")


df = pd.read_csv(
    DATA_PATH,
    chunksize=1000
)


count = 0


print("Starting transaction stream...")


for chunk in df:

    for _, row in chunk.iterrows():

        transaction = row.to_dict()

        transaction["timestamp"] = str(datetime.now())


        producer.send(
            TOPIC_NAME,
            value=transaction
        )


        count += 1


        print("=" * 60)
        print(f"Transaction #{count}")
        print(f"Type   : {transaction['type']}")
        print(f"Amount : {transaction['amount']}")
        print(f"Fraud  : {transaction['isFraud']}")
        print("=" * 60)


        time.sleep(random.uniform(0.5, 2))


producer.flush()

print("All transactions sent successfully!")

producer.close()