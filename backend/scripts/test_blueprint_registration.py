"""Test blueprint registration step by step"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask

print("=" * 60)
print("TESTING BLUEPRINT REGISTRATION STEP BY STEP")
print("=" * 60)

app = Flask(__name__)

blueprints_to_test = [
    ('dashboard', 'routes.dashboard'),
    ('learning_path', 'routes.learning_path'),
    ('users', 'routes.users'),
    ('progress', 'routes.progress'),
    ('recommendation', 'routes.recommendation'),
    ('questions', 'routes.questions'),
    ('chat', 'routes.chat'),
    ('personalization', 'routes.personalization'),
    ('assessment', 'routes.assessment'),
    ('progress_update', 'routes.progress_update'),
    ('exam', 'routes.exam'),
]

for bp_name, module_path in blueprints_to_test:
    try:
        module = __import__(module_path, fromlist=[f'{bp_name}_bp'])
        bp = getattr(module, f'{bp_name}_bp')
        app.register_blueprint(bp, url_prefix='/api')
        print(f"✓ {bp_name:20s} - registered")
    except Exception as e:
        print(f"✗ {bp_name:20s} - ERROR: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "=" * 60)
print("FINAL BLUEPRINT STATUS")
print("=" * 60)
print(f"Blueprints registered: {list(app.blueprints.keys())}")
print(f"Total routes: {len(list(app.url_map.iter_rules()))}")

exam_routes = [str(rule) for rule in app.url_map.iter_rules() if 'exam' in str(rule).lower()]
print(f"Exam routes: {len(exam_routes)}")
if exam_routes:
    for route in exam_routes:
        print(f"  - {route}")

