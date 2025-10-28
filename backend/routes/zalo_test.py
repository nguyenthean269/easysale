"""
Zalo Message Processor Test API Routes
"""

from flask import Blueprint, request, jsonify
from services.zalo_message_processor import zalo_processor
import logging

logger = logging.getLogger(__name__)

# Tạo blueprint
zalo_test_bp = Blueprint('zalo_test', __name__)

@zalo_test_bp.route('/process-message', methods=['POST'])
def test_process_message():
    """Test xử lý một tin nhắn cụ thể"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided'
            }), 400
        
        message_id = data.get('message_id')
        message_content = data.get('message_content')
        
        if not message_id and not message_content:
            return jsonify({
                'success': False,
                'error': 'Either message_id or message_content is required'
            }), 400
        
        # Nếu có message_id, lấy tin nhắn từ database
        if message_id:
            logger.info(f"Testing message processing for ID: {message_id}")
            result, error = zalo_processor.run_test_one_mode(message_id)
            
            if error:
                return jsonify({
                    'success': False,
                    'error': error
                }), 500
            
            return jsonify({
                'success': True,
                'data': result,
                'message': f'Successfully processed message ID: {message_id}'
            })
        
        # Nếu có message_content, xử lý trực tiếp
        elif message_content:
            logger.info(f"Testing message processing for content: {message_content[:100]}...")
            
            # Gửi tới Groq để bóc tách thông tin
            groq_result = zalo_processor.process_message_with_groq(message_content)
            
            if not groq_result:
                return jsonify({
                    'success': False,
                    'error': 'Failed to process message with Groq'
                }), 500
            
            # Parse JSON từ Groq response
            apartment_data = zalo_processor.parse_groq_response(groq_result)
            
            if not apartment_data:
                return jsonify({
                    'success': False,
                    'error': 'Failed to parse Groq response',
                    'raw_response': groq_result
                }), 500
            
            return jsonify({
                'success': True,
                'data': {
                    'groq_response': groq_result,
                    'parsed_data': apartment_data
                },
                'message': 'Successfully processed message content'
            })
        
    except Exception as e:
        logger.error(f"Error in test_process_message: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@zalo_test_bp.route('/unprocessed-messages', methods=['GET'])
def get_unprocessed_messages():
    """Lấy danh sách tin nhắn chưa xử lý"""
    try:
        limit = request.args.get('limit', 20, type=int)
        
        messages = zalo_processor.get_unprocessed_messages(limit=limit)
        
        return jsonify({
            'success': True,
            'data': messages,
            'count': len(messages)
        })
        
    except Exception as e:
        logger.error(f"Error in get_unprocessed_messages: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@zalo_test_bp.route('/processor-status', methods=['GET'])
def get_processor_status():
    """Lấy trạng thái của Zalo Message Processor"""
    try:
        status = zalo_processor.get_status()
        
        return jsonify({
            'success': True,
            'data': status
        })
        
    except Exception as e:
        logger.error(f"Error in get_processor_status: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@zalo_test_bp.route('/property-tree', methods=['GET'])
def get_property_tree():
    """Lấy property tree cho prompt"""
    try:
        root_id = request.args.get('root_id', 1, type=int)
        
        property_tree = zalo_processor.get_property_tree_for_prompt(root_id)
        
        return jsonify({
            'success': True,
            'data': {
                'root_id': root_id,
                'property_tree': property_tree
            }
        })
        
    except Exception as e:
        logger.error(f"Error in get_property_tree: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@zalo_test_bp.route('/batch-process', methods=['POST'])
def batch_process_messages():
    """Xử lý batch tin nhắn"""
    try:
        data = request.get_json() or {}
        limit = data.get('limit', 20)
        
        logger.info(f"Starting batch processing with limit: {limit}")
        
        processed_count, error_count = zalo_processor.process_messages_batch(limit=limit)
        
        return jsonify({
            'success': True,
            'data': {
                'processed_count': processed_count,
                'error_count': error_count,
                'total_processed': processed_count + error_count
            },
            'message': f'Batch processing completed: {processed_count} processed, {error_count} errors'
        })
        
    except Exception as e:
        logger.error(f"Error in batch_process_messages: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
