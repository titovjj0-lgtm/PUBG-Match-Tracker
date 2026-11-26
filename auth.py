import sqlite3
from contextlib import closing
from flask import Blueprint, request, jsonify, session, abort
from werkzeug.security import generate_password_hash, check_password_hash
import storage

auth = Blueprint("auth", __name__)


@auth.post("/register")
def register():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Expected JSON"}), 400

    login = data.get("login", "")
    password = data.get("password", "")

    if not isinstance(login, str) or not isinstance(password, str):
        return jsonify({"error": "Invalid credentials"}), 400

    login = login.strip()

    if not 3 <= len(login) <= 64 or not 8 <= len(password) <= 128:
        return jsonify({"error": "Invalid login or password length"}), 400

    try:
        with closing(storage.connect()) as conn, conn:
            cursor = conn.execute("""
                INSERT INTO users (login, password_hash)
                VALUES (?, ?)
            """, (login, generate_password_hash(password)))

            user_id = cursor.lastrowid

    except sqlite3.IntegrityError:
        return jsonify({"error": "Login already exists"}), 409

    session.clear()
    session["user_id"] = user_id
    return jsonify({"id": user_id}), 201


@auth.post("/login")
def login():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Expected JSON"}), 400

    login = data.get("login", "")
    password = data.get("password", "")

    if not isinstance(login, str) or not isinstance(password, str):
        return jsonify({"error": "Invalid credentials"}), 400

    with closing(storage.connect()) as conn:
        user = conn.execute(
            "SELECT * FROM users WHERE login = ?",
            (login.strip(),)
        ).fetchone()

    if user is None or not check_password_hash(
        user["password_hash"], password
    ):
        return jsonify({"error": "Invalid login or password"}), 401

    session.clear()
    session["user_id"] = user["id"]

    return jsonify({"id": user["id"]})


@auth.post("/logout")
def logout():
    session.clear()
    return jsonify({"ok": True})


def current_user():
    user_id = session.get("user_id")

    if user_id is None:
        abort(401)

    with closing(storage.connect()) as conn:
        user = conn.execute(
            "SELECT * FROM users WHERE id = ?",
            (user_id,)
        ).fetchone()

    if user is None:
        session.clear()
        abort(401)

    return user


def require_admin():
    if "CF-Connecting-IP" in request.headers:
        abort(404)

    user = current_user()

    if not user["is_admin"]:
        abort(403)

    return user


@auth.get("/me")
def me():
    user = current_user()
    return jsonify({
        "id": user["id"],
        "login": user["login"],
        "is_admin": bool(user["is_admin"])
    })
