from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.permissions import require_roles
from utils.rate_limit import apply_rate_limit
from models import Post
from models import db

posts_bp = Blueprint('posts', __name__)

@posts_bp.route('/', methods=['GET'])
@jwt_required()
@require_roles('user', 'manager', 'admin')
@apply_rate_limit("30 per minute")
def list_posts():
    """
    Lấy danh sách tất cả bài viết
    """
    try:
        # Lấy tham số query
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status')  # 'draft' hoặc 'posted'
        
        # Xây dựng query
        query = Post.query
        
        # Lọc theo status nếu có
        if status:
            query = query.filter(Post.staus == status)
        
        # Sắp xếp theo thời gian tạo mới nhất
        query = query.order_by(Post.created_at.desc())
        
        # Phân trang
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        posts = pagination.items
        
        return jsonify({
            'success': True,
            'data': {
                'posts': [post.to_dict() for post in posts],
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': pagination.total,
                    'pages': pagination.pages,
                    'has_next': pagination.has_next,
                    'has_prev': pagination.has_prev
                }
            }
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Lỗi khi lấy danh sách bài viết',
            'message': str(e)
        }), 500

@posts_bp.route('/<int:post_id>', methods=['GET'])
@jwt_required()
@require_roles('user', 'manager', 'admin')
@apply_rate_limit("30 per minute")
def get_post_detail(post_id):
    """
    Lấy chi tiết bài viết theo ID
    """
    try:
        post = Post.query.get(post_id)
        
        if not post:
            return jsonify({
                'error': 'Không tìm thấy bài viết',
                'message': f'Bài viết với ID {post_id} không tồn tại'
            }), 404
        
        return jsonify({
            'success': True,
            'data': post.to_dict()
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Lỗi khi lấy chi tiết bài viết',
            'message': str(e)
        }), 500

@posts_bp.route('/', methods=['POST'])
@jwt_required()
@require_roles('user', 'manager', 'admin')
@apply_rate_limit("10 per minute")
def create_post():
    """
    Tạo bài viết mới
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Dữ liệu không được cung cấp'}), 400
        
        content = data.get('content')
        if not content:
            return jsonify({'error': 'Nội dung bài viết là bắt buộc'}), 400
        
        status = data.get('staus', 'draft')  # Default là draft
        if status not in ['draft', 'posted']:
            return jsonify({'error': 'Trạng thái không hợp lệ. Chỉ chấp nhận: draft, posted'}), 400
        
        # Tạo bài viết mới
        new_post = Post(
            content=content,
            staus=status
        )
        
        db.session.add(new_post)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Tạo bài viết thành công',
            'data': new_post.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Lỗi khi tạo bài viết',
            'message': str(e)
        }), 500

@posts_bp.route('/<int:post_id>', methods=['PUT'])
@jwt_required()
@require_roles('user', 'manager', 'admin')
@apply_rate_limit("10 per minute")
def update_post(post_id):
    """
    Cập nhật bài viết
    """
    try:
        post = Post.query.get(post_id)
        
        if not post:
            return jsonify({
                'error': 'Không tìm thấy bài viết',
                'message': f'Bài viết với ID {post_id} không tồn tại'
            }), 404
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Dữ liệu không được cung cấp'}), 400
        
        # Cập nhật các trường
        if 'content' in data:
            post.content = data['content']
        
        if 'staus' in data:
            if data['staus'] not in ['draft', 'posted']:
                return jsonify({'error': 'Trạng thái không hợp lệ. Chỉ chấp nhận: draft, posted'}), 400
            post.staus = data['staus']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Cập nhật bài viết thành công',
            'data': post.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Lỗi khi cập nhật bài viết',
            'message': str(e)
        }), 500

@posts_bp.route('/<int:post_id>', methods=['DELETE'])
@jwt_required()
@require_roles('manager', 'admin')
@apply_rate_limit("5 per minute")
def delete_post(post_id):
    """
    Xóa bài viết
    """
    try:
        post = Post.query.get(post_id)
        
        if not post:
            return jsonify({
                'error': 'Không tìm thấy bài viết',
                'message': f'Bài viết với ID {post_id} không tồn tại'
            }), 404
        
        db.session.delete(post)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Xóa bài viết thành công'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Lỗi khi xóa bài viết',
            'message': str(e)
        }), 500 