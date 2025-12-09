"""
Test script untuk debugging exam endpoint
"""
import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db import db

load_dotenv()

if db is None:
    print("[ERROR] Database not connected")
    sys.exit(1)

print("=" * 60)
print("TESTING EXAM ENDPOINT")
print("=" * 60)

# Get Soal_Ujian collection
exam_coll = db['Soal_Ujian']

# Get all unique course names
print("\n1. Getting all unique course names from Soal_Ujian...")
all_docs = list(exam_coll.find({}, {'course_name': 1}))
unique_courses = sorted(set(doc.get('course_name', '') for doc in all_docs if doc.get('course_name')))

print(f"\nFound {len(unique_courses)} unique courses:")
for i, course in enumerate(unique_courses, 1):
    count = sum(1 for doc in all_docs if doc.get('course_name') == course)
    print(f"  {i}. {course} ({count} questions)")

# Test query for a specific course
if unique_courses:
    test_course = unique_courses[0]
    print(f"\n2. Testing query for course: '{test_course}'")
    test_query = {'course_name': test_course}
    results = list(exam_coll.find(test_query))
    print(f"   Found {len(results)} questions")
    
    if results:
        print(f"\n3. Sample question structure:")
        sample = results[0]
        print(f"   Keys: {list(sample.keys())}")
        print(f"   course_name: {sample.get('course_name')}")
        print(f"   question_text: {sample.get('question_text', '')[:50]}...")
        print(f"   correct_answer: {sample.get('correct_answer')}")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)

