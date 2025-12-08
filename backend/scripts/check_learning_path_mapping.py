"""Check learning path mapping"""
import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db import db

load_dotenv()

if db is None:
    print("[ERROR] MongoDB connection failed")
    sys.exit(1)

print("=" * 60)
print("Checking Learning Path Mapping")
print("=" * 60)

# Check Learning_Path collection
lp_coll = db['Learning_Path']
lp_docs = list(lp_coll.find({}, {'_id': 0, 'learning_path_id': 1, 'learning_path_name': 1}).limit(20))

print(f"\nLearning_Path collection ({len(lp_docs)} documents):")
for doc in lp_docs:
    print(f"  ID: {doc.get('learning_path_id')}, Name: {doc.get('learning_path_name')}")

# Check Learning_Path_Answer collection
lpa_coll = db['Learning_Path_Answer']
lpa_docs = list(lpa_coll.find({}, {'_id': 0, 'id': 1, 'name': 1}).limit(20))

print(f"\nLearning_Path_Answer collection ({len(lpa_docs)} documents):")
for doc in lpa_docs[:10]:
    print(f"  ID: {doc.get('id')}, Name: {doc.get('name')}")

print("\n" + "=" * 60)
print("Expected mapping:")
print("Mobile Development → Learning Path IDs: [2, 12, 10]")
print("Artificial Intelligence → Learning Path IDs: [1, 8, 11]")
print("Cloud Computing → Learning Path IDs: [6, 9]")
print("Web Development → Learning Path IDs: [3, 4, 7, 13]")
print("=" * 60)

# Check if IDs match
expected_ids = [1, 2, 3, 4, 6, 7, 8, 9, 10, 11, 12, 13]
lp_ids = [doc.get('learning_path_id') for doc in lp_docs if doc.get('learning_path_id')]
lpa_ids = [doc.get('id') for doc in lpa_docs if doc.get('id')]

print(f"\nLearning_Path IDs found: {sorted(set(lp_ids))}")
print(f"Learning_Path_Answer IDs found: {sorted(set(lpa_ids))[:20]}...")

# Check if expected IDs exist in Learning_Path_Answer
print("\nChecking if expected IDs exist in Learning_Path_Answer:")
for exp_id in expected_ids:
    found = any(doc.get('id') == exp_id for doc in lpa_docs)
    status = "✓" if found else "✗"
    print(f"  {status} ID {exp_id}")

