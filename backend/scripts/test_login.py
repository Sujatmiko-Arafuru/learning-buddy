"""Test login functionality"""
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
print("Testing Login Functionality")
print("=" * 60)

# Test credentials from screenshot
test_email = "ofurosasuke@gmail.com"
test_password = "Angelio123"

print(f"\nTesting with:")
print(f"  Email: {test_email}")
print(f"  Password: {test_password}")

# Find user
user = collections['users'].find_one({'email': test_email.lower().strip()})

if not user:
    print(f"\n✗ User not found with email: {test_email.lower().strip()}")
    print("\nAvailable users:")
    all_users = list(collections['users'].find({}, {'_id': 0, 'email': 1, 'name': 1}))
    for u in all_users:
        print(f"  - {u.get('email')} ({u.get('name')})")
    sys.exit(1)

print(f"\n✓ User found: {user.get('name')}")
print(f"  Stored email: '{user.get('email')}'")
print(f"  Stored password: '{user.get('password')}'")
print(f"  Password length: {len(str(user.get('password', '')))}")

# Test password comparison
stored_password = str(user.get('password', '')).strip()
input_password = test_password.strip()

print(f"\nPassword comparison:")
print(f"  Stored (stripped): '{stored_password}' (length: {len(stored_password)})")
print(f"  Input (stripped): '{input_password}' (length: {len(input_password)})")
print(f"  Match: {stored_password == input_password}")

if stored_password == input_password:
    print("\n✓ Password matches! Login should work.")
else:
    print("\n✗ Password does NOT match!")
    print("\nDebugging:")
    print(f"  Stored bytes: {stored_password.encode('utf-8')}")
    print(f"  Input bytes: {input_password.encode('utf-8')}")
    print(f"  Are they equal?: {stored_password == input_password}")
    print(f"  repr(stored): {repr(stored_password)}")
    print(f"  repr(input): {repr(input_password)}")

