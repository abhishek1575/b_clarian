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
    user_list = []
    for user in users:
        user_data = {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
        }
        user_list.append(user_data)
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

    user_data = {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
    }
    return jsonify({"user": user_data}), 200
# http://127.0.0.1:5000/admin/users/5


# update user role
@admin_bp.route('/users/<int:user_id>/promote', methods=['PUT'])
@jwt_required()
def promote_user(user_id):
    current_user_id = get_jwt_identity()

    # Ensure only an admin can promote another user
    if not is_admin(current_user_id):
        return jsonify({"error": "Unauthorized"}), 403

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Promote the user to admin
    user.role = "admin"

    db.session.commit()
    return jsonify({"message": f"User {user_id} has been promoted to admin."}), 200
# http://127.0.0.1:5000/admin/users/8/promote



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

  
# Product Management:



# Add Products
def add_product():
    current_user_id = get_jwt_identity()
    if not is_admin(current_user_id):
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json() or {}
    name = data.get('name', "").strip()
    description = data.get('description', "").strip()
    price = data.get('price')
    stock = data.get('stock', 0)
    category = data.get('category', "").strip()
    image_url = data.get('image_url', "").strip()

    # Basic validation: required fields
    if not name or price is None or not category:
        return jsonify({"error": "Missing required product details"}), 400

    new_product = Product(
        name=name,
        description=description,
        price=price,
        stock=stock,
        category=category,
        image_url=image_url
    )
    db.session.add(new_product)
    db.session.commit()

    return jsonify({"message": "Product added successfully", "product_id": new_product.id}), 201





# List Products

@admin_bp.route('/products', methods=['GET'])
@jwt_required()
def list_products():
    current_user_id = get_jwt_identity()
    if not is_admin(current_user_id):
        return jsonify({"error": "Unauthorized"}), 403

    products = Product.query.all()
    product_list = []
    for product in products:
        product_list.append({
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "price": product.price,
            "stock": product.stock,
            "category": product.category,
            "image_url": product.image_url
        })
    return jsonify({"products": product_list}), 200
# http://127.0.0.1:5000/admin/products


# Get product details
@admin_bp.route('/products/<int:product_id>', methods=['GET'])
@jwt_required()
def product_details(product_id):
    current_user_id = get_jwt_identity()
    if not is_admin(current_user_id):
        return jsonify({"error": "Unauthorized"}), 403

    product = Product.query.get(product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404

    product_data = {
        "id": product.id,
        "name": product.name,
        "description": product.description,
        "price": product.price,
        "stock": product.stock,
        "category": product.category,
        "image_url": product.image_url
    }
    return jsonify({"product": product_data}), 200
# http://127.0.0.1:5000/admin/products/3

# Update Product details

@admin_bp.route('/products/<int:product_id>', methods=['PUT'])
@jwt_required()
def update_product(product_id):
    current_user_id = get_jwt_identity()
    if not is_admin(current_user_id):
        return jsonify({"error": "Unauthorized"}), 403

    product = Product.query.get(product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404

    data = request.get_json() or {}
    # Update fields if present in the request
    if 'name' in data:
        product.name = data.get('name').strip()
    if 'description' in data:
        product.description = data.get('description').strip()
    if 'price' in data:
        product.price = data.get('price')
    if 'stock' in data:
        product.stock = data.get('stock')
    if 'category' in data:
        product.category = data.get('category').strip()
    if 'image_url' in data:
        product.image_url = data.get('image_url').strip()

    db.session.commit()
    return jsonify({"message": "Product updated successfully"}), 200


# Delete Product

@admin_bp.route('/products/<int:product_id>', methods=['DELETE'])
@jwt_required()
def delete_product(product_id):
    current_user_id = get_jwt_identity()
    if not is_admin(current_user_id):
        return jsonify({"error": "Unauthorized"}), 403

    product = Product.query.get(product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404

    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": "Product deleted successfully"}), 200

# 