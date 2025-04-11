
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from app.models import db, Order, User

order_bp = Blueprint('order', __name__)



# Get Order Status

@order_bp.route('/order/status/<int:order_id>', methods=['GET'])
@jwt_required()
def get_order_status(order_id):
    user_id = get_jwt_identity()
    order = Order.query.filter_by(id=order_id, user_id=user_id).first()
    if not order:
        return jsonify({"error": "Order not found"}), 404

    # If updated_at is not available, remove this field from response
    last_updated = order.updated_at.strftime("%Y-%m-%d %H:%M:%S") if hasattr(order, 'updated_at') and order.updated_at else "N/A"
    
    return jsonify({
        "order_id": order.id,
        "status": order.status,
        "last_updated": last_updated
    }), 200


@order_bp.route('/order/status/update', methods=['POST'])
@jwt_required()
def update_order_status():
    data = request.get_json()
    order_id = data.get("order_id")
    new_status = data.get("status")

    if not order_id or not new_status:
        return jsonify({"error": "Order ID and new status are required"}), 400

    # Restrict to admin users only
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or user.role != "admin":
        return jsonify({"error": "Unauthorized"}), 403

    order = Order.query.filter_by(id=order_id).first()
    if not order:
        return jsonify({"error": "Order not found"}), 404

    order.status = new_status
    if hasattr(order, 'updated_at'):
        order.updated_at = datetime.utcnow()
    db.session.commit()

    return jsonify({"message": f"Order {order_id} status updated to {new_status}"}), 200



@order_bp.route('/order/webhook/payment', methods=['POST'])
def payment_webhook():
    data = request.get_json()
    order_id = data.get("order_id")
    payment_status = data.get("payment_status")

    if not order_id or not payment_status:
        return jsonify({"error": "Order ID and payment status are required"}), 400

    order = Order.query.filter_by(id=order_id).first()
    if not order:
        return jsonify({"error": "Order not found"}), 404

    if payment_status.lower() == "success":
        order.status = "Paid"
    else:
        order.status = "Payment Failed"

    if hasattr(order, 'updated_at'):
        order.updated_at = datetime.utcnow()
    db.session.commit()

    return jsonify({"message": f"Order {order_id} updated based on payment status: {payment_status}"}), 200
