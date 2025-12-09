"""Check if exam routes are registered"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("=" * 60)
print("CHECKING EXAM BLUEPRINT REGISTRATION")
print("=" * 60)

# Test import
try:
    from routes.exam import exam_bp
    print(f"\n✓ Blueprint imported: {exam_bp.name}")
    print(f"  Routes in blueprint: {len(exam_bp.deferred_functions)}")
except Exception as e:
    print(f"\n✗ Import error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test registration
try:
    from flask import Flask
    test_app = Flask(__name__)
    test_app.register_blueprint(exam_bp, url_prefix='/api')
    print(f"\n✓ Blueprint registered successfully")
    
    # Check routes
    routes = list(test_app.url_map.iter_rules())
    exam_routes = [str(rule) for rule in routes if 'exam' in str(rule).lower()]
    print(f"  Exam routes after registration: {len(exam_routes)}")
    if exam_routes:
        for route in exam_routes:
            print(f"    - {route}")
except Exception as e:
    print(f"\n✗ Registration error: {e}")
    import traceback
    traceback.print_exc()

# Check actual app
print("\n" + "=" * 60)
print("CHECKING ACTUAL APP")
print("=" * 60)

try:
    from app import app
    all_routes = list(app.url_map.iter_rules())
    exam_routes = [str(rule) for rule in all_routes if 'exam' in str(rule).lower()]
    
    print(f"\nTotal routes in app: {len(all_routes)}")
    print(f"Exam routes in app: {len(exam_routes)}")
    
    if exam_routes:
        print("\n✓ Exam routes found:")
        for route in exam_routes:
            print(f"  - {route}")
    else:
        print("\n✗ NO EXAM ROUTES in app!")
        print("\nChecking if exam_bp is in app.blueprints...")
        print(f"  Blueprints: {list(app.blueprints.keys())}")
        if 'exam' in app.blueprints:
            print("  ✓ exam blueprint is registered")
        else:
            print("  ✗ exam blueprint NOT registered")
except Exception as e:
    print(f"\n✗ Error checking app: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
