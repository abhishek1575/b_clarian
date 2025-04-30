# runner.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db, User, Order, RunnerAssignments
from datetime import datetime

runner_bp = Blueprint('runner', __name__,)

def is_admin(user_id):
    u = User.query.get(user_id)
    return u and u.role == 'admin'

# 1️⃣ Promote an existing user to Runner (or create a fresh Runner)
@runner_bp.route('/promote/<int:user_id>', methods=['PUT'])
@jwt_required()
def promote_to_runner(user_id):
    admin_id = get_jwt_identity()
    if not is_admin(admin_id):
        return jsonify({"error": "Unauthorized"}), 403

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    user.role = 'runner'
    db.session.commit()
    return jsonify({"message": f"User {user.name} is now a Runner."}), 200

# 2️⃣ Update Runner info (name, email, phone)
@runner_bp.route('/<int:runner_id>', methods=['PUT'])
@jwt_required()
def update_runner_info(runner_id):
    admin_id = get_jwt_identity()
    if not is_admin(admin_id):
        return jsonify({"error": "Unauthorized"}), 403

    runner = User.query.filter_by(id=runner_id, role='runner').first()
    if not runner:
        return jsonify({"error": "Runner not found"}), 404

    data = request.get_json() or {}
    for fld in ['name','email','phone']:
        if fld in data:
            setattr(runner, fld, data[fld].strip())
    db.session.commit()
    return jsonify({"message": "Runner info updated"}), 200

# 3️⃣ Toggle Runner active/inactive (ban/unban)
@runner_bp.route('/<int:runner_id>/active', methods=['PUT'])
@jwt_required()
def set_runner_active(runner_id):
    admin_id = get_jwt_identity()
    if not is_admin(admin_id):
        return jsonify({"error": "Unauthorized"}), 403

    runner = User.query.filter_by(id=runner_id, role='runner').first()
    if not runner:
        return jsonify({"error": "Runner not found"}), 404

    data = request.get_json() or {}
    if 'isActive' not in data:
        return jsonify({"error": "isActive required"}), 400

    runner.isActive = bool(data['isActive'])
    db.session.commit()
    status = "activated" if runner.isActive else "banned"
    return jsonify({"message": f"Runner {status}."}), 200

# 4️⃣ Assign a Runner to an Order
@runner_bp.route('/assign', methods=['POST'])
@jwt_required()
def assign_runner():
    admin_id = get_jwt_identity()
    if not is_admin(admin_id):
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json() or {}
    order_id = data.get('order_id')
    runner_id = data.get('runner_id')
    if not order_id or not runner_id:
        return jsonify({"error": "order_id and runner_id required"}), 400

    # Validate
    order = Order.query.get(order_id)
    runner = User.query.filter_by(id=runner_id, role='runner', isActive=True).first()
    if not order:
        return jsonify({"error": "Order not found"}), 404
    if not runner:
        return jsonify({"error": "Runner not available"}), 404

    # Check runner free (no open assignment)
    open_assign = RunnerAssignments.query.filter_by(
        runner_id=runner_id
    ).filter(RunnerAssignments.status.in_(['assigned','picked_up'])).first()
    if open_assign:
        return jsonify({"error": "Runner is currently engaged"}), 400

    # Create assignment
    ra = RunnerAssignments(order_id=order_id, runner_id=runner_id)
    db.session.add(ra)
    db.session.commit()
    return jsonify({"message": f"Runner {runner.name} assigned to order {order.id}"}), 201

@runner_bp.route('/assignment/<int:assign_id>', methods=['PUT'])
@jwt_required()
def update_assignment(assign_id):
    user_id = get_jwt_identity()
    user    = User.query.get(user_id)
    ra      = RunnerAssignments.query.get(assign_id)
    if not ra:
        return jsonify({"error": "Assignment not found"}), 404
    if user.role != 'admin' and ra.runner_id != user_id:
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json() or {}
    new_status = data.get('status')
    if new_status not in ['assigned','picked_up','delivered','cancelled']:
        return jsonify({"error": "Invalid status"}), 400

    # Explicit updates
    if new_status == 'picked_up':
        ra.picked_up_at    = datetime.utcnow()
        ra.status         = 'picked_up'
        ra.order.status   = 'Out_for_delivery'
    elif new_status == 'delivered':
        ra.delivered_at   = datetime.utcnow()
        ra.status         = 'delivered'
        ra.order.status   = 'Delivered'
    elif new_status == 'cancelled':
        ra.status         = 'cancelled'
        ra.order.status   = 'Cancelled'
    else:
        ra.status = 'assigned'

    db.session.commit()
    return jsonify({"message": f"Assignment and order marked '{new_status}'"}), 200




# 6️⃣ List Runners by Engagement
@runner_bp.route('/get_runner_list', methods=['GET'])
@jwt_required()
def list_runners():
    # optional filter ?status=free|engaged
    status = request.args.get('status')
    base = User.query.filter_by(role='runner', isActive=True)
    runners = []
    for r in base:
        open_assign = RunnerAssignments.query.filter_by(
            runner_id=r.id
        ).filter(RunnerAssignments.status.in_(['assigned','picked_up'])).first()
        engaged = bool(open_assign)
        if status=='free' and engaged:   continue
        if status=='engaged' and not engaged:   continue
        runners.append({
            "id": r.id,
            "name": r.name,
            "email": r.email,
            "phone": r.phone,
            "engaged": engaged
        })
    return jsonify(runners), 200

# 7️⃣ Get all Runners with full details
@runner_bp.route('/all_runners', methods=['GET'])
@jwt_required()
def get_all_runners():
    admin_id = get_jwt_identity()
    if not is_admin(admin_id):
        return jsonify({"error": "Unauthorized"}), 403

    runners = User.query.filter_by(role='runner').all()
    result = [ 
        {
            "id": r.id,
            "name": r.name,
            "email": r.email,
            "phone": r.phone,
            "isActive": r.isActive
        } for r in runners 
    ]
    return jsonify(result), 200


@runner_bp.route('/<int:runner_id>/history', methods=['GET'])
@jwt_required()
def get_runner_history(runner_id):
 
    current_user_id = get_jwt_identity()
    current = User.query.get(current_user_id)
    # only the runner themself or an admin can view
    if not (current.role == 'admin' or current.id == runner_id):
        return jsonify({"error": "Unauthorized"}), 403

    assignments = RunnerAssignments\
        .query\
        .filter_by(runner_id=runner_id)\
        .order_by(RunnerAssignments.assigned_at.desc())\
        .all()

    history = []
    for a in assignments:
        order = Order.query.get(a.order_id)
        history.append({
            "assignment_id":     a.id,
            "order_id":          a.order_id,
            "order_status":      order.status,
            "order_created_at":  order.created_at.isoformat(),
            "total_price":       order.total_price,
            "assigned_at":       a.assigned_at.isoformat(),
            "picked_up_at":      a.picked_up_at.isoformat() if a.picked_up_at else None,
            "delivered_at":      a.delivered_at.isoformat() if a.delivered_at else None,
            "assignment_status": a.status
        })

    return jsonify(history), 200
