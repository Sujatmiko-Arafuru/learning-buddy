# backend/routes/auth.py
from flask import Blueprint, request, jsonify, current_app
from db import collections
from datetime import datetime
import bcrypt
from bson import ObjectId
from utils.jwt_helper import generate_token

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/auth/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if not name or not email or not password:
        return jsonify({"success": False, "error": "Field name, email, dan password wajib diisi"}), 400

    if collections['users'] is None:
        return jsonify({"success": False, "error": "Database not connected"}), 500

    # cek duplikat
    existing = collections['users'].find_one({"email": email})
    if existing:
        return jsonify({"success": False, "error": "Email sudah terdaftar"}), 400

    # hash password
    salt = bcrypt.gensalt()
    hashed_pw = bcrypt.hashpw(password.encode("utf-8"), salt)

    user_doc = {
        "name": name,
        "email": email,
        "password": hashed_pw.decode("utf-8"),  # simpan string
        "created_at": datetime.utcnow().isoformat(),
        "onboarding_completed": False,
        "preferences": data.get("preferences", {}),
        "current_learning_path": None,
        "skill_assessment": {}
    }

    res = collections['users'].insert_one(user_doc)
    user_doc["_id"] = str(res.inserted_id)
    # jangan kembalikan password
    user_doc.pop("password", None)

    return jsonify({"success": True, "data": user_doc}), 201


@auth_bp.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"success": False, "error": "Email dan password wajib diisi"}), 400

    if collections['users'] is None:
        return jsonify({"success": False, "error": "Database not connected"}), 500

    user = collections['users'].find_one({"email": email})
    if not user:
        return jsonify({"success": False, "error": "Email tidak ditemukan"}), 404

    stored_pw = user.get("password", "")
    # verify
    try:
        ok = bcrypt.checkpw(password.encode("utf-8"), stored_pw.encode("utf-8"))
    except Exception:
        ok = False

    if not ok:
        return jsonify({"success": False, "error": "Password salah"}), 400

    token = generate_token(user_id=str(user["_id"]))

    # response user info tanpa password
    user_info = {
        "id": str(user["_id"]),
        "name": user.get("name"),
        "email": user.get("email")
    }

    return jsonify({"success": True, "token": token, "user": user_info}), 200
