from flask import Blueprint, request, jsonify
from app.models import db, Product
from flask_jwt_extended import jwt_required,get_jwt_identity

product_bp = Blueprint('product', __name__)

# Get all products
@product_bp.route('/products', methods=['GET'])
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
@product_bp.route('/products', methods=['POST'])
@jwt_required()
def add_product():
    print(f"Received Token: {get_jwt_identity()}")  # Debugging line
    data = request.get_json()
    name = data.get('name')
    description = data.get('description')
    price = data.get('price')
    unit = data.get('unit')
    stock = data.get('stock')
    category = data.get('category')
    image_url = data.get('image_url')

    if not all([name, price, unit, stock, category]):
        return jsonify({"error": "Missing required fields"}), 400

    new_product = Product(
        name=name, description=description, price=price, 
        unit=unit, stock=stock, category=category, image_url=image_url
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



import os
from werkzeug.utils import secure_filename
from flask import current_app

UPLOAD_FOLDER = 'static/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@product_bp.route('/product/upload_image/<int:product_id>', methods=['POST'])
def upload_image(product_id):
    if 'image' not in request.files:
        return jsonify({'message': 'No file part'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)

        # Save the image path in the database
        product = Product.query.get(product_id)
        if not product:
            return jsonify({'message': 'Product not found'}), 404

        product.image_url = file_path
        db.session.commit()

        return jsonify({'message': 'Image uploaded successfully', 'image_url': file_path}), 200

    return jsonify({'message': 'Invalid file type'}), 400



























# to add an item 
# start 'flask shell'


from app import db
from app.models import Product

# product1 = Product(name="Apple", description="Fresh red apples", price=3.99, unit="1 kg", stock=100, category="Fruits", image_url="apple.jpg")
# product2 = Product(name="Banana", description="Organic bananas", price=1.99, unit="1 dozen", stock=50, category="Fruits", image_url="banana.jpg")
# product3 = Product(name="Carrot", description="Crunchy carrots", price=2.49, unit="500g", stock=75, category="Vegetables", image_url="carrot.jpg")

# db.session.add_all([product1, product2, product3])
# db.session.commit()
# print("Sample products added successfully!")


# exit()




# to add image 
# flask shell
# from app import db
# from app.models import Product
# product = Product.query.get(1)  # Change 1 to your product ID
# product.image_url = "static/images/example.jpg"  # Change to your actual image file
# db.session.commit()
# print(product.image_url)
