import os
import uuid
import random
from datetime import datetime, timedelta

from dotenv import load_dotenv
load_dotenv()

import joblib
import pandas as pd
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
import base64

# ------------------------------------------------------------
# Load model (same as api/app.py)
# ------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "models", "fraud_detection_model.pkl")
model = joblib.load(MODEL_PATH)

TRANSACTION_TYPES = ["CASH_IN", "CASH_OUT", "DEBIT", "PAYMENT", "TRANSFER"]
TYPE_ENCODING = {t: i for i, t in enumerate(TRANSACTION_TYPES)}

# ------------------------------------------------------------
# Connect to Astra (same pattern as api/app.py)
# ------------------------------------------------------------
ASTRA_APPLICATION_TOKEN = os.getenv("ASTRA_APPLICATION_TOKEN")
ASTRA_SC_BUNDLE_BASE64 = os.getenv("ASTRA_SC_BUNDLE_BASE64")
CASSANDRA_KEYSPACE = os.getenv("CASSANDRA_KEYSPACE", "default_keyspace")

bundle_path = os.path.join(os.getcwd(), "temp_bundle.zip")
with open(bundle_path, "wb") as f:
    f.write(base64.b64decode(ASTRA_SC_BUNDLE_BASE64))

auth_provider = PlainTextAuthProvider(username="token", password=ASTRA_APPLICATION_TOKEN)
cluster = Cluster(cloud={"secure_connect_bundle": bundle_path}, auth_provider=auth_provider)
session = cluster.connect(CASSANDRA_KEYSPACE)

print("Connected to Astra. Generating and inserting sample transactions...")

# ------------------------------------------------------------
# Generate, score, and insert sample transactions
# ------------------------------------------------------------
NUM_SAMPLES = 200

for i in range(NUM_SAMPLES):
    tx_type = random.choice(TRANSACTION_TYPES)
    amount = round(random.uniform(10, 50000), 2)
    old_bal_org = round(random.uniform(0, 100000), 2)
    new_bal_orig = max(0, round(old_bal_org - amount, 2))
    old_bal_dest = round(random.uniform(0, 100000), 2)
    new_bal_dest = round(old_bal_dest + amount, 2)

    row = pd.DataFrame([{
        "step": random.randint(1, 720),
        "type": TYPE_ENCODING[tx_type],
        "amount": amount,
        "oldbalanceOrg": old_bal_org,
        "newbalanceOrig": new_bal_orig,
        "oldbalanceDest": old_bal_dest,
        "newbalanceDest": new_bal_dest,
        "isFlaggedFraud": 0
    }])

    prediction = int(model.predict(row)[0])

    tx_id = uuid.uuid4()
    timestamp = (datetime.now() - timedelta(minutes=random.randint(0, 10000))).isoformat()

    session.execute(
        """
        INSERT INTO transactions (id, amount, prediction, timestamp, type)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (tx_id, amount, prediction, timestamp, TYPE_ENCODING[tx_type])
    )

print(f"Inserted {NUM_SAMPLES} sample transactions into Astra.")

os.remove(bundle_path)
