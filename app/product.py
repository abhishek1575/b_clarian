
from flask import Blueprint, request, jsonify
from app.models import db, Product
from flask_jwt_extended import jwt_required,get_jwt_identity
from werkzeug.utils import secure_filename
from flask import current_app
import os
import uuid
from flask import Flask
from flask_cors import CORS
from config import Config

app = Flask(__name__, static_url_path='/static', static_folder='static')
app.config.from_object(Config)
CORS(app)


product_bp = Blueprint('product', __name__,url_prefix='/api')

# Get all products
@product_bp.route('/get_all_products', methods=['GET'])
def get_products():
    products = Product.query.all()
    return jsonify([product.to_dict() for product in products]), 200

# Get a single product by ID
@product_bp.route('/products/<int:id>', methods=['GET'])
def get_product(id):
    product = Product.query.get(id)
    if not product:
        return jsonify({"error": "Product not found"}), 404
    return jsonify(product.to_dict()), 200

# Add a new product (Admin Only)

@product_bp.route('/add_products', methods=['POST'])
@jwt_required()
def add_product():
    name = request.form.get('name')
    description = request.form.get('description')
    price = request.form.get('price')
    unit = request.form.get('unit')
    stock = request.form.get('stock')
    category = request.form.get('category')
    image_file = request.files.get('image')

    image_url = None
    if image_file:
        filename = f"{uuid.uuid4().hex}_{secure_filename(image_file.filename)}"
        upload_folder = current_app.config['UPLOAD_FOLDER']
        save_path = os.path.join(upload_folder, filename)
        image_file.save(save_path)
        image_url = f"/static/uploads/{filename}"

    if not all([name, price, unit, stock, category]):
        return jsonify({"error": "Missing required fields"}), 400

    new_product = Product(
        name=name,
        description=description,
        price=float(price),
        unit=unit,
        stock=int(stock),
        category=category,
        image_url=image_url
    )

    db.session.add(new_product)
    db.session.commit()

    return jsonify({"message": "Product added successfully"}), 201


# Update a product (Admin Only)
@product_bp.route('/products/<int:id>', methods=['PUT'])
@jwt_required()
def update_product(id):
    product = Product.query.get(id)
    if not product:
        return jsonify({"error": "Product not found"}), 404

    data = request.get_json()
    product.name = data.get('name', product.name)
    product.description = data.get('description', product.description)
    product.price = data.get('price', product.price)
    product.unit = data.get('unit', product.unit)
    product.stock = data.get('stock', product.stock)
    product.category = data.get('category', product.category)
    product.image_url = data.get('image_url', product.image_url)

    db.session.commit()
    return jsonify({"message": "Product updated successfully"}), 200

# Delete a product (Admin Only)
@product_bp.route('/products/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_product(id):
    product = Product.query.get(id)
    if not product:
        return jsonify({"error": "Product not found"}), 404

    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": "Product deleted successfully"}), 200


@product_bp.route('/product/card/<int:product_id>', methods=['GET'])
def get_product_card(product_id):
    product = Product.query.get(product_id)
    
    if not product:
        return jsonify({'message': 'Product not found'}), 404
    
    product_card = {
        'product_id': product.id,
        'name': product.name,
        'image_url': product.image_url,
        'price': product.price,
        'unit': product.unit,
        'discount': product.discount  # ✅ Added Discount
    }
    
    return jsonify(product_card), 200



# import os
# from werkzeug.utils import secure_filename
# from flask import current_app

# UPLOAD_FOLDER = 'static/images'
# ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# # Ensure the upload folder exists
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS




# import base64

# @product_bp.route('/product/upload_image/<int:product_id>', methods=['POST'])
# def upload_image(product_id):
#     if 'image' not in request.files:
#         return jsonify({'message': 'No file part'}), 400

#     file = request.files['image']
#     if file.filename == '':
#         return jsonify({'message': 'No selected file'}), 400

#     product = Product.query.get(product_id)
#     if not product:
#         return jsonify({'message': 'Product not found'}), 404

#     image_data = file.read()  
#     product.image = image_data  
#     db.session.commit()

#     return jsonify({'message': 'Image uploaded successfully'}), 200




# @product_bp.route('/product/image/<int:product_id>', methods=['GET'])
# def get_product_image(product_id):
#     product = Product.query.get(product_id)
#     if not product or not product.image:
#         return jsonify({'message': 'Image not found'}), 404

#     # Convert BLOB to Base64
#     image_base64 = base64.b64encode(product.image).decode('utf-8')

#     return jsonify({'image': image_base64}), 200