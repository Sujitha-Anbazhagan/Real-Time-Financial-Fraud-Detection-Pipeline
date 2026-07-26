"""Model training script for fraud detection"""

import logging
import joblib
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (
    classification_report, confusion_matrix, roc_auc_score, 
    roc_curve, precision_recall_curve, f1_score, accuracy_score
)
import matplotlib.pyplot as plt
import seaborn as sns

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FraudDetectionModel:
    """Train and evaluate fraud detection model"""
    
    def __init__(self, model_params: dict = None):
        self.model_params = model_params or {
            'n_estimators': 100,
            'max_depth': 10,
            'min_samples_split': 5,
            'min_samples_leaf': 2,
            'random_state': 42,
            'n_jobs': -1,
            'class_weight': 'balanced'
        }
        self.model = RandomForestClassifier(**self.model_params)
        self.label_encoders = {}
        
    def load_data(self, filepath: str) -> pd.DataFrame:
        """Load transaction data"""
        logger.info(f"Loading data from {filepath}")
        df = pd.read_csv(filepath)
        logger.info(f"Data shape: {df.shape}")
        return df
    
    def preprocess_data(self, df: pd.DataFrame) -> tuple:
        """Preprocess data for training"""
        logger.info("Starting data preprocessing")
        
        df = df.drop_duplicates()
        df = df.dropna(subset=['isFraud'])
        
        categorical_cols = ['type']
        for col in categorical_cols:
            if col in df.columns:
                le = LabelEncoder()
                df[col] = le.fit_transform(df[col].astype(str))
                self.label_encoders[col] = le
        
        numeric_cols = [col for col in df.columns if col != 'isFraud' and col != 'isFlaggedFraud']
        feature_cols = [col for col in numeric_cols if col in df.columns]
        
        X = df[feature_cols].fillna(df[feature_cols].median())
        y = df['isFraud']
        
        logger.info(f"Features: {feature_cols}")
        logger.info(f"Target distribution: {y.value_counts().to_dict()}")
        
        return X, y, feature_cols
    
    def train(self, X: pd.DataFrame, y: pd.Series, test_size: float = 0.2):
        """Train the model"""
        logger.info("Splitting data for training")
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )
        
        logger.info(f"Training set size: {X_train.shape}")
        logger.info(f"Test set size: {X_test.shape}")
        
        logger.info("Training Random Forest model")
        self.model.fit(X_train, y_train)
        
        return X_train, X_test, y_train, y_test
    
    def evaluate(self, X_test: pd.DataFrame, y_test: pd.Series) -> dict:
        """Evaluate model performance"""
        logger.info("Evaluating model")
        
        y_pred = self.model.predict(X_test)
        y_pred_proba = self.model.predict_proba(X_test)[:, 1]
        
        results = {
            'accuracy': accuracy_score(y_test, y_pred),
            'f1_score': f1_score(y_test, y_pred),
            'roc_auc': roc_auc_score(y_test, y_pred_proba),
            'classification_report': classification_report(y_test, y_pred),
            'confusion_matrix': confusion_matrix(y_test, y_pred)
        }
        
        logger.info(f"Accuracy: {results['accuracy']:.4f}")
        logger.info(f"F1 Score: {results['f1_score']:.4f}")
        logger.info(f"ROC AUC: {results['roc_auc']:.4f}")
        logger.info(f"Classification Report:\n{results['classification_report']}")
        
        return results
    
    def save_model(self, model_path: str):
        """Save trained model"""
        Path(model_path).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.model, model_path)
        logger.info(f"Model saved to {model_path}")
    
    def save_label_encoders(self, encoders_path: str):
        """Save label encoders"""
        Path(encoders_path).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.label_encoders, encoders_path)
        logger.info(f"Label encoders saved to {encoders_path}")


def main():
    """Main training pipeline"""
    # Configuration
    data_path = Path(__file__).parent / "data" / "PS_20174392719_1491204439457_log.csv"
    model_path = Path(__file__).parent / "models" / "fraud_detection_model.pkl"
    encoders_path = Path(__file__).parent / "models" / "label_encoders.pkl"
    
    try:
        # Initialize model
        fraud_model = FraudDetectionModel()
        
        # Load and preprocess data
        df = fraud_model.load_data(str(data_path))
        X, y, feature_cols = fraud_model.preprocess_data(df)
        
        # Train model
        X_train, X_test, y_train, y_test = fraud_model.train(X, y)
        
        # Evaluate
        results = fraud_model.evaluate(X_test, y_test)
        
        # Save model
        fraud_model.save_model(str(model_path))
        fraud_model.save_label_encoders(str(encoders_path))
        
        logger.info("Model training completed successfully!")
        
    except Exception as e:
        logger.error(f"Error during training: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
