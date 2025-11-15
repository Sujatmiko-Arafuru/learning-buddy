"""
Database connection module for MongoDB Atlas
"""
import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

# MongoDB connection
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
DB_NAME = os.getenv('DB_NAME', 'learning_buddy_db')

try:
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    # Test connection
    client.admin.command('ping')
    print(f"[OK] Connected to MongoDB: {DB_NAME}")
except Exception as e:
    print(f"[ERROR] MongoDB connection error: {e}")
    db = None

# Collection references
collections = {
    'learning_paths': db.learning_paths if db is not None else None,
    'courses': db.courses if db is not None else None,
    'tutorials': db.tutorials if db is not None else None,
    'course_levels': db.course_levels if db is not None else None,
    'learning_path_answers': db.learning_path_answers if db is not None else None,
    'current_interest_questions': db.current_interest_questions if db is not None else None,
    'current_tech_questions': db.current_tech_questions if db is not None else None,
    'skill_keywords': db.skill_keywords if db is not None else None,
    'student_progress': db.student_progress if db is not None else None,
    'users': db.users if db is not None else None,
}

