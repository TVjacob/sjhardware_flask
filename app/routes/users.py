from flask import Blueprint, request, jsonify
from app import db
from app.models import User, Permission
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

users_bp = Blueprint('users', __name__, url_prefix='/users')

# ---------------- User Routes ---------------- #

# Create a new user
@users_bp.route('/', methods=['POST'])
def create_user():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    role = data.get('role', 'Staff')

    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already exists"}), 400

    user = User(
        username=username,
        role=role,
        status=1,  # Active
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User created", "user_id": user.id}), 201

# Get all users
@users_bp.route('/', methods=['GET'])
def get_users():
    users = User.query.all()
    data = []
    for u in users:
        data.append({
            "id": u.id,
            "username": u.username,
            "role": u.role,
            "status": u.status,
            "created_at": u.created_at,
            "updated_at": u.updated_at,
            "permissions": [p.name for p in u.permissions]
        })
    return jsonify(data)

# Get a user by ID
@users_bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify({
        "id": user.id,
        "username": user.username,
        "role": user.role,
        "status": user.status,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
        "permissions": [p.name for p in user.permissions]
    })

# Update a user
@users_bp.route('/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.json

    user.username = data.get('username', user.username)
    user.role = data.get('role', user.role)
    if 'password' in data and data['password']:
        user.set_password(data['password'])
    user.updated_at = datetime.utcnow()
    db.session.commit()

    return jsonify({"message": "User updated", "user_id": user.id})

# Delete a user
@users_bp.route('/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted", "user_id": user.id})

# ---------------- Permission Routes ---------------- #

# Create a permission
@users_bp.route('/permissions', methods=['POST'])
def create_permission():
    data = request.json
    name = data.get('name')
    description = data.get('description', '')

    if Permission.query.filter_by(name=name).first():
        return jsonify({"error": "Permission already exists"}), 400

    perm = Permission(
        name=name,
        description=description,
        status=1,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.session.add(perm)
    db.session.commit()

    return jsonify({"message": "Permission created", "permission_id": perm.id}), 201


@users_bp.route('/permissions', methods=['GET'])
def get_permissions():
    permissions = Permission.query.all()

    return jsonify([
        {
            "id": perm.id,
            "name": perm.name,
            "description": perm.description,
            "status": perm.status,
            "created_at": perm.created_at,
            "updated_at": perm.updated_at
        } for perm in permissions
    ])


# Assign permission to user
@users_bp.route('/<int:user_id>/permissions/<int:perm_id>', methods=['POST'])
def assign_permission(user_id, perm_id):
    user = User.query.get_or_404(user_id)
    perm = Permission.query.get_or_404(perm_id)
    user.add_permission(perm)
    user.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify({"message": f"Permission '{perm.name}' assigned to user '{user.username}'"})

# Remove permission from user
@users_bp.route('/<int:user_id>/permissions/<int:perm_id>', methods=['DELETE'])
def remove_permission(user_id, perm_id):
    user = User.query.get_or_404(user_id)
    perm = Permission.query.get_or_404(perm_id)
    user.remove_permission(perm)
    user.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify({"message": f"Permission '{perm.name}' removed from user '{user.username}'"})
