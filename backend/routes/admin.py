from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.permissions import require_roles, require_permissions
from utils.rate_limit import apply_rate_limit
from models import db

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard')
@require_roles('admin')
@apply_rate_limit("60 per minute")
def admin_dashboard():
    return jsonify({
        'message': 'Welcome to the admin dashboard!',
        'role': 'admin',
        'permissions': ['user:read', 'user:write', 'user:delete', 'admin:read', 'admin:write', 'admin:delete']
    })

@admin_bp.route('/users')
@require_roles('admin', 'manager')
@require_permissions('user:read')
@apply_rate_limit("30 per minute")
def get_all_users():
    """Lấy danh sách tất cả users (chỉ admin và manager)"""
    from models import User
    
    users = User.query.all()
    return jsonify({
        'message': 'Danh sách users',
        'users': [user.to_dict() for user in users],
        'total': len(users)
    })

@admin_bp.route('/users/<int:user_id>')
@require_roles('admin', 'manager')
@require_permissions('user:read')
@apply_rate_limit("30 per minute")
def get_user_by_id(user_id):
    """Lấy thông tin user theo ID (chỉ admin và manager)"""
    from models import User
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'message': 'Thông tin user',
        'user': user.to_dict()
    })

@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
@require_roles('admin')
@require_permissions('user:write')
@apply_rate_limit("20 per minute")
def update_user(user_id):
    """Cập nhật thông tin user (chỉ admin)"""
    from flask import request
    from models import User
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    
    # Cập nhật các trường được phép
    if 'full_name' in data:
        user.full_name = data['full_name']
    if 'email' in data:
        user.email = data['email']
    if 'phone' in data:
        user.phone = data['phone']
    if 'role' in data and data['role'] in ['admin', 'manager', 'user']:
        user.role = data['role']
    if 'is_active' in data:
        user.is_active = data['is_active']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Cập nhật user thành công',
        'user': user.to_dict()
    })

@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@require_roles('admin')
@require_permissions('user:delete')
@apply_rate_limit("10 per minute")
def delete_user(user_id):
    """Xóa user (chỉ admin)"""
    from models import User
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Không cho phép xóa admin chính
    if user.role == 'admin':
        return jsonify({'error': 'Không thể xóa admin'}), 400
    
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({
        'message': 'Xóa user thành công',
        'deleted_user_id': user_id
    }) 