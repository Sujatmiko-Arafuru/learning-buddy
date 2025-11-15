"""
Template script untuk training model machine learning
Tim ML dapat menggunakan script ini sebagai starting point untuk training model recommendation
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import pickle
import os
import sys

# Add parent directory to path untuk import dari backend
sys.path.append(os.path.join(os.path.dirname(__file__), '../../learning-buddy/backend'))

from db import collections

class ModelTrainer:
    """
    Base class untuk training model recommendation
    Tim ML dapat extend class ini untuk implementasi model mereka
    """
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.model_path = os.path.join(os.path.dirname(__file__), '../models')
        
    def load_data(self):
        """
        Load data dari MongoDB atau file CSV/Excel
        Tim ML dapat customize method ini sesuai kebutuhan
        """
        print("Loading data...")
        
        # Option 1: Load dari MongoDB
        data = []
        if collections.get('student_progress'):
            progress_data = list(collections['student_progress'].find({}))
            data = pd.DataFrame(progress_data)
        
        # Option 2: Load dari file CSV/Excel
        # data_path = os.path.join(os.path.dirname(__file__), '../data/raw/dataset.csv')
        # if os.path.exists(data_path):
        #     data = pd.read_csv(data_path)
        
        print(f"Loaded {len(data)} records")
        return data
    
    def preprocess_data(self, data):
        """
        Preprocess data untuk training
        Tim ML dapat customize preprocessing sesuai kebutuhan
        """
        print("Preprocessing data...")
        
        # Contoh preprocessing
        # - Handle missing values
        # - Feature engineering
        # - Encoding categorical variables
        # - Normalization/scaling
        
        processed_data = data.copy()
        
        # TODO: Implement preprocessing sesuai kebutuhan
        # processed_data = processed_data.dropna()
        # processed_data = pd.get_dummies(processed_data, columns=['category'])
        
        return processed_data
    
    def prepare_features(self, data):
        """
        Prepare features (X) dan target (y) untuk training
        """
        print("Preparing features...")
        
        # TODO: Define features dan target
        # X = data[['feature1', 'feature2', ...]]
        # y = data['target']
        
        # Placeholder
        X = data
        y = None
        
        return X, y
    
    def train(self, X_train, y_train):
        """
        Train model
        Tim ML dapat implement model mereka di sini
        """
        print("Training model...")
        
        # TODO: Implement model training
        # Contoh:
        # from sklearn.ensemble import RandomForestClassifier
        # self.model = RandomForestClassifier()
        # self.model.fit(X_train, y_train)
        
        print("Model training completed!")
        return self.model
    
    def evaluate(self, X_test, y_test):
        """
        Evaluate model performance
        """
        print("Evaluating model...")
        
        if self.model is None:
            print("Model not trained yet!")
            return None
        
        # TODO: Implement evaluation metrics
        # from sklearn.metrics import accuracy_score, precision_score, recall_score
        # predictions = self.model.predict(X_test)
        # accuracy = accuracy_score(y_test, predictions)
        # print(f"Accuracy: {accuracy}")
        
        return None
    
    def save_model(self, filename='recommender_model.pkl'):
        """
        Save trained model ke file
        """
        if self.model is None:
            print("No model to save!")
            return
        
        os.makedirs(self.model_path, exist_ok=True)
        model_file = os.path.join(self.model_path, filename)
        
        with open(model_file, 'wb') as f:
            pickle.dump(self.model, f)
        
        print(f"Model saved to {model_file}")
    
    def load_model(self, filename='recommender_model.pkl'):
        """
        Load trained model dari file
        """
        model_file = os.path.join(self.model_path, filename)
        
        if not os.path.exists(model_file):
            print(f"Model file not found: {model_file}")
            return None
        
        with open(model_file, 'rb') as f:
            self.model = pickle.load(f)
        
        print(f"Model loaded from {model_file}")
        return self.model
    
    def run_training_pipeline(self):
        """
        Run complete training pipeline
        """
        print("=" * 50)
        print("Starting Training Pipeline")
        print("=" * 50)
        
        # 1. Load data
        data = self.load_data()
        
        if data is None or len(data) == 0:
            print("No data available for training!")
            return
        
        # 2. Preprocess
        processed_data = self.preprocess_data(data)
        
        # 3. Prepare features
        X, y = self.prepare_features(processed_data)
        
        if y is None:
            print("Target variable not defined!")
            return
        
        # 4. Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # 5. Train
        self.train(X_train, y_train)
        
        # 6. Evaluate
        self.evaluate(X_test, y_test)
        
        # 7. Save model
        self.save_model()
        
        print("=" * 50)
        print("Training Pipeline Completed!")
        print("=" * 50)


if __name__ == '__main__':
    trainer = ModelTrainer()
    trainer.run_training_pipeline()

