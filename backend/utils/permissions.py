"""
Utility functions cho permission management
"""

from functools import wraps
from flask import request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User

def require_roles(*roles):
    """
    Decorator để yêu cầu role cụ thể
    Sử dụng: @require_roles('admin', 'manager')
    """
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            try:
                user_id = int(get_jwt_identity())
                user = User.query.get(user_id)
                
                if not user:
                    return jsonify({
                        'error': 'Unauthorized',
                        'message': 'User không tồn tại'
                    }), 401
                
                if user.role not in roles:
                    return jsonify({
                        'error': 'Forbidden',
                        'message': f'Bạn cần có quyền {", ".join(roles)} để truy cập API này'
                    }), 403
                
                return f(*args, **kwargs)
            except Exception as e:
                return jsonify({
                    'error': 'Authentication failed',
                    'message': 'Token không hợp lệ hoặc đã hết hạn'
                }), 401
        return decorated_function
    return decorator

def require_permissions(*permissions):
    """
    Decorator để yêu cầu permission cụ thể
    Sử dụng: @require_permissions('user:read', 'user:write')
    """
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            try:
                user_id = int(get_jwt_identity())
                
                # Lấy user từ database để kiểm tra permissions
                user = User.query.get(user_id)
                if not user:
                    return jsonify({
                        'error': 'User not found',
                        'message': 'Không tìm thấy user'
                    }), 404
                
                # Kiểm tra permissions dựa trên role
                user_permissions = get_permissions_by_role(user.role)
                
                for permission in permissions:
                    if permission not in user_permissions:
                        return jsonify({
                            'error': 'Forbidden',
                            'message': f'Bạn cần có quyền {permission} để truy cập API này'
                        }), 403
                
                return f(*args, **kwargs)
            except Exception as e:
                return jsonify({
                    'error': 'Authentication failed',
                    'message': 'Token không hợp lệ hoặc đã hết hạn'
                }), 401
        return decorated_function
    return decorator

def require_ownership(resource_type):
    """
    Decorator để yêu cầu quyền sở hữu resource
    Sử dụng: @require_ownership('user') - kiểm tra user_id trong URL
    """
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            try:
                current_user_id = int(get_jwt_identity())
                user = User.query.get(current_user_id)
                
                if not user:
                    return jsonify({
                        'error': 'User not found',
                        'message': 'Không tìm thấy user'
                    }), 404
                
                # Admin có thể truy cập tất cả
                if user.role == 'admin':
                    return f(*args, **kwargs)
                
                # Kiểm tra quyền sở hữu dựa trên resource_type
                if resource_type == 'user':
                    # Kiểm tra user_id trong URL params
                    target_user_id = kwargs.get('user_id')
                    if target_user_id and int(target_user_id) != int(current_user_id):
                        return jsonify({
                            'error': 'Forbidden',
                            'message': 'Bạn chỉ có thể truy cập thông tin của chính mình'
                        }), 403
                
                return f(*args, **kwargs)
            except Exception as e:
                return jsonify({
                    'error': 'Authentication failed',
                    'message': 'Token không hợp lệ hoặc đã hết hạn'
                }), 401
        return decorated_function
    return decorator

def get_permissions_by_role(role):
    """
    Lấy danh sách permissions theo role
    """
    permissions_map = {
        'admin': [
            'user:read', 'user:write', 'user:delete',
            'admin:read', 'admin:write', 'admin:delete',
            'system:read', 'system:write', 'system:delete'
        ],
        'manager': [
            'user:read', 'user:write',
            'admin:read',
            'system:read'
        ],
        'user': [
            'user:read', 'user:write'
        ]
    }
    
    return permissions_map.get(role, [])

def is_admin():
    """
    Kiểm tra user hiện tại có phải admin không
    """
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        return user and user.role == 'admin'
    except:
        return False

def is_owner(user_id):
    """
    Kiểm tra user hiện tại có phải chủ sở hữu không
    """
    try:
        current_user_id = int(get_jwt_identity())
        return int(current_user_id) == int(user_id)
    except:
        return False

def has_permission(permission):
    """
    Kiểm tra user hiện tại có permission cụ thể không
    """
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        if not user:
            return False
        user_permissions = get_permissions_by_role(user.role)
        return permission in user_permissions
    except:
        return False 