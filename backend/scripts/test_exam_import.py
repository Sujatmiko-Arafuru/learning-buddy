"""Test if exam.py can be imported without errors"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("=" * 60)
print("TESTING EXAM.PY IMPORT")
print("=" * 60)

try:
    print("\n1. Importing exam blueprint...")
    from routes.exam import exam_bp
    print(f"   ✓ Import successful")
    print(f"   Blueprint name: {exam_bp.name}")
    print(f"   Blueprint import_name: {exam_bp.import_name}")
    
    print("\n2. Checking routes...")
    print(f"   Deferred functions: {len(exam_bp.deferred_functions)}")
    for func in exam_bp.deferred_functions:
        print(f"     - {func}")
    
    print("\n3. Testing route registration...")
    from flask import Flask
    test_app = Flask(__name__)
    test_app.register_blueprint(exam_bp, url_prefix='/api')
    
    routes = list(test_app.url_map.iter_rules())
    exam_routes = [str(r) for r in routes if 'exam' in str(r).lower()]
    print(f"   ✓ Registration successful")
    print(f"   Exam routes: {len(exam_routes)}")
    for route in exam_routes:
        print(f"     - {route}")
    
    print("\n✓ ALL TESTS PASSED - exam.py is OK!")
    
except Exception as e:
    print(f"\n✗ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)

