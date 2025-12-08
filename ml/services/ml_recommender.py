"""
ML-based Recommender Service
Template untuk tim ML - implementasikan model recommendation di sini
"""
import os
import sys
import pickle
import numpy as np
import pandas as pd

# Add backend to path untuk akses database
sys.path.append(os.path.join(os.path.dirname(__file__), '../../backend'))
from db import collections

class MLRecommenderService:
    """
    ML-based recommendation service
    Tim ML dapat implementasikan model mereka di sini
    """
    
    def __init__(self, model_path=None):
        """
        Initialize ML recommender
        
        Args:
            model_path: Path ke trained model file (.pkl, .joblib, dll)
        """
        self.model = None
        self.model_path = model_path or os.path.join(
            os.path.dirname(__file__),
            '../models/recommender_model.pkl'
        )
        
        # Load model jika ada
        if os.path.exists(self.model_path):
            self.load_model()
    
    def load_model(self, model_path=None):
        """
        Load trained model dari file
        
        Args:
            model_path: Path ke model file (optional)
        """
        path = model_path or self.model_path
        
        try:
            with open(path, 'rb') as f:
                self.model = pickle.load(f)
            print(f"Model loaded from {path}")
        except Exception as e:
            print(f"Error loading model: {e}")
            self.model = None
    
    def save_model(self, model, model_path=None):
        """
        Save trained model ke file
        
        Args:
            model: Trained model object
            model_path: Path untuk save model (optional)
        """
        path = model_path or self.model_path
        
        # Create directory if not exists
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        with open(path, 'wb') as f:
            pickle.dump(model, f)
        print(f"Model saved to {path}")
    
    def prepare_features(self, user_email, user_progress, user_preferences):
        """
        Prepare features untuk model prediction
        Tim ML dapat customize method ini sesuai kebutuhan
        
        Args:
            user_email: User email
            user_progress: List of progress documents
            user_preferences: User preferences dict
        
        Returns:
            Feature vector untuk model
        """
        # TODO: Implement feature engineering
        # Contoh:
        # - Extract skills from progress
        # - Calculate completion rates
        # - Encode preferences
        # - Normalize features
        
        features = {
            'total_courses': len(user_progress),
            'completed_courses': sum(1 for p in user_progress if p.get('is_graduated', 0) == 1),
            'total_tutorials': sum(p.get('active_tutorials', 0) + p.get('completed_tutorials', 0) for p in user_progress),
            'completed_tutorials': sum(p.get('completed_tutorials', 0) for p in user_progress),
        }
        
        return features
    
    def get_recommendations(self, user_email, user_progress, user_preferences):
        """
        Get recommendations menggunakan ML model
        Method ini akan dipanggil dari backend/services/recommender.py
        
        Args:
            user_email: User email
            user_progress: List of progress documents
            user_preferences: User preferences dict
        
        Returns:
            dict dengan format yang sama seperti rule-based:
            {
                'recommended_courses': [...],
                'recommended_learning_paths': [...],
                'skill_analysis': {...}
            }
        """
        if self.model is None:
            raise ValueError("Model not loaded. Please train and save model first.")
        
        # Prepare features
        features = self.prepare_features(user_email, user_progress, user_preferences)
        
        # Get all courses
        all_courses = []
        if collections['courses']:
            all_courses = list(collections['courses'].find({}, {'_id': 0}))
        
        # TODO: Implement ML prediction
        # Contoh:
        # predictions = self.model.predict(features)
        # scores = self.model.predict_proba(features)
        
        # For now, return empty (tim ML akan implement)
        recommended_courses = []
        recommended_learning_paths = []
        
        # Format response sesuai dengan rule-based
        return {
            'recommended_courses': recommended_courses,
            'recommended_learning_paths': recommended_learning_paths,
            'skill_analysis': {
                'completed_skills': [],
                'weak_areas': []
            }
        }
    
    def train(self, training_data):
        """
        Train model menggunakan training data
        Tim ML dapat implementasikan training logic di sini
        
        Args:
            training_data: Training data (DataFrame atau dict)
        """
        # TODO: Implement model training
        # Contoh:
        # from sklearn.ensemble import RandomForestClassifier
        # self.model = RandomForestClassifier()
        # self.model.fit(X_train, y_train)
        
        print("Training model...")
        # Placeholder - tim ML akan implement
        pass
    
    def evaluate(self, test_data):
        """
        Evaluate model performance
        Tim ML dapat implementasikan evaluation logic di sini
        
        Args:
            test_data: Test data (DataFrame atau dict)
        
        Returns:
            Evaluation metrics (dict)
        """
        if self.model is None:
            raise ValueError("Model not loaded")
        
        # TODO: Implement evaluation
        # Contoh:
        # predictions = self.model.predict(X_test)
        # accuracy = accuracy_score(y_test, predictions)
        
        return {
            'accuracy': 0.0,
            'precision': 0.0,
            'recall': 0.0,
            'f1_score': 0.0
        }

