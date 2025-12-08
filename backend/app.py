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
from routes.personalization import personalization_bp
from routes.assessment import assessment_bp
from routes.exam import exam_bp

# Register blueprints
app.register_blueprint(learning_path_bp, url_prefix='/api')
app.register_blueprint(users_bp, url_prefix='/api')
app.register_blueprint(progress_bp, url_prefix='/api')
app.register_blueprint(recommendation_bp, url_prefix='/api')
app.register_blueprint(questions_bp, url_prefix='/api')
app.register_blueprint(chat_bp, url_prefix='/api')
app.register_blueprint(personalization_bp, url_prefix='/api')
app.register_blueprint(assessment_bp, url_prefix='/api')
app.register_blueprint(exam_bp, url_prefix='/api')

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
    print("=" * 60)
    print("Learning Buddy Backend Server")
    print("=" * 60)
    print(f"Server running on: http://0.0.0.0:{port}")
    print(f"API endpoint: http://localhost:{port}/api")
    print(f"Health check: http://localhost:{port}/api/health")
    print("=" * 60)
    print("Press Ctrl+C to stop the server")
    print("=" * 60)
    print()
    try:
        app.run(host='0.0.0.0', port=port, debug=True)
    except OSError as e:
        if "Address already in use" in str(e) or "address is already in use" in str(e).lower():
            print(f"\n[ERROR] Port {port} is already in use!")
            print(f"Please either:")
            print(f"  1. Stop the application using port {port}")
            print(f"  2. Change PORT in .env file to a different port")
            print(f"\nTo find what's using port {port}:")
            print(f"  Windows: netstat -ano | findstr :{port}")
            print(f"  Linux/Mac: lsof -i :{port}")
        else:
            print(f"\n[ERROR] Failed to start server: {e}")
        raise

