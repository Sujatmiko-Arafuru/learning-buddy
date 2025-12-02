"""Quick script to check if backend is running"""
import requests
import sys

try:
    response = requests.get('http://localhost:5000/api/health', timeout=5)
    if response.status_code == 200:
        print("✓ Backend is running!")
        print(f"  Response: {response.json()}")
        sys.exit(0)
    else:
        print(f"✗ Backend returned status code: {response.status_code}")
        sys.exit(1)
except requests.exceptions.ConnectionError:
    print("✗ Backend is NOT running!")
    print("  Please start the backend with: python app.py")
    sys.exit(1)
except requests.exceptions.Timeout:
    print("✗ Backend request timed out!")
    sys.exit(1)
except Exception as e:
    print(f"✗ Error checking backend: {e}")
    sys.exit(1)

