from app import app
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity,create_refresh_token
from datetime import timedelta
from app.models import db, User
import jwt
# from config import Config


auth_bp = Blueprint('auth', __name__)

#register
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}

    name = data.get('name', "").strip()
    email = data.get('email', "").strip().lower()
    phone = data.get('phone', "").strip()
    password = data.get('password', "").strip()
    role = data.get("role", "user")

    if not name or not email or not password or not phone:
        return jsonify({"error": "All fields are required"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 409
    if User.query.filter_by(phone=phone).first():
        return jsonify({"error": "Phone number already exists"}), 400

    hashed_password = generate_password_hash(password)
    new_user = User(name=name, email=email, phone=phone, password=hashed_password, role=role)
    
    db.session.add(new_user)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print("Error committing to the database:", e)
        return jsonify({"error": "Database error"}), 500

    return jsonify({"message": "User registered successfully"}), 201

# if we want to implement flsk for specific routes

# from flask import Flask, request, jsonify
# from flask_cors import cross_origin

# app = Flask(__name__)

# @app.route('/auth/register', methods=['POST'])
# @cross_origin(origin='http://localhost:5173')  # Allow requests from React frontend
# def register():
#     data = request.json
#     return jsonify({"message": "User registered successfully"}), 200




# Register admin

@auth_bp.route('/register-admin', methods=['POST'])
def register_admin():
    data = request.get_json() or {}

    name = data.get('name', "").strip()
    email = data.get('email', "").strip().lower()
    phone = data.get('phone', "").strip()
    password = data.get('password', "").strip()

    if not name or not email or not password or not phone:
        return jsonify({"error": "All fields are required"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 409
    if User.query.filter_by(phone=phone).first():
        return jsonify({"error": "Phone number already exists"}), 400

    hashed_password = generate_password_hash(password)
    new_admin = User(name=name, email=email, phone=phone, password=hashed_password, role="admin")

    db.session.add(new_admin)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print("Error committing to the database:", e)
        return jsonify({"error": "Database error"}), 500

    return jsonify({"message": "Admin registered successfully"}), 201


#generated token
def generate_token(user):
    payload = {
        "id": user.id,
        "email": user.email,
        "role": user.role,  
        # "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }
    secret_key = app.config.get("SECRET_KEY", "your_default_secret")
    return jwt.encode(payload, secret_key, algorithm="HS256")



#Login
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}

    email = data.get('email', "").strip().lower()
    password = data.get('password', "").strip()

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password, password):
        return jsonify({"error": "Invalid credentials"}), 401

    access_token = create_access_token(identity=str(user.id), expires_delta=timedelta(days=1))
    refresh_token = create_refresh_token(identity=str(user.id))

    return jsonify({
        "message": "Login successful",
        "access_token": access_token,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role
        }
    }), 200



# password change
@auth_bp.route('/change-password', methods=['PUT'])
@jwt_required()
def change_password():
    data = request.get_json() or {}
    current_password = data.get('current_password', "").strip()
    new_password = data.get('new_password', "").strip()

    if not current_password or not new_password:
        return jsonify({"error": "Both current and new passwords are required"}), 400

    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user or not check_password_hash(user.password, current_password):
        return jsonify({"error": "Current password is incorrect"}), 401

    if len(new_password) < 8:
        return jsonify({"error": "New password must be at least 8 characters long"}), 400

    user.password = generate_password_hash(new_password)
    db.session.commit()

    return jsonify({"message": "Password changed successfully"}), 200



#Logout
@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    return jsonify({"message": "Logout successful."}), 200

















































