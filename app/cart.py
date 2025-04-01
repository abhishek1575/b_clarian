from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Cart, Product

cart_bp = Blueprint('cart', __name__)

@cart_bp.route('/cart/add', methods=['POST'])
@jwt_required()
def add_to_cart():
    data = request.get_json()
    user_id = get_jwt_identity()
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)

    product = Product.query.get(product_id)
    if not product:
        return jsonify({'message': 'Product not found'}), 404

    cart_item = Cart.query.filter_by(user_id=user_id, product_id=product_id).first()
    if cart_item:
        cart_item.quantity += quantity
    else:
        new_cart_item = Cart(user_id=user_id, product_id=product_id, quantity=quantity)
        db.session.add(new_cart_item)

    db.session.commit()
    return jsonify({'message': 'Item added to cart'}), 201

@cart_bp.route('/cart/remove/<int:cart_id>', methods=['DELETE'])
@jwt_required()
def remove_from_cart(cart_id):
    user_id = get_jwt_identity()
    cart_item = Cart.query.filter_by(id=cart_id, user_id=user_id).first()

    if not cart_item:
        return jsonify({'message': 'Item not found in cart'}), 404

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

    cart_item = Cart.query.filter_by(id=cart_id, user_id=user_id).first()
    if not cart_item:
        return jsonify({'message': 'Item not found in cart'}), 404

    if quantity <= 0:
        db.session.delete(cart_item)
    else:
        cart_item.quantity = quantity

    db.session.commit()
    return jsonify({'message': 'Cart updated successfully'}), 200

@cart_bp.route('/cart/view', methods=['GET'])
@jwt_required()
def view_cart():
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
            'total_price': item.quantity * item.product.price
        })

    return jsonify(cart_data), 200
