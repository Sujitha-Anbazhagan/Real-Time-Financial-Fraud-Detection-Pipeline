from fastapi import FastAPI, HTTPException
import joblib
import os
import pandas as pd
from sklearn.preprocessing import LabelEncoder

app = FastAPI(
    title="Real-Time Fraud Detection API",
    description="API for real-time financial transaction fraud detection",
    version="1.0.0"
)

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

    encoder.fit([
        "CASH_IN",
        "CASH_OUT",
        "DEBIT",
        "PAYMENT",
        "TRANSFER"
    ])

    return encoder


# Load model and encoder when API starts

try:
    model = joblib.load(MODEL_PATH)
    label_encoder = load_label_encoder()

except Exception as e:
    model = None
    label_encoder = None
    print(f"Model loading error: {e}")


@app.get("/")
def home():
    return {
        "message": "Fraud Detection API is running",
        "status": "healthy",
        "version": "1.0.0"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "encoder_loaded": label_encoder is not None
    }


@app.post("/predict")
def predict(transaction: dict):

    if model is None:
        raise HTTPException(
            status_code=503,
            detail="Fraud detection model is not loaded"
        )

    try:
        data = pd.DataFrame([transaction]).copy()

        # Normalize transaction type

        if "type" in data.columns:

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

        prediction = int(
            model.predict(data[features])[0]
        )

        result = "Fraud" if prediction == 1 else "Normal"

        probability = None

        if hasattr(model, "predict_proba"):

            probabilities = model.predict_proba(
                data[features]
            )[0]

            probability = float(probabilities[1])

        if result == "Fraud":
            risk = "High"

        elif probability is not None and probability >= 0.30:
            risk = "Medium"

        else:
            risk = "Low"

        response = {
            "prediction": result,
            "risk": risk
        }

        if probability is not None:
            response["fraud_probability"] = round(
                probability,
                4
            )

        return response

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction error: {str(e)}"
        )