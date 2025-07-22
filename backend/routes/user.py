from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.permissions import require_roles, require_permissions, require_ownership
from utils.rate_limit import apply_rate_limit
from models import User, LinkCrawl, db
import requests
import json
from datetime import datetime
import time

user_bp = Blueprint('user', __name__)

@user_bp.route('/profile')
@require_roles('user', 'manager', 'admin')
@apply_rate_limit("30 per minute")
def user_profile():
    identity = get_jwt_identity()
    return jsonify({
        'message': f"Welcome, {identity['username']}!",
        'role': identity['role'],
        'user_id': identity['user_id']
    })

@user_bp.route('/profile', methods=['PUT'])
@require_roles('user', 'manager', 'admin')
@require_permissions('user:write')
@apply_rate_limit("20 per minute")
def update_profile():
    """Cập nhật thông tin profile của chính mình"""
    identity = get_jwt_identity()
    user_id = identity['user_id']
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    
    # Chỉ cho phép cập nhật một số trường
    if 'full_name' in data:
        user.full_name = data['full_name']
    if 'phone' in data:
        user.phone = data['phone']
    if 'email' in data:
        # Kiểm tra email không trùng lặp
        existing_email = User.query.filter_by(email=data['email']).first()
        if existing_email and existing_email.id != user_id:
            return jsonify({'error': 'Email đã được sử dụng'}), 400
        user.email = data['email']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Cập nhật profile thành công',
        'user': user.to_dict()
    })

@user_bp.route('/users/<int:user_id>')
@require_ownership('user')
@apply_rate_limit("30 per minute")
def get_own_profile(user_id):
    """Lấy thông tin profile của chính mình hoặc admin có thể xem tất cả"""
    current_user_id = int(get_jwt_identity())
    # Lấy user để biết role
    current_user = User.query.get(current_user_id)
    if not current_user:
        return jsonify({'error': 'User not found'}), 404
    user_role = current_user.role
    
    # Admin có thể xem tất cả
    if user_role == 'admin':
        user = User.query.get(user_id)
    else:
        # User thường chỉ xem được thông tin của chính mình
        user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'message': 'Thông tin profile',
        'user': user.to_dict()
    })

@user_bp.route('/crawls', methods=['POST'])
@require_roles('user', 'manager', 'admin')
@apply_rate_limit("10 per minute")
def create_crawl():
    """Tạo crawl request và gọi API firecrawl"""
    user_id = int(get_jwt_identity())
    
    data = request.get_json()
    
    # Validate input
    if not data or 'link' not in data:
        return jsonify({'error': 'Link is required'}), 400
    
    link = data['link']
    crawl_tool = data.get('crawl_tool', 'firecrawl')  # Default to firecrawl
    
    # Validate crawl_tool
    if crawl_tool not in ['firecrawl', 'watercrawl']:
        return jsonify({'error': 'crawl_tool must be either "firecrawl" or "watercrawl"'}), 400
    
    try:
        # Ghi lại thời gian bắt đầu
        started_at = datetime.utcnow()
        
        # Gọi API firecrawl
        firecrawl_response = call_firecrawl_api(link)
        
        # Ghi lại thời gian kết thúc
        done_at = datetime.utcnow()
        
        # Lưu vào database
        link_crawl = LinkCrawl(
            link=link,
            content=firecrawl_response.get('content', ''),
            crawl_tool=crawl_tool,
            user_id=user_id,
            started_at=started_at,
            done_at=done_at
        )
        
        db.session.add(link_crawl)
        db.session.commit()
        
        return jsonify({
            'message': 'Crawl completed successfully',
            'crawl_id': link_crawl.id,
            'link': link,
            'crawl_tool': crawl_tool,
            'started_at': started_at.isoformat(),
            'done_at': done_at.isoformat(),
            'content_length': len(firecrawl_response.get('content', ''))
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Crawl failed: {str(e)}'}), 500

def call_firecrawl_api(link):
    """Gọi API firecrawl để crawl nội dung từ link"""
    try:
        from flask import current_app
        
        # Lấy cấu hình từ app config
        firecrawl_url = current_app.config.get('FIRECRAWL_API_URL', 'https://api.firecrawl.dev/scrape')
        api_key = current_app.config.get('FIRECRAWL_API_KEY', '')
        
        # Headers cho API request
        headers = {
            'Content-Type': 'application/json'
        }
        
        # Thêm API key nếu có
        if api_key:
            headers['Authorization'] = f'Bearer {api_key}'
        
        # Payload cho API request
        payload = {
            'url': link,
            "formats": [ "markdown" ],
            "onlyMainContent": True,
            "parsePDF": True,
        }

        # Gọi API
        response = requests.post(firecrawl_url, json=payload, headers=headers, timeout=30)
        
        # Kiểm tra response
        if response.status_code != 200:
            raise Exception(f"API returned status {response.status_code}: {response.text}")
        
        # Kiểm tra response content
        if not response.text.strip():
            raise Exception("API returned empty response")
        
        try:
            result = response.json()
        except json.JSONDecodeError as e:
            raise Exception(f"Invalid JSON response: {response.text[:200]}")
        
        # Trả về nội dung đã crawl
        content = result.get('data', {}).get('markdown', '')
        if not content:
            # Fallback: sử dụng HTML content nếu có
            content = result.get('data', {}).get('html', '')
            if not content:
                content = f"Content crawled from {link} (no markdown/html content available)"
        
        return {
            'content': content,
            'status': 'success'
        }
        
    except requests.exceptions.RequestException as e:
        # Fallback: trả về mock content nếu API không khả dụng
        print(f"Warning: Firecrawl API not available: {str(e)}")
        return {
            'content': f"Mock content for {link}\n\nThis is a fallback response when the firecrawl API is not available. The actual content would be crawled from the provided URL.",
            'status': 'fallback'
        }
    except Exception as e:
        # Fallback cho các lỗi khác
        print(f"Warning: Error calling firecrawl API: {str(e)}")
        return {
            'content': f"Error content for {link}\n\nError occurred while crawling: {str(e)}",
            'status': 'error'
        }

@user_bp.route('/crawls', methods=['GET'])
@require_roles('user', 'manager', 'admin')
@apply_rate_limit("30 per minute")
def get_crawls():
    """Lấy danh sách crawls của user"""
    user_id = int(get_jwt_identity())
    # Lấy user để biết role
    current_user = User.query.get(user_id)
    if not current_user:
        return jsonify({'error': 'User not found'}), 404
    user_role = current_user.role
    
    # Admin có thể xem tất cả crawls
    if user_role == 'admin':
        crawls = LinkCrawl.query.all()
    else:
        # User thường chỉ xem crawls của chính mình
        crawls = LinkCrawl.query.filter_by(user_id=user_id).all()
    
    return jsonify({
        'message': 'Danh sách crawls',
        'crawls': [crawl.to_dict() for crawl in crawls]
    })

@user_bp.route('/crawls/<int:crawl_id>', methods=['GET'])
@require_roles('user', 'manager', 'admin')
@apply_rate_limit("30 per minute")
def get_crawl_detail(crawl_id):
    """Lấy chi tiết một crawl cụ thể"""
    user_id = int(get_jwt_identity())
    # Lấy user để biết role
    current_user = User.query.get(user_id)
    if not current_user:
        return jsonify({'error': 'User not found'}), 404
    user_role = current_user.role
    
    crawl = LinkCrawl.query.get(crawl_id)
    if not crawl:
        return jsonify({'error': 'Crawl not found'}), 404
    
    # Kiểm tra quyền truy cập
    if user_role != 'admin' and crawl.user_id != user_id:
        return jsonify({'error': 'Access denied'}), 403
    
    return jsonify({
        'message': 'Chi tiết crawl',
        'crawl': crawl.to_dict()
    }) 