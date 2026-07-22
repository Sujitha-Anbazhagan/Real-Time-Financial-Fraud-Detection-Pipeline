from fastapi import FastAPI
import joblib
import pandas as pd


app = FastAPI(
    title="Real-Time Fraud Detection API",
    version="1.0"
)


# Load trained model
import os

MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    "../models/fraud_detection_model.pkl"
)

model = joblib.load(MODEL_PATH)

@app.get("/")
def home():
    return {
        "message": "Fraud Detection API is running"
    }


@app.post("/predict")
def predict(transaction: dict):

    data = pd.DataFrame([transaction])

    prediction = model.predict(data)[0]

    if prediction == 1:
        result = "Fraud"
    else:
        result = "Normal"

    return {
        "prediction": result
    }