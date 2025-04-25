# newest code for order

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from app import db
from app.models import (
    User, Product, Cart, Order, OrderItems,
    Address, Inventory, OrderStatusHistory, Payments, RunnerAssignments
)

order_bp = Blueprint("order", __name__, url_prefix="/orders")

def _record_history(order, old_status, new_status):
    db.session.add(OrderStatusHistory(
        order_id=order.id,
        old_status=old_status,
        new_status=new_status,
        changed_at=datetime.utcnow()
    ))

# Place an order
@order_bp.route("/place", methods=["POST"])
@jwt_required()
def place_order():
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    if "address_id" not in data or "payment_mode" not in data:
        return jsonify({"error": "Missing address or payment mode"}), 400

    address = Address.query.filter_by(id=data["address_id"], user_id=user_id).first()
    if not address:
        return jsonify({"error": "Invalid or unauthorized address"}), 400

    cart_items = Cart.query.filter_by(user_id=user_id).all()
    if not cart_items:
        return jsonify({"error": "Cart is empty"}), 400

    total_price = 0
    for item in cart_items:
        prod = Product.query.get(item.product_id)
        if not prod or prod.stock < item.quantity:
            name = prod.name if prod else item.product_id
            return jsonify({"error": f"Insufficient stock for '{name}'"}), 400
        total_price += prod.price * item.quantity

    initial_status = "Pending" if data["payment_mode"].strip().lower() == "cod" else "Paid"
    order = Order(user_id=user_id, total_price=total_price, status=initial_status, created_at=datetime.utcnow())
    db.session.add(order)
    db.session.flush()

    _record_history(order, "Created", initial_status)

    for item in cart_items:
        db.session.add(OrderItems(
            order_id=order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price_at_order_time=Product.query.get(item.product_id).price
        ))
        p = Product.query.get(item.product_id)
        p.stock -= item.quantity
        inv = Inventory.query.filter_by(product_id=p.id).first()
        if inv:
            inv.stock -= item.quantity
            inv.updated_at = datetime.utcnow()

    Cart.query.filter_by(user_id=user_id).delete()
    db.session.commit()

    return jsonify({
        "message": "Order placed successfully",
        "order_id": order.id,
        "status": order.status,
        "total_price": total_price
    }), 201

# List current user's orders
@order_bp.route("/userorder", methods=["GET"])
@jwt_required()
def get_user_orders():
    user_id = get_jwt_identity()
    orders = (Order.query
        .filter_by(user_id=user_id)
        .order_by(Order.created_at.desc())
        .all()
    )
    return jsonify([{
        "order_id": o.id,
        "total_price": o.total_price,
        "status": o.status,
        "created_at": o.created_at.isoformat()
    } for o in orders]), 200

# Admin: list all orders
@order_bp.route("/get_all_orders", methods=["GET"])
@jwt_required()
def get_all_orders():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or user.role != "admin":
        return jsonify({"error": "Unauthorized"}), 403

    orders = Order.query.order_by(Order.created_at.desc()).all()
    return jsonify([{
        "order_id": o.id,
        "user_id": o.user_id,
        "user": o.user.name,
        "total_price": o.total_price,
        "status": o.status,
        "created_at": o.created_at.isoformat()
    } for o in orders]), 200

# Get order details (user or admin), include address for admin
@order_bp.route("/<int:order_id>", methods=["GET"])
@jwt_required()
def get_order(order_id):
    me = get_jwt_identity()
    user = User.query.get(me)
    order = Order.query.get(order_id)
    if not order or (order.user_id != me and user.role != "admin"):
        return jsonify({"error": "Unauthorized"}), 403

    data = {
        "order_id": order.id,
        "user_id": order.user_id,
        "total_price": order.total_price,
        "status": order.status,
        "created_at": order.created_at.isoformat(),
        "items": [
            {
                "product_id": i.product_id,
                "product_name": i.product.name,
                "quantity": i.quantity,
                "unit_price": i.price_at_order_time
            } for i in order.order_items
        ]
    }

    if user.role == "admin":
        addr = Address.query.filter_by(id=order.user.addresses[0].id).first()
        data["shipping_address"] = {
            "street": addr.street,
            "city": addr.city,
            "state": addr.state,
            "zip_code": addr.zip_code,
            "country": addr.country
        }

    return jsonify(data), 200

# Change order status (admin or user for specific transitions)
@order_bp.route("/<int:order_id>/status", methods=["PUT"])
@jwt_required()
def change_status(order_id):
    me = get_jwt_identity()
    user = User.query.get(me)
    order = Order.query.get(order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404

    new = (request.get_json() or {}).get("status")
    valid = ["Pending","Processing","Out_for_delivery","Delivered",
             "Cancelled","Returned","Defective","Return_Processed"]
    if new not in valid:
        return jsonify({"error": "Invalid status"}), 400

    if user.role != "admin" and new not in ["Cancelled","Defective","Returned"]:
        return jsonify({"error": "Unauthorized"}), 403

    old = order.status
    order.status = new
    _record_history(order, old, new)

    if new == "Return_Processed":
        for it in order.order_items:
            p = Product.query.get(it.product_id)
            p.stock += it.quantity
            inv = Inventory.query.filter_by(product_id=p.id).first()
            if inv:
                inv.stock += it.quantity
                inv.updated_at = datetime.utcnow()

    db.session.commit()
    return jsonify({"message": f"Order status updated to '{new}'"}), 200

# Get order history (status, optional payments/delivery)
@order_bp.route("/<int:order_id>/history", methods=["GET"])
@jwt_required()
def history(order_id):
    me = get_jwt_identity()
    user = User.query.get(me)
    order = Order.query.get(order_id)
    if not order or (order.user_id != me and user.role != "admin"):
        return jsonify({"error": "Unauthorized"}), 403

    include = (request.args.get("include") or "").split(",")
    out = {}

    hist = OrderStatusHistory.query.filter_by(order_id=order_id).order_by(OrderStatusHistory.changed_at).all()
    out["status_history"] = [
        {"old": h.old_status, "new": h.new_status, "at": h.changed_at.isoformat()}
        for h in hist
    ]
    if "payments" in include:
        out["payment_history"] = [
            {"id": p.id, "method": p.payment_method, "tx": p.transaction_id,
             "status": p.status, "paid_at": p.paid_at.isoformat() if p.paid_at else None}
            for p in Payments.query.filter_by(order_id=order_id)
        ]
    if "delivery" in include:
        assigns = RunnerAssignments.query.filter_by(order_id=order_id).all()
        out["delivery_history"] = [
            {"assign_id": a.id, "runner_id": a.runner_id, "status": a.status,
             "assigned_at": a.assigned_at.isoformat(),
             "picked_up_at": a.picked_up_at and a.picked_up_at.isoformat(),
             "delivered_at": a.delivered_at and a.delivered_at.isoformat()}
            for a in assigns
        ]
    return jsonify(out), 200