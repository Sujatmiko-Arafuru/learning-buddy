"""Test importing app.py to see if there are any errors"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("=" * 60)
print("TESTING APP.PY IMPORT")
print("=" * 60)

try:
    print("\n1. Testing db import...")
    from db import collections, db
    print("   ✓ db imported successfully")
    
    print("\n2. Testing exam blueprint import...")
    from routes.exam import exam_bp
    print(f"   ✓ exam_bp imported: {exam_bp.name}")
    
    print("\n3. Testing app import...")
    from app import app
    print("   ✓ app imported successfully")
    
    print("\n4. Checking blueprints...")
    print(f"   Blueprints registered: {list(app.blueprints.keys())}")
    
    print("\n5. Checking routes...")
    all_routes = list(app.url_map.iter_rules())
    exam_routes = [str(rule) for rule in all_routes if 'exam' in str(rule).lower()]
    print(f"   Total routes: {len(all_routes)}")
    print(f"   Exam routes: {len(exam_routes)}")
    if exam_routes:
        for route in exam_routes:
            print(f"     - {route}")
    
except Exception as e:
    print(f"\n✗ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)

