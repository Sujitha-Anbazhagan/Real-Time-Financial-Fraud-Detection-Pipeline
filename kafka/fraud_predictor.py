import joblib
import pandas as pd
import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "fraud_detection_model.pkl"
)


ENCODER_PATH = os.path.join(
    BASE_DIR,
    "models",
    "label_encoder.pkl"
)


# Load model and encoder

model = joblib.load(MODEL_PATH)

label_encoder = joblib.load(ENCODER_PATH)



def predict_fraud(transaction):

    data = pd.DataFrame([transaction])


    # Convert type text into encoded number

    data["type"] = label_encoder.transform(
        data["type"]
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


    data = data[features]


    prediction = model.predict(data)[0]

    probability = None


    if prediction == 1:
        status = "FRAUD"
    else:
        status = "NORMAL"


    return {
    "prediction": int(prediction),
    "fraud_probability": probability,
    "status": "FRAUD" if prediction == 1 else "NORMAL"
}