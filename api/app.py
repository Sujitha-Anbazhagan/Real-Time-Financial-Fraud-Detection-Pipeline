from fastapi import FastAPI
import joblib
import os
import pandas as pd
from sklearn.preprocessing import LabelEncoder


app = FastAPI(
    title="Real-Time Fraud Detection API",
    version="1.0"
)


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "models", "fraud_detection_model.pkl")


def load_label_encoder():
    encoder_candidates = [
        os.path.join(BASE_DIR, "models", "label_encoder.pkl"),
        os.path.join(BASE_DIR, "models", "label_encoders.pkl"),
    ]

    for candidate in encoder_candidates:
        if os.path.exists(candidate):
            encoder = joblib.load(candidate)
            if isinstance(encoder, dict):
                if "type" in encoder:
                    return encoder["type"]
                if encoder:
                    return next(iter(encoder.values()))
            return encoder

    encoder = LabelEncoder()
    encoder.fit(["CASH_IN", "CASH_OUT", "DEBIT", "PAYMENT", "TRANSFER"])
    return encoder


model = joblib.load(MODEL_PATH)
label_encoder = load_label_encoder()


@app.get("/")
def home():
    return {
        "message": "Fraud Detection API is running"
    }


@app.post("/predict")
def predict(transaction: dict):
    data = pd.DataFrame([transaction]).copy()

    if "type" in data.columns and not pd.api.types.is_numeric_dtype(data["type"]):
        data["type"] = data["type"].astype(str).str.upper()
        data["type"] = label_encoder.transform(data["type"])

    features = [
        "step",
        "type",
        "amount",
        "oldbalanceOrg",
        "newbalanceOrig",
        "oldbalanceDest",
        "newbalanceDest",
        "isFlaggedFraud",
    ]

    missing_columns = [col for col in features if col not in data.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns for prediction: {missing_columns}")

    prediction = int(model.predict(data[features])[0])
    result = "Fraud" if prediction == 1 else "Normal"

    return {
        "prediction": result,
        "risk": "High" if result == "Fraud" else "Low"
    }
