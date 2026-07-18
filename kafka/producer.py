from kafka import KafkaProducer
import pandas as pd
import json
import time
from datetime import datetime


KAFKA_SERVER = "localhost:9092"
TOPIC_NAME = "transactions"

DATA_PATH = "data/PS_20174392719_1491204439457_log.csv"


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


        print(
            "Sent transaction:",
            count
        )


        time.sleep(1)