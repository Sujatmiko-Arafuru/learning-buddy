# backend/utils/jwt_helper.py
import jwt
import datetime
import os
from functools import wraps
from flask import request, jsonify, current_app

SECRET_KEY = os.getenv("SECRET_KEY", current_app.config.get("SECRET_KEY") if current_app else os.getenv("SECRET_KEY", "dev-secret-key"))

def generate_token(user_id, expires_hours=24):
    payload = {
        "user_id": str(user_id),
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=expires_hours),
        "iat": datetime.datetime.utcnow()
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    # PyJWT >=2 returns str; if bytes, decode
    if isinstance(token, bytes):
        token = token.decode("utf-8")
    return token

def decode_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return {"error": "Token expired"}
    except jwt.InvalidTokenError:
        return {"error": "Invalid token"}

def token_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", None)
        if not auth_header:
            return jsonify({"success": False, "error": "Missing Authorization header"}), 401
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return jsonify({"success": False, "error": "Invalid Authorization header format (expected: Bearer <token>)"}), 401
        token = parts[1]
        decoded = decode_token(token)
        if isinstance(decoded, dict) and decoded.get("error"):
            return jsonify({"success": False, "error": decoded["error"]}), 401
        # pass user_id to route if needed
        request.user_id = decoded.get("user_id")
        return fn(*args, **kwargs)
    return wrapper

