from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash

from app import db
from app.models import User

auth_api = Blueprint("auth_api", __name__, url_prefix="/api/auth")


def user_to_dict(user):
    return {
        "id": user.id,
        "username": user.username,
        "role": user.role,
        "telegram": user.telegram,
        "messenger": user.messenger,
        "viber": user.viber,
        "phone": user.phone,
        "profile_image": user.profile_image,
    }


# @auth_api.route("/register", methods=["POST"])
# def register():
#     data = request.get_json()

#     username = data.get("username")
#     password = data.get("password")

#     if not username or not password:
#         return jsonify({
#             "message": "Username and password are required"
#         }), 400

#     existing_user = User.query.filter_by(username=username).first()

#     if existing_user:
#         return jsonify({
#             "message": "Username already exists"
#         }), 409

#     hashed_password = generate_password_hash(password)

#     user = User(
#         username=username,
#         password=hashed_password
#     )

#     db.session.add(user)
#     db.session.commit()

#     return jsonify({
#         "message": "Register successful",
#         "user": user_to_dict(user)
#     }), 201


@auth_api.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({
            "message": "Username and password are required"
        }), 400

    user = User.query.filter_by(username=username).first()

    if not user or not check_password_hash(user.password, password):
        return jsonify({
            "message": "Invalid username or password"
        }), 401

    session["user_id"] = user.id
    session["username"] = user.username
    session["role"] = user.role

    return jsonify({
        "message": "Login successful",
        "user": user_to_dict(user)
    }), 200


@auth_api.route("/me", methods=["GET"])
def me():
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({
            "message": "Not authenticated",
            "user": None
        }), 401

    user = User.query.get(user_id)

    if not user:
        session.clear()

        return jsonify({
            "message": "User not found",
            "user": None
        }), 404

    return jsonify({
        "user": user_to_dict(user)
    }), 200


@auth_api.route("/logout", methods=["POST"])
def logout():
    session.clear()

    return jsonify({
        "message": "Logout successful"
    }), 200