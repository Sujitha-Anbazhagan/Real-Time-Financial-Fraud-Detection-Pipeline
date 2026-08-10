import joblib
import os

import pandas as pd
from sklearn.preprocessing import LabelEncoder


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "fraud_detection_model.pkl"
)


def load_label_encoder():
    encoder_candidates = [
        os.path.join(BASE_DIR, "models", "label_encoder.pkl"),
        os.path.join(BASE_DIR, "models", "label_encoders.pkl"),
    ]

    for encoder_path in encoder_candidates:
        if os.path.exists(encoder_path):
            encoder = joblib.load(encoder_path)

            if isinstance(encoder, dict):
                if "type" in encoder:
                    return encoder["type"]

                if encoder:
                    return next(iter(encoder.values()))

            return encoder

    encoder = LabelEncoder()
    encoder.fit([
        "CASH_IN",
        "CASH_OUT",
        "DEBIT",
        "PAYMENT",
        "TRANSFER"
    ])

    return encoder


# Load model and encoder
model = joblib.load(MODEL_PATH)
label_encoder = load_label_encoder()


def predict_fraud(transaction):
    data = pd.DataFrame([transaction]).copy()

    # Encode transaction type
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

    missing_columns = [
        col for col in features
        if col not in data.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns for prediction: {missing_columns}"
        )

    data = data[features]

    # Prediction
    prediction = int(model.predict(data)[0])

    # Fraud probability
    fraud_probability = None

    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba(data)[0]

        # Find probability corresponding to class 1 (fraud)
        if 1 in model.classes_:
            fraud_class_index = list(model.classes_).index(1)
            fraud_probability = float(probabilities[fraud_class_index])

    return {
        "prediction": prediction,
        "fraud_probability": fraud_probability,
        "status": "FRAUD" if prediction == 1 else "NORMAL",
    }