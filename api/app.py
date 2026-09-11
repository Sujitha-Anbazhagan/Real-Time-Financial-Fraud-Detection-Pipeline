from fastapi import FastAPI, HTTPException
from cassandra.cluster import Cluster
import joblib
import os
import pandas as pd
from datetime import datetime
from sklearn.preprocessing import LabelEncoder
from dotenv import load_dotenv
load_dotenv()


# ============================================================
# FastAPI Configuration
# ============================================================

app = FastAPI(
    title="Real-Time Fraud Detection API",
    description="API for real-time financial transaction fraud detection",
    version="1.0.0"
)


# ============================================================
# Project Paths
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "fraud_detection_model.pkl"
)

# ============================================================
# Cassandra / Astra DB Configuration
# ============================================================
from cassandra.auth import PlainTextAuthProvider
import base64


# ============================================================
# Cassandra / Astra DB Configuration
# ============================================================

ASTRA_APPLICATION_TOKEN = os.getenv(
    "ASTRA_APPLICATION_TOKEN"
)

ASTRA_SC_BUNDLE_BASE64 = os.getenv(
    "ASTRA_SC_BUNDLE_BASE64"
)

CASSANDRA_KEYSPACE = os.getenv(
    "CASSANDRA_KEYSPACE",
    "fraud_detection"
)


try:

    if ASTRA_SC_BUNDLE_BASE64 and ASTRA_APPLICATION_TOKEN:

        # ----------------------------------------------------
        # Recreate Astra Secure Connect Bundle from Base64
        # ----------------------------------------------------

        ASTRA_SC_BUNDLE_PATH = os.path.join(
            "/tmp",
            "secure-connect-bundle.zip"
        )

        with open(
            ASTRA_SC_BUNDLE_PATH,
            "wb"
        ) as bundle_file:

            bundle_file.write(
                base64.b64decode(
                    ASTRA_SC_BUNDLE_BASE64
                )
            )

        # ----------------------------------------------------
        # Connect to Astra DB
        # ----------------------------------------------------

        auth_provider = PlainTextAuthProvider(
            username="token",
            password=ASTRA_APPLICATION_TOKEN
        )

        cassandra_cluster = Cluster(
            cloud={
                "secure_connect_bundle":
                    ASTRA_SC_BUNDLE_PATH
            },
            auth_provider=auth_provider
        )

        cassandra_session = cassandra_cluster.connect(
            CASSANDRA_KEYSPACE
        )

        print(
            "Astra DB connection established"
        )

    else:

        # ----------------------------------------------------
        # Local Cassandra fallback
        # ----------------------------------------------------

        CASSANDRA_HOST = os.getenv(
            "CASSANDRA_HOST",
            "127.0.0.1"
        )

        CASSANDRA_PORT = int(
            os.getenv(
                "CASSANDRA_PORT",
                "9042"
            )
        )

        cassandra_cluster = Cluster(
            [CASSANDRA_HOST],
            port=CASSANDRA_PORT
        )

        cassandra_session = cassandra_cluster.connect(
            CASSANDRA_KEYSPACE
        )

        print(
            "Local Cassandra connection established"
        )


except Exception as e:

    cassandra_cluster = None
    cassandra_session = None

    print(
        f"Cassandra connection error: {e}"
    )
# ============================================================
# Load Label Encoder
# ============================================================

def load_label_encoder():

    encoder_candidates = [
        os.path.join(
            BASE_DIR,
            "models",
            "label_encoder.pkl"
        ),
        os.path.join(
            BASE_DIR,
            "models",
            "label_encoders.pkl"
        ),
    ]

    for candidate in encoder_candidates:

        if os.path.exists(candidate):

            encoder = joblib.load(candidate)

            if isinstance(encoder, dict):

                if "type" in encoder:
                    return encoder["type"]

                if encoder:
                    return next(
                        iter(
                            encoder.values()
                        )
                    )

            return encoder

    # Fallback encoder
    encoder = LabelEncoder()

    encoder.fit([
        "CASH_IN",
        "CASH_OUT",
        "DEBIT",
        "PAYMENT",
        "TRANSFER"
    ])

    return encoder


# ============================================================
# Load Model and Encoder
# ============================================================

try:

    model = joblib.load(
        MODEL_PATH
    )

    label_encoder = load_label_encoder()

    print("Fraud detection model loaded")
    print("Label encoder loaded")

except Exception as e:

    model = None
    label_encoder = None

    print(
        f"Model loading error: {e}"
    )


# ============================================================
# HOME
# ============================================================

@app.get("/")
def home():

    return {
        "message": "Fraud Detection API is running",
        "status": "healthy",
        "version": "1.0.0"
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health_check():

    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "encoder_loaded": label_encoder is not None,
        "cassandra_connected": cassandra_session is not None
    }


# ============================================================
# FRAUD PREDICTION
# ============================================================

@app.post("/predict")
def predict(transaction: dict):

    if model is None:

        raise HTTPException(
            status_code=503,
            detail="Fraud detection model is not loaded"
        )

    try:

        # ----------------------------------------------------
        # Convert incoming JSON into DataFrame
        # ----------------------------------------------------

        data = pd.DataFrame(
            [transaction]
        ).copy()

        # ----------------------------------------------------
        # Normalize transaction type
        # ----------------------------------------------------

        if "type" not in data.columns:

            raise HTTPException(
                status_code=400,
                detail="Transaction type is required"
            )

        data["type"] = (
            data["type"]
            .astype(str)
            .str.upper()
            .str.strip()
        )

        try:

            data["type"] = label_encoder.transform(
                data["type"]
            )

        except ValueError as e:

            raise HTTPException(
                status_code=400,
                detail=f"Invalid transaction type: {e}"
            )

        # ----------------------------------------------------
        # Model features
        # ----------------------------------------------------

        features = [
            "step",
            "type",
            "amount",
            "oldbalanceOrg",
            "newbalanceOrig",
            "oldbalanceDest",
            "newbalanceDest",
            "isFlaggedFraud"
        ]

        # ----------------------------------------------------
        # Check missing columns
        # ----------------------------------------------------

        missing_columns = [
            column
            for column in features
            if column not in data.columns
        ]

        if missing_columns:

            raise HTTPException(
                status_code=400,
                detail={
                    "message": "Missing required columns",
                    "missing_columns": missing_columns
                }
            )

        # ----------------------------------------------------
        # Make prediction
        # ----------------------------------------------------

        prediction = int(
            model.predict(
                data[features]
            )[0]
        )

        # ----------------------------------------------------
        # Get fraud probability
        # ----------------------------------------------------

        if hasattr(
            model,
            "predict_proba"
        ):

            probabilities = model.predict_proba(
                data[features]
            )[0]

            fraud_probability = float(
                probabilities[1]
            )

        else:

            fraud_probability = None

        # ----------------------------------------------------
        # Determine prediction result
        # ----------------------------------------------------

        result = (
            "Fraud"
            if prediction == 1
            else "Normal"
        )

        # ----------------------------------------------------
        # Determine risk level
        # ----------------------------------------------------

        if fraud_probability is None:

            risk = "Unknown"

        elif fraud_probability >= 0.70:

            risk = "High"

        elif fraud_probability >= 0.30:

            risk = "Medium"

        else:

            risk = "Low"

        # ----------------------------------------------------
        # Calculate confidence
        # ----------------------------------------------------

        confidence = None

        if fraud_probability is not None:

            confidence = (
                fraud_probability
                if prediction == 1
                else 1 - fraud_probability
            )

        # ----------------------------------------------------
        # Final API response
        # ----------------------------------------------------

        response = {
            "prediction": result,
            "risk": risk,
            "fraud_probability": (
                round(
                    fraud_probability,
                    4
                )
                if fraud_probability is not None
                else None
            ),
            "confidence": (
                round(
                    confidence,
                    4
                )
                if confidence is not None
                else None
            ),
            "timestamp": datetime.now().isoformat()
        }

        return response

    except HTTPException:

        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Prediction error: {str(e)}"
        )


# ============================================================
# GET TRANSACTIONS FROM CASSANDRA
# ============================================================

@app.get("/transactions")
def get_transactions(limit: int = 50):

    if cassandra_session is None:

        raise HTTPException(
            status_code=503,
            detail="Cassandra is not connected"
        )

    try:

        # ----------------------------------------------------
        # Prevent very large queries
        # ----------------------------------------------------

        limit = max(
            1,
            min(limit, 100)
        )

        # ----------------------------------------------------
        # Query Cassandra
        # ----------------------------------------------------

        query = f"""
        SELECT
            id,
            amount,
            prediction,
            timestamp,
            type
        FROM transactions
        LIMIT {limit}
        """

        rows = cassandra_session.execute(
            query
        )

        # ----------------------------------------------------
        # Convert Cassandra rows to JSON
        # ----------------------------------------------------

        transactions = []

        for row in rows:

            transactions.append(
                {
                    "id": str(row.id),
                    "amount": float(row.amount),
                    "prediction": int(row.prediction),
                    "timestamp": str(row.timestamp),
                    "type": int(row.type)
                }
            )

        return {
            "count": len(transactions),
            "transactions": transactions
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}"
        )


# ============================================================
# TRANSACTION STATISTICS
# ============================================================

@app.get("/stats")
def get_stats():

    if cassandra_session is None:

        raise HTTPException(
            status_code=503,
            detail="Cassandra is not connected"
        )

    try:

        # ----------------------------------------------------
        # Query transactions
        # ----------------------------------------------------

        query = """
        SELECT
            amount,
            prediction,
            type,
            timestamp
        FROM transactions
        """

        rows = cassandra_session.execute(
            query
        )

        transactions = list(rows)

        # ----------------------------------------------------
        # Calculate statistics
        # ----------------------------------------------------

        total_transactions = len(
            transactions
        )

        fraud_transactions = sum(
            1
            for row in transactions
            if row.prediction == 1
        )

        normal_transactions = (
            total_transactions
            - fraud_transactions
        )

        total_amount = sum(
            float(row.amount)
            for row in transactions
            if row.amount is not None
        )

        fraud_amount = sum(
            float(row.amount)
            for row in transactions
            if (
                row.amount is not None
                and row.prediction == 1
            )
        )

        fraud_rate = (
            fraud_transactions / total_transactions
            if total_transactions > 0
            else 0
        )

        # ----------------------------------------------------
        # Return statistics
        # ----------------------------------------------------

        return {
            "total_transactions": total_transactions,
            "fraud_transactions": fraud_transactions,
            "normal_transactions": normal_transactions,
            "fraud_rate": round(
                fraud_rate,
                4
            ),
            "total_amount": round(
                total_amount,
                2
            ),
            "fraud_amount": round(
                fraud_amount,
                2
            )
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}"
        )
    
