"""
Zalo Bot API Routes
Quản lý Zalo bots theo config_id
"""

import sys
import os
from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
import logging
import json
from models import db, ZaloConfig, ZaloSession, ZaloMessage
from services.zalo_bot_manager import zalo_bot_manager

# Add backend directory to Python path để import zlapi từ thư mục local
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

logger = logging.getLogger(__name__)

# Tạo blueprint
zalo_bot_bp = Blueprint('zalo_bot', __name__)

@zalo_bot_bp.route('/configs', methods=['GET'])
def get_configs():
    """API lấy danh sách tất cả configs"""
    try:
        configs = zalo_bot_manager.get_all_configs()
        return jsonify({
            'success': True,
            'configs': configs
        })
    except Exception as e:
        logger.error(f"Lỗi lấy danh sách configs: {e}")
        return jsonify({
            'success': False,
            'message': f'Lỗi: {str(e)}'
        }), 500

@zalo_bot_bp.route('/config/<int:config_id>', methods=['GET'])
def get_config_info(config_id):
    """API lấy thông tin config cụ thể"""
    try:
        config = zalo_bot_manager.get_config_by_id(config_id)
        if not config:
            return jsonify({
                'success': False,
                'message': 'Config không tồn tại'
            }), 404
        
        return jsonify({
            'success': True,
            'config': config
        })
    except Exception as e:
        logger.error(f"Lỗi lấy config {config_id}: {e}")
        return jsonify({
            'success': False,
            'message': f'Lỗi: {str(e)}'
        }), 500

@zalo_bot_bp.route('/start/<int:config_id>', methods=['POST'])
def start_bot(config_id):
    """API khởi động bot cho config_id cụ thể"""
    try:
        if zalo_bot_manager.start_bot(config_id):
            return jsonify({
                'success': True,
                'message': f'Bot config {config_id} đã khởi động thành công'
            })
        else:
            return jsonify({
                'success': False,
                'message': f'Không thể khởi động bot config {config_id}'
            }), 400
    except Exception as e:
        logger.error(f"Lỗi khởi động bot {config_id}: {e}")
        return jsonify({
            'success': False,
            'message': f'Lỗi: {str(e)}'
        }), 500

@zalo_bot_bp.route('/stop/<int:config_id>', methods=['POST'])
def stop_bot(config_id):
    """API dừng bot cho config_id cụ thể"""
    try:
        if zalo_bot_manager.stop_bot(config_id):
            return jsonify({
                'success': True,
                'message': f'Bot config {config_id} đã dừng thành công'
            })
        else:
            return jsonify({
                'success': False,
                'message': f'Không thể dừng bot config {config_id}'
            }), 400
    except Exception as e:
        logger.error(f"Lỗi dừng bot {config_id}: {e}")
        return jsonify({
            'success': False,
            'message': f'Lỗi: {str(e)}'
        }), 500

@zalo_bot_bp.route('/cleanup/<int:config_id>', methods=['POST'])
def cleanup_bot(config_id):
    """API cleanup hoàn toàn bot cho config_id cụ thể"""
    try:
        if zalo_bot_manager.cleanup_bot(config_id):
            return jsonify({
                'success': True,
                'message': f'Bot config {config_id} đã được cleanup hoàn toàn'
            })
        else:
            return jsonify({
                'success': False,
                'message': f'Không thể cleanup bot config {config_id}'
            }), 400
    except Exception as e:
        logger.error(f"Lỗi cleanup bot {config_id}: {e}")
        return jsonify({
            'success': False,
            'message': f'Lỗi: {str(e)}'
        }), 500

@zalo_bot_bp.route('/status/<int:config_id>', methods=['GET'])
def get_bot_status(config_id):
    """API lấy trạng thái bot cho config_id cụ thể"""
    try:
        status = zalo_bot_manager.get_bot_status(config_id)
        return jsonify({
            'success': True,
            'data': status
        })
    except Exception as e:
        logger.error(f"Lỗi lấy status bot {config_id}: {e}")
        return jsonify({
            'success': False,
            'message': f'Lỗi: {str(e)}'
        }), 500

@zalo_bot_bp.route('/messages/<int:config_id>', methods=['GET'])
def get_bot_messages(config_id):
    """API lấy tin nhắn gần đây cho config_id cụ thể"""
    try:
        messages = zalo_bot_manager.get_messages(config_id)
        return jsonify({
            'success': True,
            'messages': messages
        })
    except Exception as e:
        logger.error(f"Lỗi lấy messages bot {config_id}: {e}")
        return jsonify({
            'success': False,
            'message': f'Lỗi: {str(e)}'
        }), 500

@zalo_bot_bp.route('/start', methods=['POST'])
def start_all_bots():
    """API khởi động tất cả bots"""
    try:
        configs = zalo_bot_manager.get_all_configs()
        started_count = 0
        
        for config in configs:
            if zalo_bot_manager.start_bot(config['id']):
                started_count += 1
        
        return jsonify({
            'success': True,
            'message': f'Đã khởi động {started_count}/{len(configs)} bots',
            'started': started_count,
            'total': len(configs)
        })
    except Exception as e:
        logger.error(f"Lỗi khởi động tất cả bots: {e}")
        return jsonify({
            'success': False,
            'message': f'Lỗi: {str(e)}'
        }), 500

@zalo_bot_bp.route('/stop', methods=['POST'])
def stop_all_bots():
    """API dừng tất cả bots"""
    try:
        configs = zalo_bot_manager.get_all_configs()
        stopped_count = 0
        
        for config in configs:
            if zalo_bot_manager.stop_bot(config['id']):
                stopped_count += 1
        
        return jsonify({
            'success': True,
            'message': f'Đã dừng {stopped_count}/{len(configs)} bots',
            'stopped': stopped_count,
            'total': len(configs)
        })
    except Exception as e:
        logger.error(f"Lỗi dừng tất cả bots: {e}")
        return jsonify({
            'success': False,
            'message': f'Lỗi: {str(e)}'
        }), 500

@zalo_bot_bp.route('/status', methods=['GET'])
def get_all_status():
    """API lấy trạng thái tất cả bots"""
    try:
        configs = zalo_bot_manager.get_all_configs()
        all_status = {}
        
        for config in configs:
            all_status[config['id']] = zalo_bot_manager.get_bot_status(config['id'])
        
        return jsonify({
            'success': True,
            'data': all_status
        })
    except Exception as e:
        logger.error(f"Lỗi lấy status tất cả bots: {e}")
        return jsonify({
            'success': False,
            'message': f'Lỗi: {str(e)}'
        }), 500

@zalo_bot_bp.route('/send/<int:config_id>', methods=['POST'])
def send_message(config_id):
    """API gửi tin nhắn từ bot config_id"""
    try:
        # Lấy thông tin tin nhắn từ request
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'Không có dữ liệu tin nhắn'
            }), 400
        
        recipient_id = data.get('recipient_id')
        content = data.get('content')
        thread_type_str = data.get('thread_type', 'USER')  # USER hoặc GROUP
        
        if not recipient_id or not content:
            return jsonify({
                'success': False,
                'message': 'Thiếu recipient_id hoặc content'
            }), 400
        
        # Validate thread_type
        if thread_type_str not in ['USER', 'GROUP']:
            return jsonify({
                'success': False,
                'message': 'Thread type phải là USER hoặc GROUP'
            }), 400
        
        # Kiểm tra bot có đang chạy không
        if config_id not in zalo_bot_manager.running or not zalo_bot_manager.running[config_id]:
            return jsonify({
                'success': False,
                'message': f'Bot config {config_id} chưa chạy'
            }), 400
        
        # Lấy bot instance
        bot = zalo_bot_manager.bots.get(config_id)
        if not bot:
            return jsonify({
                'success': False,
                'message': f'Bot config {config_id} không tồn tại'
            }), 400
        
        try:
            # Import ThreadType và Message từ zlapi
            try:
                from zlapi.zlapi.models import ThreadType, Message
            except ImportError:
                from zlapi.models import ThreadType, Message
            
            # Tạo tin nhắn và gửi
            message_obj = Message(content)
            
            # Chuyển đổi thread_type string thành ThreadType enum
            if thread_type_str == 'USER':
                thread_type_enum = ThreadType.USER
            else:
                thread_type_enum = ThreadType.GROUP
            
            logger.info(f"Config {config_id}: Đang gửi tin nhắn đến {recipient_id} (thread_type: {thread_type_str})")
            
            # Gửi tin nhắn với ThreadType enum
            bot.send(message_obj, recipient_id, thread_type_enum)
            
            logger.info(f"Config {config_id}: Đã gửi tin nhắn thành công đến {recipient_id}")
            
            # Lưu tin nhắn đã gửi vào database
            try:
                with current_app.app_context():
                    config_info = zalo_bot_manager.get_config_by_id(config_id)
                    if not config_info:
                        logger.error(f"Config {config_id}: Không tìm thấy config")
                    else:
                        db_session = ZaloSession.query.filter_by(imei=config_info['imei']).first()
                        
                        if not db_session:
                            # Tạo session mới nếu không có
                            db_session = ZaloSession(
                                imei=config_info['imei'],
                                cookies=json.dumps(config_info['cookies']),
                                created_at=datetime.now(),
                                is_active=True
                            )
                            db.session.add(db_session)
                            db.session.commit()
                            db.session.refresh(db_session)
                        
                        # Lưu tin nhắn đã gửi
                        sent_msg = ZaloMessage(
                            session_id=db_session.id,
                            recipient_id=recipient_id,
                            recipient_name=f"User_{recipient_id}",
                            content=content,
                            media_url=None,
                            media_type=None,
                            status='sent',
                            sent_at=datetime.now(),
                            response_data=None
                        )
                        db.session.add(sent_msg)
                        db.session.commit()
                        
                        # Cập nhật stats
                        if config_id in zalo_bot_manager.stats:
                            zalo_bot_manager.stats[config_id]['messages_sent'] += 1
                        
                        logger.info(f"Config {config_id}: Đã lưu tin nhắn đã gửi vào database (session_id: {db_session.id})")
                        
            except Exception as e:
                logger.error(f"Config {config_id}: Lỗi lưu tin nhắn đã gửi: {e}")
                # Không fail nếu lưu database lỗi
            
            return jsonify({
                'success': True,
                'message': f'Đã gửi tin nhắn thành công đến {recipient_id}',
                'data': {
                    'config_id': config_id,
                    'recipient_id': recipient_id,
                    'content': content,
                    'thread_type': thread_type_str,
                    'sent_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            })
            
        except Exception as e:
            logger.error(f"Config {config_id}: Lỗi gửi tin nhắn: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return jsonify({
                'success': False,
                'message': f'Lỗi gửi tin nhắn: {str(e)}'
            }), 500
            
    except Exception as e:
        logger.error(f"Lỗi API gửi tin nhắn: {e}")
        return jsonify({
            'success': False,
            'message': f'Lỗi server: {str(e)}'
        }), 500

@zalo_bot_bp.route('/send_bulk/<int:config_id>', methods=['POST'])
def send_bulk_messages(config_id):
    """API gửi nhiều tin nhắn cùng lúc từ bot config_id"""
    try:
        # Lấy danh sách tin nhắn từ request
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'Không có dữ liệu tin nhắn'
            }), 400
        
        messages = data.get('messages', [])
        if not messages or not isinstance(messages, list):
            return jsonify({
                'success': False,
                'message': 'Thiếu danh sách tin nhắn'
            }), 400
        
        # Kiểm tra bot có đang chạy không
        if config_id not in zalo_bot_manager.running or not zalo_bot_manager.running[config_id]:
            return jsonify({
                'success': False,
                'message': f'Bot config {config_id} chưa chạy'
            }), 400
        
        # Lấy bot instance
        bot = zalo_bot_manager.bots.get(config_id)
        if not bot:
            return jsonify({
                'success': False,
                'message': f'Bot config {config_id} không tồn tại'
            }), 400
        
        results = []
        success_count = 0
        
        for msg_data in messages:
            recipient_id = msg_data.get('recipient_id')
            content = msg_data.get('content')
            thread_type = msg_data.get('thread_type', 'USER')
            
            if not recipient_id or not content:
                results.append({
                    'recipient_id': recipient_id,
                    'success': False,
                    'message': 'Thiếu recipient_id hoặc content'
                })
                continue
            
            try:
                # Import ThreadType và Message từ zlapi
                try:
                    from zlapi.zlapi.models import ThreadType, Message
                except ImportError:
                    from zlapi.models import ThreadType, Message
                
                # Gửi tin nhắn
                message_obj = Message(content)
                
                # Chuyển đổi thread_type string thành ThreadType enum
                if thread_type == 'USER':
                    thread_type_enum = ThreadType.USER
                else:
                    thread_type_enum = ThreadType.GROUP
                
                logger.info(f"Config {config_id}: Đang gửi tin nhắn đến {recipient_id} (thread_type: {thread_type})")
                
                # Gửi tin nhắn với ThreadType enum
                bot.send(message_obj, recipient_id, thread_type_enum)
                
                logger.info(f"Config {config_id}: Đã gửi tin nhắn thành công đến {recipient_id}")
                
                # Lưu tin nhắn đã gửi vào database
                try:
                    with current_app.app_context():
                        config_info = zalo_bot_manager.get_config_by_id(config_id)
                        if config_info:
                            db_session = ZaloSession.query.filter_by(imei=config_info['imei']).first()
                            
                            if not db_session:
                                # Tạo session mới nếu không có
                                db_session = ZaloSession(
                                    imei=config_info['imei'],
                                    cookies=json.dumps(config_info['cookies']),
                                    created_at=datetime.now(),
                                    is_active=True
                                )
                                db.session.add(db_session)
                                db.session.commit()
                                db.session.refresh(db_session)
                            
                            # Lưu tin nhắn đã gửi
                            sent_msg = ZaloMessage(
                                session_id=db_session.id,
                                recipient_id=recipient_id,
                                recipient_name=f"User_{recipient_id}",
                                content=content,
                                media_url=None,
                                media_type=None,
                                status='sent',
                                sent_at=datetime.now(),
                                response_data=None
                            )
                            db.session.add(sent_msg)
                            db.session.commit()
                            
                            # Cập nhật stats
                            if config_id in zalo_bot_manager.stats:
                                zalo_bot_manager.stats[config_id]['messages_sent'] += 1
                            
                            success_count += 1
                            results.append({
                                'recipient_id': recipient_id,
                                'success': True,
                                'message': 'Gửi thành công'
                            })
                        else:
                            results.append({
                                'recipient_id': recipient_id,
                                'success': False,
                                'message': 'Không tìm thấy config'
                            })
                            
                except Exception as e:
                    logger.error(f"Config {config_id}: Lỗi lưu tin nhắn đã gửi: {e}")
                    results.append({
                        'recipient_id': recipient_id,
                        'success': False,
                        'message': f'Lỗi lưu database: {str(e)}'
                    })
                
            except Exception as e:
                logger.error(f"Config {config_id}: Lỗi gửi tin nhắn đến {recipient_id}: {e}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
                results.append({
                    'recipient_id': recipient_id,
                    'success': False,
                    'message': f'Lỗi gửi: {str(e)}'
                })
        
        return jsonify({
            'success': True,
            'message': f'Đã xử lý {len(messages)} tin nhắn, thành công {success_count}',
            'total': len(messages),
            'success_count': success_count,
            'results': results
        })
        
    except Exception as e:
        logger.error(f"Lỗi API gửi bulk tin nhắn: {e}")
        return jsonify({
            'success': False,
            'message': f'Lỗi server: {str(e)}'
        }), 500

@zalo_bot_bp.route('/messages_sent/<int:config_id>', methods=['GET'])
def get_sent_messages(config_id):
    """API lấy danh sách tin nhắn đã gửi của config_id"""
    try:
        with current_app.app_context():
            config_info = zalo_bot_manager.get_config_by_id(config_id)
            if not config_info:
                return jsonify({
                    'success': False,
                    'message': 'Config không tồn tại'
                }), 404
            
            # Lấy tin nhắn đã gửi từ database
            sent_messages = ZaloMessage.query.filter(
                ZaloMessage.session_id.in_(
                    db.session.query(ZaloSession.id).filter(
                        ZaloSession.imei == config_info['imei']
                    )
                )
            ).order_by(ZaloMessage.sent_at.desc()).limit(50).all()
            
            messages_list = []
            for msg in sent_messages:
                messages_list.append({
                    'id': msg.id,
                    'recipient_id': msg.recipient_id,
                    'recipient_name': msg.recipient_name,
                    'content': msg.content,
                    'status': msg.status,
                    'sent_at': msg.sent_at.strftime('%Y-%m-%d %H:%M:%S') if msg.sent_at else None,
                    'media_url': msg.media_url,
                    'media_type': msg.media_type
                })
            
            return jsonify({
                'success': True,
                'config_id': config_id,
                'messages': messages_list,
                'total': len(messages_list)
            })
        
    except Exception as e:
        logger.error(f"Lỗi API lấy tin nhắn đã gửi: {e}")
        return jsonify({
            'success': False,
            'message': f'Lỗi server: {str(e)}'
        }), 500


