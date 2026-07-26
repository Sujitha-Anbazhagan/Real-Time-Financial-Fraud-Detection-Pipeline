"""Data preprocessing utilities for fraud detection pipeline"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
import logging

logger = logging.getLogger(__name__)


class DataPreprocessor:
    """Handle data cleaning and feature engineering"""

    def __init__(self):
        self.label_encoders = {}
        self.scaler = None

    def load_data(self, filepath: str) -> pd.DataFrame:
        """Load transaction data from CSV"""
        try:
            df = pd.read_csv(filepath)
            logger.info(f"Loaded data with shape {df.shape}")
            return df
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            raise

    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean data by removing duplicates and handling missing values"""
        df = df.drop_duplicates()
        df = df.dropna(subset=['isFraud'])
        logger.info(f"Data cleaned. Shape: {df.shape}")
        return df

    def encode_categorical(self, df: pd.DataFrame, categorical_cols: list, fit: bool = True) -> pd.DataFrame:
        """Encode categorical variables"""
        df_encoded = df.copy()
        
        for col in categorical_cols:
            if col in df.columns:
                if fit:
                    self.label_encoders[col] = LabelEncoder()
                    df_encoded[col] = self.label_encoders[col].fit_transform(df[col].astype(str))
                else:
                    if col in self.label_encoders:
                        df_encoded[col] = self.label_encoders[col].transform(df[col].astype(str))
        
        logger.info(f"Encoded {len(categorical_cols)} categorical columns")
        return df_encoded

    def remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove duplicate transactions"""
        initial_size = len(df)
        df = df.drop_duplicates(subset=['step', 'type', 'amount', 'nameOrig', 'nameDest'])
        removed = initial_size - len(df)
        logger.info(f"Removed {removed} duplicate transactions")
        return df

    def handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handle missing values in the dataset"""
        missing_cols = df.columns[df.isnull().any()]
        
        for col in missing_cols:
            if df[col].dtype in ['float64', 'int64']:
                df[col] = df[col].fillna(df[col].median())
            else:
                df[col] = df[col].fillna(df[col].mode()[0])
        
        logger.info(f"Handled missing values in {len(missing_cols)} columns")
        return df

    def select_features(self, df: pd.DataFrame, feature_cols: list) -> pd.DataFrame:
        """Select relevant features for modeling"""
        available_cols = [col for col in feature_cols if col in df.columns]
        logger.info(f"Selected {len(available_cols)} features for modeling")
        return df[available_cols]

    def prepare_data(self, df: pd.DataFrame, categorical_cols: list = None, fit: bool = True) -> pd.DataFrame:
        """Complete preprocessing pipeline"""
        df = self.clean_data(df)
        df = self.handle_missing_values(df)
        df = self.remove_duplicates(df)
        
        if categorical_cols:
            df = self.encode_categorical(df, categorical_cols, fit=fit)
        
        logger.info("Data preparation complete")
        return df


def balance_dataset(X: pd.DataFrame, y: pd.Series, strategy: str = 'oversample'):
    """Balance imbalanced dataset"""
    from collections import Counter
    
    initial_dist = Counter(y)
    logger.info(f"Initial class distribution: {initial_dist}")
    
    if strategy == 'oversample':
        fraud_idx = y[y == 1].index
        normal_idx = y[y == 0].index
        
        oversample_idx = np.random.choice(fraud_idx, size=len(normal_idx), replace=True)
        balanced_idx = list(normal_idx) + list(oversample_idx)
        
        X_balanced = X.loc[balanced_idx].reset_index(drop=True)
        y_balanced = y.loc[balanced_idx].reset_index(drop=True)
    
    final_dist = Counter(y_balanced)
    logger.info(f"Final class distribution: {final_dist}")
    
    return X_balanced, y_balanced


def get_feature_importance(model, feature_names: list) -> pd.DataFrame:
    """Extract feature importance from trained model"""
    if hasattr(model, 'feature_importances_'):
        importance = model.feature_importances_
    elif hasattr(model, 'coef_'):
        importance = np.abs(model.coef_[0])
    else:
        return pd.DataFrame()
    
    importance_df = pd.DataFrame({
        'feature': feature_names,
        'importance': importance
    }).sort_values('importance', ascending=False)
    
    return importance_df
