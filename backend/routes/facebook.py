from flask import Blueprint, request, jsonify, current_app
from flask_cors import cross_origin
from flask_jwt_extended import jwt_required, get_jwt_identity
import json
import logging
from datetime import datetime

# Add the backend directory to the Python path
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from utils.facebook_service import FacebookService
from utils.permissions import require_roles
from utils.rate_limit import apply_rate_limit
from models import db, Conversation, Message, FacebookPage
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Blueprint
facebook_bp = Blueprint('facebook', __name__)

# Initialize Facebook service
facebook_service = FacebookService()

@facebook_bp.route('/webhook', methods=['GET'])
@cross_origin()
def verify_webhook():
    """
    Facebook webhook verification endpoint
    """
    try:
        # Get verification parameters from Facebook
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        
        # Your verify token (should match what you set in Facebook App)
        verify_token = Config.FACEBOOK_VERIFY_TOKEN
        
        logger.info(f"Webhook verification request - Mode: {mode}, Token: {token}")
        
        # Verify the webhook
        if mode and token and challenge:
            result = facebook_service.verify_webhook(mode, token, challenge, verify_token)
            if result:
                logger.info("Webhook verified successfully")
                return result, 200
            else:
                logger.error("Webhook verification failed")
                return "Verification failed", 403
        else:
            logger.error("Missing webhook verification parameters")
            return "Missing parameters", 400
            
    except Exception as e:
        logger.error(f"Error in webhook verification: {e}")
        return "Internal server error", 500

@facebook_bp.route('/webhook', methods=['POST'])
@cross_origin()
def webhook():
    """
    Facebook webhook endpoint to receive messages
    """
    try:
        # Get the request body
        body = request.get_data(as_text=True)
        
        # Verify signature if app secret is configured
        if hasattr(Config, 'FACEBOOK_APP_SECRET') and Config.FACEBOOK_APP_SECRET:
            signature = request.headers.get('X-Hub-Signature-256', '')
            if not facebook_service.verify_signature(signature, body, Config.FACEBOOK_APP_SECRET):
                logger.error("Invalid webhook signature")
                return "Invalid signature", 403
        
        # Parse the webhook data
        data = json.loads(body)
        logger.info(f"Received webhook data: {json.dumps(data, indent=2)}")
        
        # Process the webhook message
        result = facebook_service.process_webhook_message(data)
        
        if result['success']:
            logger.info(f"Webhook processed successfully: {result['message']}")
            return jsonify(result), 200
        else:
            logger.error(f"Webhook processing failed: {result['message']}")
            return jsonify(result), 400
            
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in webhook: {e}")
        return "Invalid JSON", 400
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return "Internal server error", 500

@facebook_bp.route('/send-message', methods=['POST'])
@cross_origin()
@require_roles('user', 'manager', 'admin')
def send_message():
    """
    Send message via Facebook Messenger API
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        # Validate required fields
        required_fields = ['page_id', 'recipient_id', 'message_text']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'Missing required field: {field}'
                }), 400
        
        page_id = data['page_id']
        recipient_id = data['recipient_id']
        message_text = data['message_text']
        conversation_id = data.get('conversation_id')  # Optional
        
        logger.info(f"Sending message to {recipient_id} via page {page_id}: {message_text}")
        
        # Send the message
        result = facebook_service.send_message(
            page_id=page_id,
            recipient_id=recipient_id,
            message_text=message_text,
            conversation_id=conversation_id
        )
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Error sending Facebook message: {e}")
        return jsonify({
            'success': False,
            'message': f'Error sending message: {str(e)}'
        }), 500

@facebook_bp.route('/typing-indicator', methods=['POST'])
@cross_origin()
@require_roles('user', 'manager', 'admin')
def send_typing_indicator():
    """
    Send typing indicator
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        # Validate required fields
        required_fields = ['page_id', 'recipient_id']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'Missing required field: {field}'
                }), 400
        
        page_id = data['page_id']
        recipient_id = data['recipient_id']
        typing = data.get('typing', True)  # Default to True
        
        logger.info(f"Sending typing indicator to {recipient_id} via page {page_id}")
        
        # Send typing indicator
        result = facebook_service.send_typing_indicator(
            page_id=page_id,
            recipient_id=recipient_id,
            typing=typing
        )
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Error sending typing indicator: {e}")
        return jsonify({
            'success': False,
            'message': f'Error sending typing indicator: {str(e)}'
        }), 500

@facebook_bp.route('/pages', methods=['GET'])
@cross_origin()
@require_roles('user', 'manager', 'admin')
def get_pages():
    """
    Get all active Facebook pages
    """
    try:
        pages = facebook_service.get_all_active_pages()
        
        return jsonify({
            'success': True,
            'pages': pages,
            'count': len(pages)
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting Facebook pages: {e}")
        return jsonify({
            'success': False,
            'message': f'Error getting pages: {str(e)}'
        }), 500

@facebook_bp.route('/pages/<page_id>', methods=['GET'])
@cross_origin()
@require_roles('user', 'manager', 'admin')
def get_page_info(page_id):
    """
    Get specific Facebook page information
    """
    try:
        page_info = facebook_service.get_page_info(page_id)
        
        if page_info:
            return jsonify({
                'success': True,
                'page': page_info
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Page not found or inactive'
            }), 404
            
    except Exception as e:
        logger.error(f"Error getting page info: {e}")
        return jsonify({
            'success': False,
            'message': f'Error getting page info: {str(e)}'
        }), 500

@facebook_bp.route('/pages', methods=['POST'])
@cross_origin()
@require_roles('admin')
def create_page():
    """
    Create a new Facebook page entry
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        # Validate required fields
        required_fields = ['page_id', 'page_name', 'page_access_token']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'Missing required field: {field}'
                }), 400
        
        # Check if page already exists
        existing_page = FacebookPage.query.filter_by(page_id=data['page_id']).first()
        if existing_page:
            return jsonify({
                'success': False,
                'message': 'Page already exists'
            }), 409
        
        # Create new page
        new_page = FacebookPage(
            chatbot_id=data.get('chatbot_id'),
            page_id=data['page_id'],
            page_name=data['page_name'],
            page_access_token=data['page_access_token'],
            status=data.get('status', True)
        )
        
        db.session.add(new_page)
        db.session.commit()
        
        logger.info(f"Created new Facebook page: {new_page.page_id}")
        
        return jsonify({
            'success': True,
            'message': 'Page created successfully',
            'page': new_page.to_dict()
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating Facebook page: {e}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error creating page: {str(e)}'
        }), 500

@facebook_bp.route('/pages/<int:page_id>', methods=['PUT'])
@cross_origin()
@require_roles('admin')
def update_page(page_id):
    """
    Update Facebook page information
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        # Find the page
        page = FacebookPage.query.get(page_id)
        if not page:
            return jsonify({
                'success': False,
                'message': 'Page not found'
            }), 404
        
        # Update fields
        if 'page_name' in data:
            page.page_name = data['page_name']
        if 'page_access_token' in data:
            page.page_access_token = data['page_access_token']
        if 'status' in data:
            page.status = data['status']
        if 'chatbot_id' in data:
            page.chatbot_id = data['chatbot_id']
        
        page.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        logger.info(f"Updated Facebook page: {page.page_id}")
        
        return jsonify({
            'success': True,
            'message': 'Page updated successfully',
            'page': page.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Error updating Facebook page: {e}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error updating page: {str(e)}'
        }), 500

@facebook_bp.route('/pages/<int:page_id>', methods=['DELETE'])
@cross_origin()
@require_roles('admin')
def delete_page(page_id):
    """
    Delete Facebook page (soft delete by setting status to False)
    """
    try:
        # Find the page
        page = FacebookPage.query.get(page_id)
        if not page:
            return jsonify({
                'success': False,
                'message': 'Page not found'
            }), 404
        
        # Soft delete by setting status to False
        page.status = False
        page.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        logger.info(f"Deleted Facebook page: {page.page_id}")
        
        return jsonify({
            'success': True,
            'message': 'Page deleted successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Error deleting Facebook page: {e}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error deleting page: {str(e)}'
        }), 500

@facebook_bp.route('/conversations/<int:conversation_id>/messages', methods=['GET'])
@cross_origin()
@require_roles('user', 'manager', 'admin')
def get_conversation_messages(conversation_id):
    """
    Get messages for a specific conversation
    """
    try:
        # Check if conversation exists
        conversation = Conversation.query.get(conversation_id)
        if not conversation:
            return jsonify({
                'success': False,
                'message': 'Conversation not found'
            }), 404
        
        # Get messages for this conversation
        messages = Message.query.filter_by(conversation_id=conversation_id).order_by(Message.created_at.asc()).all()
        
        return jsonify({
            'success': True,
            'conversation': conversation.to_dict(),
            'messages': [message.to_dict() for message in messages],
            'count': len(messages)
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting conversation messages: {e}")
        return jsonify({
            'success': False,
            'message': f'Error getting messages: {str(e)}'
        }), 500

# ============================================================================
# FACEBOOK PAGES MANAGEMENT (ADVANCED)
# ============================================================================

@facebook_bp.route('/pages-advanced', methods=['GET'])
@jwt_required()
@require_roles('user', 'manager', 'admin')
@apply_rate_limit("30 per minute")
def list_facebook_pages_advanced():
    """
    Lấy danh sách tất cả Facebook pages với phân trang và lọc
    """
    try:
        # Lấy tham số query
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status')  # 'true' hoặc 'false'
        
        # Xây dựng query
        query = FacebookPage.query
        
        # Lọc theo status nếu có
        if status is not None:
            status_bool = status.lower() == 'true'
            query = query.filter(FacebookPage.status == status_bool)
        
        # Sắp xếp theo thời gian tạo mới nhất
        query = query.order_by(FacebookPage.created_at.desc())
        
        # Phân trang
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        facebook_pages = pagination.items
        
        return jsonify({
            'success': True,
            'data': {
                'facebook_pages': [page.to_dict() for page in facebook_pages],
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
            'error': 'Lỗi khi lấy danh sách Facebook pages',
            'message': str(e)
        }), 500

@facebook_bp.route('/pages/<int:page_id>/toggle-status', methods=['PUT'])
@jwt_required()
@require_roles('manager', 'admin')
@apply_rate_limit("10 per minute")
def toggle_facebook_page_status(page_id):
    """
    Bật/tắt trạng thái Facebook page
    """
    try:
        facebook_page = FacebookPage.query.get(page_id)
        
        if not facebook_page:
            return jsonify({
                'error': 'Không tìm thấy Facebook page',
                'message': f'Facebook page với ID {page_id} không tồn tại'
            }), 404
        
        # Đảo ngược trạng thái
        facebook_page.status = not facebook_page.status
        
        db.session.commit()
        
        status_text = "bật" if facebook_page.status else "tắt"
        
        return jsonify({
            'success': True,
            'message': f'Đã {status_text} Facebook page thành công',
            'data': facebook_page.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Lỗi khi thay đổi trạng thái Facebook page',
            'message': str(e)
        }), 500

# ============================================================================
# FACEBOOK POSTING
# ============================================================================

@facebook_bp.route('/pages/<int:page_id>/post', methods=['POST'])
@jwt_required()
@require_roles('manager', 'admin')
@apply_rate_limit("5 per minute")
def create_facebook_post(page_id):
    """
    Đăng bài lên Facebook page
    """
    try:
        # Kiểm tra Facebook page có tồn tại và active không
        facebook_page = FacebookPage.query.get(page_id)
        if not facebook_page:
            return jsonify({
                'error': 'Không tìm thấy Facebook page',
                'message': f'Facebook page với ID {page_id} không tồn tại'
            }), 404
        
        if not facebook_page.status:
            return jsonify({
                'error': 'Facebook page không hoạt động',
                'message': 'Facebook page này đã bị tắt. Vui lòng bật lại để đăng bài.'
            }), 400
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Dữ liệu không được cung cấp'}), 400
        
        message = data.get('message')
        if not message:
            return jsonify({'error': 'Nội dung bài viết là bắt buộc'}), 400
        
        link = data.get('link')
        image_url = data.get('image_url')
        
        # Đăng bài lên Facebook
        if image_url:
            # Đăng bài có hình ảnh
            result = facebook_service.create_post_with_image(
                page_id=facebook_page.page_id,
                message=message,
                image_url=image_url
            )
        else:
            # Đăng bài thường
            result = facebook_service.create_post(
                page_id=facebook_page.page_id,
                message=message,
                link=link,
                image_url=image_url
            )
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': 'Đăng bài lên Facebook thành công',
                'data': {
                    'post_id': result['post_id'],
                    'facebook_page_id': facebook_page.page_id,
                    'facebook_page_name': facebook_page.page_name,
                    'message': message,
                    'link': link,
                    'image_url': image_url,
                    'facebook_response': result.get('facebook_response', {})
                }
            })
        else:
            return jsonify({
                'error': 'Lỗi khi đăng bài lên Facebook',
                'message': result['message'],
                'facebook_response': result.get('facebook_response', {})
            }), 500
        
    except Exception as e:
        return jsonify({
            'error': 'Lỗi khi đăng bài lên Facebook',
            'message': str(e)
        }), 500

@facebook_bp.route('/pages/<int:page_id>/post-schedule', methods=['POST'])
@jwt_required()
@require_roles('manager', 'admin')
@apply_rate_limit("3 per minute")
def schedule_facebook_post(page_id):
    """
    Lên lịch đăng bài lên Facebook page (tính năng mở rộng)
    """
    try:
        # Kiểm tra Facebook page có tồn tại và active không
        facebook_page = FacebookPage.query.get(page_id)
        if not facebook_page:
            return jsonify({
                'error': 'Không tìm thấy Facebook page',
                'message': f'Facebook page với ID {page_id} không tồn tại'
            }), 404
        
        if not facebook_page.status:
            return jsonify({
                'error': 'Facebook page không hoạt động',
                'message': 'Facebook page này đã bị tắt. Vui lòng bật lại để đăng bài.'
            }), 400
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Dữ liệu không được cung cấp'}), 400
        
        message = data.get('message')
        if not message:
            return jsonify({'error': 'Nội dung bài viết là bắt buộc'}), 400
        
        scheduled_time = data.get('scheduled_time')  # ISO format: "2024-01-01T10:00:00"
        if not scheduled_time:
            return jsonify({'error': 'Thời gian lên lịch là bắt buộc'}), 400
        
        link = data.get('link')
        image_url = data.get('image_url')
        
        # TODO: Implement scheduling logic
        # Có thể sử dụng Celery hoặc APScheduler để lên lịch
        # Hiện tại chỉ trả về thông tin lên lịch
        
        return jsonify({
            'success': True,
            'message': 'Đã lên lịch đăng bài thành công',
            'data': {
                'facebook_page_id': facebook_page.page_id,
                'facebook_page_name': facebook_page.page_name,
                'message': message,
                'scheduled_time': scheduled_time,
                'link': link,
                'image_url': image_url,
                'note': 'Tính năng lên lịch đang được phát triển'
            }
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Lỗi khi lên lịch đăng bài',
            'message': str(e)
        }), 500 