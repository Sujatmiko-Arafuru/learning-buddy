"""
Test exam API endpoint directly
"""
import requests
import urllib.parse
import json

# Test endpoint
BASE_URL = "http://localhost:5000/api"

# Test dengan course name yang ada di database
test_course = "Belajar Fundamental Deep Learning"

print("=" * 60)
print("TESTING EXAM API ENDPOINT")
print("=" * 60)

print(f"\n1. Testing GET /exam/questions?course_name={test_course}")
url = f"{BASE_URL}/exam/questions"
params = {"course_name": test_course}
print(f"   URL: {url}")
print(f"   Params: {params}")

try:
    response = requests.get(url, params=params, timeout=10)
    
    print(f"\n   Status Code: {response.status_code}")
    print(f"   Headers: {dict(response.headers)}")
    
    try:
        response_data = response.json()
        print(f"   Response JSON: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200:
            if response_data.get('success'):
                questions = response_data.get('data', {}).get('questions', [])
                print(f"\n   ✓ SUCCESS: Found {len(questions)} questions")
            else:
                print(f"\n   ✗ FAILED: {response_data.get('error')}")
        else:
            print(f"\n   ✗ FAILED: Status {response.status_code}")
    except json.JSONDecodeError:
        print(f"   Response Text: {response.text[:500]}")
        
except requests.exceptions.ConnectionError:
    print("\n   ✗ ERROR: Cannot connect to backend server")
    print("   Make sure backend is running on http://localhost:5000")
except Exception as e:
    print(f"\n   ✗ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
