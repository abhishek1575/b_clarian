from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db, User, Product, Inventory
from datetime import datetime

inventory_bp = Blueprint("inventory", __name__, url_prefix="/inventory")

# Helper to validate admin
def is_admin(user_id):
    user = User.query.get(user_id)
    return user and user.role == "admin"

# Reset stock for all products (default: 100)
@inventory_bp.route("/reset_all", methods=["PUT"])
@jwt_required()
def reset_all_inventory():
    user_id = get_jwt_identity()
    if not is_admin(user_id):
        return jsonify({"error": "Unauthorized"}), 403

    default_stock = 100

    # Reset in Inventory
    all_inventory = Inventory.query.all()
    for inv in all_inventory:
        inv.stock = default_stock
        inv.updated_at = datetime.utcnow()

        # Sync with Product
        product = Product.query.get(inv.product_id)
        if product:
            product.stock = default_stock

    db.session.commit()
    return jsonify({"message": f"All inventory reset to {default_stock} successfully."}), 200


# Reset stock for a specific product_id
@inventory_bp.route("/reset/<int:product_id>", methods=["PUT"])
@jwt_required()
def reset_single_inventory(product_id):
    user_id = get_jwt_identity()
    if not is_admin(user_id):
        return jsonify({"error": "Unauthorized"}), 403

    default_stock = 100

    inv = Inventory.query.filter_by(product_id=product_id).first()
    if not inv:
        return jsonify({"error": "Inventory record not found"}), 404

    inv.stock = default_stock
    inv.updated_at = datetime.utcnow()

    product = Product.query.get(product_id)
    if product:
        product.stock = default_stock

    db.session.commit()
    return jsonify({"message": f"Inventory for product_id {product_id} reset to {default_stock}."}), 200
