"""Check learning_path_answers data"""
import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db import db, collections

load_dotenv()

if db is None:
    print("[ERROR] MongoDB connection failed")
    sys.exit(1)

print("=" * 60)
print("Checking learning_path_answers collection")
print("=" * 60)

# Check different possible collection names
collection_names = ['learning_path_answers', 'Learning_Path_Answer', 'learning_path_answer']
found_collection = None

for coll_name in collection_names:
    if coll_name in db.list_collection_names():
        found_collection = coll_name
        print(f"\n✓ Found collection: {coll_name}")
        break

if not found_collection:
    print("\n✗ Collection not found. Available collections:")
    for name in db.list_collection_names():
        print(f"  - {name}")
    sys.exit(1)

coll = db[found_collection]
docs = list(coll.find({}, {'_id': 0}).limit(20))
print(f"\nTotal documents found: {len(docs)}\n")

if len(docs) > 0:
    print("Sample documents:")
    for i, doc in enumerate(docs[:5], 1):
        print(f"\n{i}. ID: {doc.get('id')} (type: {type(doc.get('id')).__name__})")
        print(f"   Name: {doc.get('name')}")
        print(f"   All keys: {list(doc.keys())}")
else:
    print("Collection is empty!")

print("\n" + "=" * 60)
print("Expected IDs for categories:")
print("Mobile Development: [2, 12, 10]")
print("Artificial Intelligence: [1, 8, 11]")
print("Cloud Computing: [6, 9]")
print("Web Development: [3, 4, 7, 13]")
print("=" * 60)
