from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Cart, Product

cart_bp = Blueprint('cart', __name__)



@cart_bp.route('/cart/add', methods=['POST'])
@jwt_required()
def add_to_cart():
    data = request.get_json()
    print("Received data:", data)
    if not data:
        return jsonify({'message': 'Invalid JSON payload'}), 422

    # Get the user_id from the JWT token
    user_id = get_jwt_identity()

    try:
        product_id = int(data.get('product_id'))
    except (TypeError, ValueError):
        return jsonify({'message': 'Product ID must be a valid integer'}), 422

    try:
        quantity = int(data.get('quantity', 1))
    except (TypeError, ValueError):
        return jsonify({'message': 'Quantity must be a valid integer'}), 422

    if not product_id:
        return jsonify({'message': 'Product ID is required'}), 400

    product = Product.query.get(product_id)
    if not product:
        return jsonify({'message': 'Product not found'}), 404

    if product.stock < quantity:
        return jsonify({'message': 'Insufficient stock available'}), 400

    # Check if the product already exists in the user's cart.
    cart_item = Cart.query.filter_by(user_id=user_id, product_id=product_id).first()
    if cart_item:
        cart_item.quantity += quantity
    else:
        new_cart_item = Cart(user_id=user_id, product_id=product_id, quantity=quantity)
        db.session.add(new_cart_item)

    db.session.commit()
    return jsonify({'message': 'Item added to cart'}), 201



@cart_bp.route('/update_cart_quantity', methods=['POST'])
@jwt_required()
def update_cart_quantity():
    user_id = get_jwt_identity()
    data = request.get_json()

    product_id = data.get('product_id')
    quantity = data.get('quantity')

    if not product_id or quantity is None:
        return jsonify({'message': 'Product ID and quantity are required'}), 400

    try:
        product_id = int(product_id)
        quantity = int(quantity)
    except ValueError:
        return jsonify({'message': 'Invalid product ID or quantity'}), 400

    cart_item = Cart.query.filter_by(user_id=user_id, product_id=product_id).first()
    if not cart_item:
        return jsonify({'message': 'Item not found in cart'}), 404

    if quantity < 1:
        db.session.delete(cart_item)
    else:
        cart_item.quantity = quantity

    db.session.commit()
    return jsonify({'message': 'Cart updated successfully'}), 200




@cart_bp.route('/cart/remove/<int:cart_id>', methods=['DELETE'])
@jwt_required()
def remove_from_cart(cart_id):
    user_id = get_jwt_identity()
    cart_item = Cart.query.filter_by(id=cart_id, user_id=user_id).first()

    if not cart_item:
        return jsonify({'message': 'Cart item not found'}), 404

    db.session.delete(cart_item)
    db.session.commit()
    return jsonify({'message': 'Item removed from cart'}), 200

@cart_bp.route('/cart/update', methods=['PUT'])
@jwt_required()
def update_cart():
    data = request.get_json()
    user_id = get_jwt_identity()
    cart_id = data.get('cart_id')
    quantity = data.get('quantity')

    if cart_id is None or quantity is None:
        return jsonify({'message': 'cart_id and quantity are required'}), 400

    cart_item = Cart.query.filter_by(id=cart_id, user_id=user_id).first()
    if not cart_item:
        return jsonify({'message': 'Cart item not found'}), 404

    if quantity <= 0:
        db.session.delete(cart_item)
        message = 'Item removed from cart'
    else:
        if cart_item.product.stock < quantity:
            return jsonify({'message': 'Insufficient stock for the desired quantity'}), 400
        cart_item.quantity = quantity
        message = 'Cart updated successfully'

    db.session.commit()
    return jsonify({'message': message}), 200




@cart_bp.route('/cart/view', methods=['GET', 'OPTIONS'])
def view_cart():
    if request.method == 'OPTIONS':
        return jsonify({'message': 'CORS preflight'}), 200 


    from flask_jwt_extended import jwt_required, get_jwt_identity

    @jwt_required()
    def get_cart():
        user_id = get_jwt_identity()
        cart_items = Cart.query.filter_by(user_id=user_id).all()

        cart_data = []
        for item in cart_items:
            cart_data.append({
                'cart_id': item.id,
                'product_id': item.product_id,
                'product_name': item.product.name,
                'quantity': item.quantity,
                'price': item.product.price,
                'total_price': item.quantity * item.product.price,
                'added_at': item.created_at.isoformat(),
                'image_url': item.product.image_url or ""

            })

        return jsonify(cart_data), 200

    return get_cart()




