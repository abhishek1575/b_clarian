from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db, Address

address_bp = Blueprint('address', __name__)

# Add new address
@address_bp.route('/add_new_address', methods=['POST'])
@jwt_required()
def add_address():
    user_id = get_jwt_identity()
    data = request.get_json() or {}

    required_fields = ['street', 'city', 'state', 'zip_code', 'country']
    if not all(field in data and data[field].strip() for field in required_fields):
        return jsonify({"error": "All address fields are required"}), 400

    new_address = Address(
        user_id=user_id,
        street=data['street'].strip(),
        city=data['city'].strip(),
        state=data['state'].strip(),
        zip_code=data['zip_code'].strip(),
        country=data['country'].strip()
    )
    db.session.add(new_address)
    db.session.commit()

    return jsonify({"message": "Address added successfully", "address_id": new_address.id}), 201

# http://127.0.0.1:5000/add_new_address

# {
#   "street": "Near dmart, Ambegaon",
#   "city": "Pune",
#   "state": "Maharashtra",
#   "zip_code": "442200",
#   "country": "India"
# }



# Get all addresses of the logged-in user
@address_bp.route('/getall_addresses', methods=['GET'])
@jwt_required()
def get_user_addresses():
    user_id = get_jwt_identity()
    addresses = Address.query.filter_by(user_id=user_id).all()

    result = []
    for addr in addresses:
        result.append({
            "id": addr.id,
            "street": addr.street,
            "city": addr.city,
            "state": addr.state,
            "zip_code": addr.zip_code,
            "country": addr.country
        })

    return jsonify({"addresses": result}), 200

# http://127.0.0.1:5000/getall_addresses




# Update an address
@address_bp.route('/update_address/<int:address_id>', methods=['PUT'])
@jwt_required()
def update_address(address_id):
    user_id = get_jwt_identity()
    address = Address.query.filter_by(id=address_id, user_id=user_id).first()

    if not address:
        return jsonify({"error": "Address not found or unauthorized"}), 404

    data = request.get_json() or {}

    # Only update if a field is provided
    address.street = data.get('street', address.street)
    address.city = data.get('city', address.city)
    address.state = data.get('state', address.state)
    address.zip_code = data.get('zip_code', address.zip_code)
    address.country = data.get('country', address.country)

    db.session.commit()

    return jsonify({"message": "Address updated successfully"}), 200

# http://127.0.0.1:5000/update_address/1

# {
#     "city":"Navi Mumbai"
# }

# Delete an address
@address_bp.route('/delete_address/<int:address_id>', methods=['DELETE'])
@jwt_required()
def delete_address(address_id):
    user_id = get_jwt_identity()
    address = Address.query.filter_by(id=address_id, user_id=user_id).first()

    if not address:
        return jsonify({"error": "Address not found or unauthorized"}), 404

    db.session.delete(address)
    db.session.commit()
    return jsonify({"message": "Address deleted successfully"}), 200


# http://127.0.0.1:5000/delete_address/1
