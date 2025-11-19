"""
Flask application entry point for Learning Buddy API
"""
from flask import Flask
from flask_cors import CORS
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['JSON_SORT_KEYS'] = False

# Import routes
from routes.learning_path import learning_path_bp
from routes.users import users_bp
from routes.progress import progress_bp
from routes.recommendation import recommendation_bp
from routes.questions import questions_bp
from routes.chat import chat_bp

# Register blueprints
app.register_blueprint(learning_path_bp, url_prefix='/api')
app.register_blueprint(users_bp, url_prefix='/api')
app.register_blueprint(progress_bp, url_prefix='/api')
app.register_blueprint(recommendation_bp, url_prefix='/api')
app.register_blueprint(questions_bp, url_prefix='/api')
app.register_blueprint(chat_bp, url_prefix='/api')

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return {'status': 'ok', 'message': 'Learning Buddy API is running'}, 200

@app.route('/')
def index():
    """Root endpoint"""
    return {'message': 'Learning Buddy API', 'version': '1.0.0'}, 200

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

