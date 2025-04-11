from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db, User,Product,Order
from app import app  
# User Management:

admin_bp = Blueprint('admin', __name__)

def is_admin(user_id):
    user = User.query.get(user_id)
    return user and user.role == "admin"

# (register admin) is in auth.py


# Get all users
@admin_bp.route('/users', methods=['GET'])
@jwt_required()
def get_all_users():
    current_user_id = get_jwt_identity()
    if not is_admin(current_user_id):
        return jsonify({"error": "Unauthorized"}), 403

    users = User.query.all()
    user_list = [user.to_dict() for user in users]
    return jsonify({"users": user_list}), 200

# http://127.0.0.1:5000/admin/users



# display user details
@admin_bp.route('/users/<int:user_id>', methods=['GET'])
@jwt_required()
def user_details(user_id):
    current_user_id = get_jwt_identity()
    if not is_admin(current_user_id):
        return jsonify({"error": "Unauthorized"}), 403

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({"user": user.to_dict()}), 200

# http://127.0.0.1:5000/admin/users/5


# delete a user
@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    current_user_id = get_jwt_identity()
    if not is_admin(current_user_id):
        return jsonify({"error": "Unauthorized"}), 403

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted successfully"}), 200
# http://127.0.0.1:5000/admin/users/8


# Change user status (active/inactive)
# This endpoint allows an admin to change the status of a user (active/inactive).
@admin_bp.route('/users/<int:user_id>/status', methods=['PUT'])
@jwt_required()
def update_user_status(user_id):
    current_user_id = get_jwt_identity()
    if not is_admin(current_user_id):
        return jsonify({"error": "Unauthorized"}), 403

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json()
    is_active = data.get("isActive")

    if is_active is None or not isinstance(is_active, bool):
        return jsonify({"error": "Invalid 'isActive' value. It must be true or false."}), 400

    user.isActive = is_active
    db.session.commit()

    return jsonify({"message": f"User status updated to {'Active' if is_active else 'Inactive'}."}), 200

  
