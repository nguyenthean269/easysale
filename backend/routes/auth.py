from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, db
from utils.permissions import require_roles, require_permissions, get_permissions_by_role
from utils.rate_limit import apply_rate_limit
import re

auth_bp = Blueprint('auth', __name__)

def validate_email(email):
    """Kiểm tra email hợp lệ"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Kiểm tra mật khẩu mạnh"""
    if len(password) < 6:
        return False, "Mật khẩu phải có ít nhất 6 ký tự"
    return True, ""

@auth_bp.route('/register', methods=['POST'])
@apply_rate_limit("5 per minute")
@apply_rate_limit("20 per hour")
def register():
    try:
        data = request.get_json()
        
        # Kiểm tra dữ liệu đầu vào
        required_fields = ['username', 'password', 'email', 'full_name']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Trường {field} là bắt buộc'}), 400
        
        username = data.get('username').strip()
        password = data.get('password')
        email = data.get('email').strip().lower()
        full_name = data.get('full_name').strip()
        phone = data.get('phone', '').strip()
        
        # Kiểm tra độ dài username
        if len(username) < 3:
            return jsonify({'error': 'Tên đăng nhập phải có ít nhất 3 ký tự'}), 400
        
        # Kiểm tra email hợp lệ
        if not validate_email(email):
            return jsonify({'error': 'Email không hợp lệ'}), 400
        
        # Kiểm tra mật khẩu mạnh
        is_valid_password, password_error = validate_password(password)
        if not is_valid_password:
            return jsonify({'error': password_error}), 400
        
        # Kiểm tra username đã tồn tại
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return jsonify({'error': 'Tên đăng nhập đã tồn tại'}), 400
        
        # Kiểm tra email đã tồn tại
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            return jsonify({'error': 'Email đã được sử dụng'}), 400
        
        # Tạo user mới
        hashed_password = generate_password_hash(password)
        new_user = User(
            username=username,
            password=hashed_password,
            email=email,
            full_name=full_name,
            phone=phone,
            role='user'
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        # Tạo token cho user mới
        access_token = create_access_token(identity=str(new_user.id))
        refresh_token = create_refresh_token(identity=str(new_user.id))
        
        return jsonify({
            'message': 'Đăng ký thành công',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': new_user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Lỗi server, vui lòng thử lại sau'}), 500

@auth_bp.route('/login', methods=['POST'])
@apply_rate_limit("10 per minute")
@apply_rate_limit("50 per hour")
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Tên đăng nhập và mật khẩu là bắt buộc'}), 400
        
        # Tìm user trong database
        user = User.query.filter_by(username=username).first()
        
        if not user:
            return jsonify({'error': 'Tên đăng nhập hoặc mật khẩu không đúng'}), 401
        
        if not user.is_active:
            return jsonify({'error': 'Tài khoản đã bị khóa'}), 401
        
        # Kiểm tra mật khẩu
        if not check_password_hash(user.password, password):
            return jsonify({'error': 'Tên đăng nhập hoặc mật khẩu không đúng'}), 401
        
        # Tạo token với user_id làm identity (chuyển thành string)
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))
        
        return jsonify({
            'message': 'Đăng nhập thành công',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Lỗi server, vui lòng thử lại sau'}), 500

@auth_bp.route('/permissions', methods=['GET'])
@jwt_required()
@apply_rate_limit("30 per minute")
def get_user_permissions():
    """Lấy danh sách permissions của user hiện tại"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        user_role = user.role
        permissions = get_permissions_by_role(user_role)
        
        return jsonify({
            'message': 'Danh sách permissions',
            'role': user_role,
            'permissions': permissions,
            'total_permissions': len(permissions)
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Không thể lấy thông tin permissions'}), 500

@auth_bp.route('/rate-limit-status', methods=['GET'])
@apply_rate_limit("10 per minute")
def get_rate_limit_status():
    """Lấy thông tin về rate limit hiện tại"""
    try:
        from utils.rate_limit import get_rate_limit_info
        info = get_rate_limit_info()
        return jsonify({
            'message': 'Rate limit status',
            'data': info
        }), 200
    except Exception as e:
        return jsonify({'error': 'Không thể lấy thông tin rate limit'}), 500

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
@apply_rate_limit("30 per minute")
def get_profile():
    """Lấy thông tin profile của user hiện tại"""
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'Không tìm thấy user'}), 404
        
        return jsonify({'user': user.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': 'Lỗi server, vui lòng thử lại sau'}), 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
@apply_rate_limit("30 per minute")
def refresh():
    """Refresh access token bằng refresh token"""
    try:
        # Lấy thông tin token hiện tại
        jwt_data = get_jwt()
        
        # Kiểm tra xem có phải refresh token không
        if jwt_data.get('type') != 'refresh':
            return jsonify({
                'error': 'Invalid token type',
                'message': 'Chỉ chấp nhận refresh token'
            }), 401
        
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User không tồn tại'}), 404
        
        if not user.is_active:
            return jsonify({'error': 'Tài khoản đã bị khóa'}), 401
        
        # Tạo access token mới
        new_access_token = create_access_token(identity=str(user.id))
        
        return jsonify({
            'message': 'Token đã được refresh thành công',
            'access_token': new_access_token
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Lỗi server, vui lòng thử lại sau'}), 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
@apply_rate_limit("30 per minute")
def logout():
    """Đăng xuất và vô hiệu hóa token"""
    try:
        # Lấy thông tin token hiện tại
        jti = get_jwt()["jti"]
        
        # Trong thực tế, bạn có thể lưu jti vào blacklist để vô hiệu hóa token
        # Ở đây chúng ta chỉ trả về thông báo thành công
        
        return jsonify({
            'message': 'Đăng xuất thành công'
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Lỗi server, vui lòng thử lại sau'}), 500 