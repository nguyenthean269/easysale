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
    """Test xử lý batch tin nhắn (chỉ hỗ trợ message_ids array)"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided'
            }), 400
        
        message_ids = data.get('message_ids')  # Array of message IDs (required)
        message_content = data.get('message_content')  # Optional: for testing content directly
        
        # Nếu có message_ids array, xử lý batch messages
        if message_ids:
            if not isinstance(message_ids, list) or len(message_ids) == 0:
                return jsonify({
                    'success': False,
                    'error': 'message_ids must be a non-empty array'
                }), 400
            
            logger.info(f"Processing batch messages for IDs: {message_ids}")
            result, error = zalo_processor.run_test_batch_mode(message_ids)
            
            if error:
                return jsonify({
                    'success': False,
                    'error': error
                }), 500
            
            return jsonify({
                'success': True,
                'data': result,
                'message': f'Successfully processed {len(message_ids)} messages'
            })
        
        # Nếu có message_content, xử lý trực tiếp (chỉ để test content)
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
        
        else:
            return jsonify({
                'success': False,
                'error': 'Either message_ids array or message_content is required'
            }), 400
        
    except Exception as e:
        logger.error(f"Error in test_process_message: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@zalo_test_bp.route('/messages', methods=['GET'])
def get_messages():
    """Lấy danh sách messages unique theo content_hash với pagination và filter warehouse_id"""
    try:
        limit = request.args.get('limit', 20, type=int)
        offset = request.args.get('offset', 0, type=int)
        warehouse_id = request.args.get('warehouse_id', 'NULL', type=str)
        sort = request.args.get('sort', 'newest', type=str)
        
        # Validate sort parameter
        if sort not in ('newest', 'oldest'):
            return jsonify({
                'success': False,
                'error': "Invalid sort. Must be 'newest' or 'oldest'"
            }), 400
        
        # Validate warehouse_id parameter
        valid_warehouse_ids = ['NULL', 'NOT_NULL', 'ALL']
        if warehouse_id not in valid_warehouse_ids and not warehouse_id.isdigit():
            return jsonify({
                'success': False,
                'error': f'Invalid warehouse_id. Must be one of: {valid_warehouse_ids} or a specific ID number'
            }), 400
        
        # Validate pagination parameters
        if limit <= 0 or limit > 1000:
            return jsonify({
                'success': False,
                'error': 'limit must be between 1 and 1000'
            }), 400
        
        if offset < 0:
            return jsonify({
                'success': False,
                'error': 'offset must be >= 0'
            }), 400
        
        result = zalo_processor.get_unprocessed_messages(limit=limit, offset=offset, warehouse_id=warehouse_id, sort=sort)
        
        # result is now a dict with 'messages' and 'total'
        messages = result.get('messages', [])
        total_count = result.get('total', 0)
        
        return jsonify({
            'success': True,
            'data': messages,
            'count': len(messages),
            'total': total_count,
            'limit': limit,
            'offset': offset,
            'warehouse_id_filter': warehouse_id,
            'sort': sort
        })
        
    except Exception as e:
        logger.error(f"Error in get_messages: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@zalo_test_bp.route('/unprocessed-messages', methods=['GET'])
def get_unprocessed_messages_deprecated():
    """
    DEPRECATED: Sử dụng /messages thay thế
    Route này được giữ lại để backward compatibility
    """
    return get_messages()

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

@zalo_test_bp.route('/schedule/start', methods=['POST'])
def start_schedule():
    """
    Bắt đầu schedule
    Body (optional): {"interval_minutes": 10} - Interval tính bằng phút
    """
    try:
        if zalo_processor.is_running:
            return jsonify({
                'success': False,
                'error': 'Schedule is already running'
            }), 400
        
        # Lấy interval từ request body (optional)
        data = request.get_json() or {}
        interval_minutes = data.get('interval_minutes')
        
        # Validate interval nếu có
        if interval_minutes is not None:
            if not isinstance(interval_minutes, int) or interval_minutes <= 0:
                return jsonify({
                    'success': False,
                    'error': 'interval_minutes must be a positive integer'
                }), 400
            if interval_minutes > 1440:  # Max 24 hours
                return jsonify({
                    'success': False,
                    'error': 'interval_minutes must be <= 1440 (24 hours)'
                }), 400
        
        # Start schedule (có thể với interval tùy chỉnh)
        # Cho phép start ngay cả khi schedule_enabled=False (ZALO_MESSAGE_PROCESSOR_SCHEDULE=0)
        zalo_processor.start(interval_minutes=interval_minutes)
        
        status = zalo_processor.get_status()
        
        return jsonify({
            'success': True,
            'data': status,
            'message': f'Schedule started successfully with interval: {status["interval_minutes"]} minutes'
        })
        
    except Exception as e:
        logger.error(f"Error in start_schedule: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@zalo_test_bp.route('/schedule/stop', methods=['POST'])
def stop_schedule():
    """Dừng schedule"""
    try:
        if not zalo_processor.is_running:
            return jsonify({
                'success': False,
                'error': 'Schedule is not running'
            }), 400
        
        zalo_processor.stop()
        
        status = zalo_processor.get_status()
        
        return jsonify({
            'success': True,
            'data': status,
            'message': 'Schedule stopped successfully'
        })
        
    except Exception as e:
        logger.error(f"Error in stop_schedule: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
