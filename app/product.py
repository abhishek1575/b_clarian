from flask import Blueprint, request, jsonify,send_from_directory
from app.models import db, Product
import os
from werkzeug.utils import secure_filename
from app import app, db
from flask_jwt_extended import jwt_required


product_bp = Blueprint('product', __name__,url_prefix='/api')


UPLOAD_FOLDER = os.path.abspath(os.path.join(app.root_path,'img'))
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



# Get all products
@product_bp.route('/get_all_products', methods=['GET'])
def get_products():
    products = Product.query.all()
    return jsonify([product.to_dict() for product in products]), 200

# Get a single product by ID
@product_bp.route('/get_product/<int:id>', methods=['GET'])
def get_product(id):
    product = Product.query.get(id)
    if not product:
        return jsonify({"error": "Product not found"}), 404
    return jsonify(product.to_dict()), 200

# Get products based on category
@product_bp.route('/category/filter', methods=['GET'])
def filter_products_by_category():
    category = request.args.get('category')
    if not category:
        return jsonify({"message": "Please provide a category to filter"}), 400
    products = Product.query.filter_by(category=category).all()
    return jsonify([product.to_dict() for product in products]), 200

FIXED_CATEGORIES = ["Fruits", "Vegetables", "Dairy"]


#Add a product (Admin Only)
@product_bp.route('/add_product', methods=['POST'])
@jwt_required()
def add_product():
    # Multipart form-data support
    name = request.form.get('name')
    description = request.form.get('description', "")
    price = request.form.get('price')
    unit = request.form.get('unit')
    stock = request.form.get('stock')
    category = request.form.get('category')
    image_file = request.files.get('image')

    if not all([name, price, unit, stock, category]):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        price = float(price)
        stock = int(stock)
    except ValueError:
        return jsonify({"error": "Invalid price or stock"}), 400

    # Save image
    image_url = ""
    if image_file:
        filename = secure_filename(image_file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image_file.save(filepath)
        image_url = f"/api/img/{filename}"  # Save as API route path

    # Save to DB
    new_product = Product(
        name=name,
        description=description,
        price=price,
        unit=unit,
        stock=stock,
        category=category,
        image_url=image_url
    )

    db.session.add(new_product)
    db.session.commit()

    return jsonify({
        "message": "Product added successfully",
        "product": new_product.to_dict()
    }), 201

from flask import send_file, current_app

@product_bp.route('/img/<filename>', methods=['GET'])
def serve_image(filename):
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404
    return send_file(file_path, mimetype='image/png')

# @product_bp.route('/img/<filename>', methods=['GET'])
# def serve_image(filename):
#     return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)


# Update a product (Admin Only)
@product_bp.route('/update_product/<int:id>', methods=['PUT'])
@jwt_required()
def update_product(id):
    product = Product.query.get(id)
    if not product:
        return jsonify({"error": "Product not found"}), 404

    # Parse form data (multipart/form-data)
    name = request.form.get('name', product.name)
    description = request.form.get('description', product.description)
    price = request.form.get('price', product.price)
    unit = request.form.get('unit', product.unit)
    stock = request.form.get('stock', product.stock)
    category = request.form.get('category', product.category)
    image_file = request.files.get('image')

    try:
        price = float(price)
        stock = int(stock)
    except ValueError:
        return jsonify({"error": "Invalid price or stock"}), 400

    # Update product fields
    product.name = name
    product.description = description
    product.price = price
    product.unit = unit
    product.stock = stock
    product.category = category

    # Handle image upload (if any)
    if image_file:
        filename = secure_filename(image_file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image_file.save(filepath)
        product.image_url = f"/api/img/{filename}"  # Update image URL path

    db.session.commit()
    return jsonify({
        "message": "Product updated successfully",
        "product": product.to_dict()
    }), 200


# Delete a product (Admin Only)
@product_bp.route('/delete_product/<int:id>', methods=['DELETE'])
@jwt_required()     
def delete_product(id):
    product = Product.query.get(id)
    if not product:
        return jsonify({"error": "Product not found"}), 404

    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": "Product deleted successfully"}), 200

