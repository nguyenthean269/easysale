"""
Zalo Bot Manager Service
Quản lý nhiều Zalo bot theo config_id
"""

import hashlib
import json
import logging
import threading
import time
import queue
import sys
import os
from datetime import datetime
from flask import Flask
from sqlalchemy.exc import IntegrityError
from models import db, ZaloConfig, ZaloSession, ZaloReceivedMessage, ZaloReceivedMessageExtraSender, ZaloMessage

# Helper function để lấy Flask app instance (tránh circular import)
def get_flask_app():
    """Lấy Flask app instance để dùng trong thread"""
    try:
        # Thử import app trực tiếp
        from app import app
        return app
    except ImportError:
        # Nếu không import được, thử cách khác
        try:
            import sys
            # Tìm app trong modules đã import
            for module_name, module in sys.modules.items():
                if hasattr(module, 'app') and isinstance(module.app, Flask):
                    return module.app
        except:
            pass
    return None

# Add backend directory to Python path để import zlapi từ thư mục local
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

logger = logging.getLogger(__name__)

# Import zlapi từ thư mục local
try:
    from zlapi import ZaloAPI
    from zlapi.zlapi.models import Message, ThreadType
except ImportError:
    try:
        from zlapi.zlapi import ZaloAPI
        from zlapi.zlapi.models import Message, ThreadType
    except ImportError:
        logger.error("Lỗi: Không thể import zlapi từ thư mục local. Kiểm tra đường dẫn: backend/zlapi")
        ZaloAPI = None
        Message = None
        ThreadType = None

# Global bot status tracking
bot_status = {}  # {config_id: status}

class ZaloBotManager:
    """Quản lý nhiều Zalo bot theo config_id"""
    
    def __init__(self):
        self.bots = {}  # {config_id: bot_instance}
        self.threads = {}  # {config_id: thread}
        self.running = {}  # {config_id: running}
        self.message_queues = {}  # {config_id: queue}
        self.stats = {}  # {config_id: stats}
    
    def get_all_configs(self):
        """Lấy danh sách tất cả configs từ database"""
        try:
            flask_app = get_flask_app()
            if not flask_app:
                logger.error("Không thể lấy Flask app instance")
                return []
            
            with flask_app.app_context():
                configs = ZaloConfig.query.all()
                config_list = []
                
                for config in configs:
                    config_info = {
                        'id': config.id,
                        'name': config.name,
                        'imei': config.imei,
                        'is_default': config.is_default,
                        'created_at': config.created_at.strftime('%Y-%m-%d %H:%M:%S') if config.created_at else None,
                        'status': bot_status.get(config.id, 'stopped'),
                        'running': config.id in self.running and self.running[config.id]
                    }
                    config_list.append(config_info)
                
                return config_list
                
        except Exception as e:
            logger.error(f"Lỗi lấy danh sách configs: {e}")
            return []
    
    def get_config_by_id(self, config_id):
        """Lấy config theo ID"""
        try:
            flask_app = get_flask_app()
            if not flask_app:
                logger.error(f"Không thể lấy Flask app instance")
                return None
            
            with flask_app.app_context():
                config = ZaloConfig.query.filter_by(id=config_id).first()
                
                if config:
                    # Parse cookies từ JSON string
                    try:
                        cookies = json.loads(config.cookies) if config.cookies else {}
                    except json.JSONDecodeError:
                        cookies = {}
                    
                    config_data = {
                        'id': config.id,
                        'name': config.name,
                        'imei': config.imei,
                        'cookies': cookies,
                        'is_default': config.is_default
                    }
                    
                    return config_data
                else:
                    return None
                    
        except Exception as e:
            logger.error(f"Lỗi lấy config {config_id}: {e}")
            return None
    
    def save_message_to_db(self, config_id, sender_id, sender_name, content, thread_id, thread_type):
        """Lưu tin nhắn nhận được vào database"""
        try:
            # Validation - Đảm bảo sender_name không bao giờ NULL
            if not sender_name or sender_name.strip() == "":
                sender_name = f"User_{sender_id}"
                logger.warning(f"Config {config_id}: Sender name rỗng, reset về: {sender_name}")
            
            # Validation - Đảm bảo sender_id không rỗng
            if not sender_id or str(sender_id).strip() == "":
                logger.error(f"Config {config_id}: Sender ID rỗng, không thể lưu tin nhắn")
                return
            
            # Validation - Đảm bảo content không rỗng
            if not content or str(content).strip() == "":
                logger.error(f"Config {config_id}: Content rỗng, không thể lưu tin nhắn")
                return
            
            logger.info(f"Config {config_id}: Bắt đầu lưu tin nhắn với sender_name='{sender_name}', sender_id='{sender_id}'")
            
            # Sử dụng app instance trực tiếp thay vì current_app vì được gọi từ thread
            flask_app = get_flask_app()
            if not flask_app:
                logger.error(f"Config {config_id}: Không thể lấy Flask app instance")
                return
            
            with flask_app.app_context():
                # Lấy config trực tiếp trong context này để tránh tạo context lồng nhau
                config = ZaloConfig.query.filter_by(id=config_id).first()
                if not config:
                    logger.error(f"Config {config_id}: Không tìm thấy config")
                    return
                
                # Parse cookies từ JSON string
                try:
                    cookies_dict = json.loads(config.cookies) if config.cookies else {}
                except json.JSONDecodeError:
                    cookies_dict = {}
                
                config_info = {
                    'id': config.id,
                    'name': config.name,
                    'imei': config.imei,
                    'cookies': cookies_dict,
                    'is_default': config.is_default
                }
                
                db_session = ZaloSession.query.filter_by(imei=config_info['imei']).first()
                
                if not db_session:
                    # Tạo session mới nếu không có
                    logger.info(f"Config {config_id}: Tạo session mới cho IMEI {config_info['imei']}")
                    db_session = ZaloSession(
                        imei=config_info['imei'],
                        cookies=json.dumps(config_info['cookies']),
                        created_at=datetime.now(),
                        is_active=True
                    )
                    db.session.add(db_session)
                    db.session.commit()
                    db.session.refresh(db_session)
                    logger.info(f"Config {config_id}: Đã tạo session {db_session.id}")
                else:
                    logger.info(f"Config {config_id}: Sử dụng session hiện có {db_session.id}")
                
                # Hash content giống MySQL SHA(content) để kiểm tra trùng
                content_hash = hashlib.sha1(str(content).encode('utf-8')).hexdigest()
                existing = ZaloReceivedMessage.query.filter_by(content_hash=content_hash).first()
                
                if existing:
                    # Tin nhắn trùng content: chỉ lưu sender vào bảng extra_senders
                    try:
                        extra = ZaloReceivedMessageExtraSender(
                            message_id=existing.id,
                            sender_id=str(sender_id),
                            sender_name=str(sender_name),
                            session_id=db_session.id,
                            config_id=config_id,
                            received_at=datetime.now()
                        )
                        db.session.add(extra)
                        db.session.commit()
                        logger.info(f"Config {config_id}: Tin nhắn trùng content_hash, đã lưu sender {sender_name} vào extra_senders (message_id={existing.id})")
                    except IntegrityError:
                        db.session.rollback()
                        logger.info(f"Config {config_id}: Sender {sender_id} đã tồn tại cho message_id={existing.id}, bỏ qua")
                else:
                    # Tin nhắn mới: insert vào zalo_received_messages
                    received_msg = ZaloReceivedMessage(
                        session_id=db_session.id,
                        config_id=config_id,
                        sender_id=str(sender_id),
                        sender_name=str(sender_name),
                        content=str(content),
                        thread_id=str(thread_id) if thread_id else None,
                        thread_type=str(thread_type) if thread_type else None,
                        received_at=datetime.now(),
                        status_push_kafka=0
                    )
                    db.session.add(received_msg)
                    db.session.commit()
                    logger.info(f"Config {config_id}: Đã lưu tin nhắn từ {sender_name} vào database (session_id: {db_session.id})")
                    received_msg.status_push_kafka = 1
                    db.session.commit()
                
                # Cập nhật stats cho config này
                if config_id not in self.stats:
                    self.stats[config_id] = {
                        'start_time': None,
                        'messages_received': 0,
                        'messages_sent': 0,
                        'last_message_time': None
                    }
                
                self.stats[config_id]['messages_received'] += 1
                self.stats[config_id]['last_message_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                # Thêm vào message queue của config này
                if config_id not in self.message_queues:
                    self.message_queues[config_id] = queue.Queue()
                
                self.message_queues[config_id].put({
                    'type': 'received',
                    'sender': sender_name,
                    'content': content,
                    'time': datetime.now().strftime('%H:%M:%S')
                })
            
        except Exception as e:
            logger.error(f"Lỗi lưu tin nhắn cho config {config_id}: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            try:
                # Thử rollback nếu có app context
                flask_app = get_flask_app()
                if flask_app:
                    with flask_app.app_context():
                        db.session.rollback()
            except:
                pass
    
    def create_bot(self, config_id):
        """Tạo bot instance cho config_id cụ thể"""
        if not ZaloAPI:
            logger.error("ZaloAPI không khả dụng. Hãy cài đặt zlapi.")
            return False
            
        config = self.get_config_by_id(config_id)
        if not config:
            logger.error(f"Không thể lấy config {config_id}")
            return False
        
        # Kiểm tra xem bot đã tồn tại chưa, nếu có thì dừng trước
        if config_id in self.bots and self.bots[config_id]:
            logger.info(f"Config {config_id}: Bot đã tồn tại, đang dừng bot cũ...")
            try:
                self.bots[config_id].stopListening()
            except:
                pass
            self.bots[config_id] = None
        
        try:
            # Tạo custom bot class - giống hệt như trong zalohandler
            class CustomBot(ZaloAPI):
                def __init__(self, phone, password, imei, cookies, config_id, manager):
                    # Sử dụng session_cookies theo documentation - giống hệt zalohandler
                    # ZaloAPI sẽ tự động kiểm tra session_cookies, nếu hợp lệ thì không login bằng phone/password
                    # Nếu cookies không hợp lệ, ZaloAPI sẽ thử login bằng phone/password (nhưng dummy nên sẽ fail)
                    try:
                        super().__init__(phone, password, imei=imei, session_cookies=cookies)
                        logger.info(f"✅ Config {config_id}: Khởi tạo thành công với session_cookies")
                    except Exception as e:
                        # Nếu cookies không hợp lệ, ZaloAPI đã thử login bằng phone/password và fail
                        # Không cần làm gì thêm, chỉ log và raise exception
                        error_msg = str(e)
                        if "ZaloLoginError" in error_msg or "logging in" in error_msg:
                            logger.error(f"❌ Config {config_id}: Cookies không hợp lệ hoặc đã hết hạn. API getLoginInfo trả về lỗi.")
                            logger.error(f"❌ Config {config_id}: Chi tiết lỗi: {error_msg}")
                            raise Exception(f"Cookies không hợp lệ hoặc đã hết hạn. Vui lòng cập nhật cookies mới. Lỗi: {error_msg}")
                        else:
                            # Lỗi khác, raise lại
                            logger.error(f"❌ Config {config_id}: Lỗi không xác định khi khởi tạo bot: {error_msg}")
                            raise
                    
                    # Set _imei thủ công vì session_cookies có thể không set nó
                    if not hasattr(self, '_imei') or not self._imei:
                        self._imei = imei
                        logger.info(f"✅ Config {config_id}: Đã set _imei thủ công: {imei}")
                    
                    self.config_id = config_id
                    self.manager = manager
                
                def onListening(self):
                    logger.info(f"Config {self.config_id}: Bot đang lắng nghe tin nhắn...")
                    
                    # Cập nhật stats
                    if self.config_id not in self.manager.stats:
                        self.manager.stats[self.config_id] = {
                            'start_time': None,
                            'messages_received': 0,
                            'messages_sent': 0,
                            'last_message_time': None
                        }
                    
                    self.manager.stats[self.config_id]['start_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    bot_status[self.config_id] = 'listening'
                
                def onMessage(self, mid, author_id, message, message_object, thread_id, thread_type):
                    try:
                        if not isinstance(message, str):
                            return
                        
                        # Lấy thông tin người gửi - Đảm bảo sender_name không bao giờ NULL
                        sender_name = f"User_{author_id}"  # Giá trị mặc định
                        logger.info(f"Config {self.config_id}: Bắt đầu xử lý tin nhắn từ {author_id}")
                        
                        try:
                            logger.info(f"Config {self.config_id}: Đang fetch thông tin user {author_id}")
                            user_info = self.fetchUserInfo(author_id)
                            logger.info(f"Config {self.config_id}: User info result: {user_info}")
                            
                            # Debug user_info structure
                            if user_info:
                                logger.info(f"Config {self.config_id}: User info type: {type(user_info)}")
                                logger.info(f"Config {self.config_id}: User info dict: {user_info.__dict__ if hasattr(user_info, '__dict__') else 'No __dict__'}")
                            
                            # Lấy zaloName từ changed_profiles
                            if user_info and hasattr(user_info, 'changed_profiles') and user_info.changed_profiles:
                                user_id_str = str(author_id)
                                if user_id_str in user_info.changed_profiles:
                                    profile = user_info.changed_profiles[user_id_str]
                                    if 'zaloName' in profile and profile['zaloName']:
                                        sender_name = profile['zaloName']
                                        logger.info(f"Config {self.config_id}: Lấy được zaloName: {sender_name}")
                                    elif 'displayName' in profile and profile['displayName']:
                                        sender_name = profile['displayName']
                                        logger.info(f"Config {self.config_id}: Lấy được displayName: {sender_name}")
                                    else:
                                        logger.info(f"Config {self.config_id}: Không có zaloName/displayName trong profile, sử dụng mặc định: {sender_name}")
                                else:
                                    logger.info(f"Config {self.config_id}: User ID {user_id_str} không có trong changed_profiles, sử dụng mặc định: {sender_name}")
                            else:
                                logger.info(f"Config {self.config_id}: Không có changed_profiles, sử dụng mặc định: {sender_name}")
                        except Exception as e:
                            logger.warning(f"Config {self.config_id}: Lỗi fetch user info: {e}, sử dụng tên mặc định: {sender_name}")
                        
                        # Đảm bảo sender_name không rỗng
                        if not sender_name or sender_name.strip() == "":
                            sender_name = f"User_{author_id}"
                            logger.warning(f"Config {self.config_id}: Sender name rỗng, reset về: {sender_name}")
                        
                        logger.info(f"Config {self.config_id}: Tin nhắn từ {sender_name} ({author_id}): {message}")
                        
                        # Lưu tin nhắn vào database
                        try:
                            logger.info(f"Config {self.config_id}: Bắt đầu lưu tin nhắn vào database")
                            logger.info(f"Config {self.config_id}: sender_name = '{sender_name}', sender_id = '{author_id}'")
                            
                            self.manager.save_message_to_db(
                                self.config_id, author_id, sender_name, 
                                message, thread_id, str(thread_type)
                            )
                            logger.info(f"Config {self.config_id}: Đã lưu tin nhắn vào database thành công")
                        except Exception as e:
                            logger.error(f"Config {self.config_id}: Lỗi lưu tin nhắn vào database: {e}")
                            import traceback
                            logger.error(f"Traceback: {traceback.format_exc()}")
                        
                    except Exception as e:
                        logger.error(f"Config {self.config_id}: Lỗi xử lý tin nhắn: {e}")
                        import traceback
                        logger.error(f"Traceback: {traceback.format_exc()}")
                
                def onEvent(self, event_data, event_type):
                    logger.info(f"Config {self.config_id}: Sự kiện: {event_type} - {event_data}")
            
            # Khởi tạo bot - Sử dụng dummy phone/password và session_cookies như trong zalohandler
            logger.info(f"Khởi tạo CustomBot cho config {config_id}...")
            logger.info(f"Config {config_id}: IMEI: {config['imei']}")
            logger.info(f"Config {config_id}: Cookies type: {type(config['cookies'])}")
            logger.info(f"Config {config_id}: Cookies keys: {list(config['cookies'].keys()) if isinstance(config['cookies'], dict) else 'Not a dict'}")
            
            # In ra cookies để debug
            if isinstance(config['cookies'], dict):
                logger.info(f"Config {config_id}: Cookies content (full): {json.dumps(config['cookies'], indent=2, ensure_ascii=False)}")
                logger.info(f"Config {config_id}: Cookies count: {len(config['cookies'])}")
                # Kiểm tra các cookies quan trọng
                important_cookies = ['zpsid', 'zpw_sek', '_zlang', 'app.event.zalo.me']
                for key in important_cookies:
                    if key in config['cookies']:
                        value = config['cookies'][key]
                        logger.info(f"Config {config_id}: Cookie '{key}': {value[:50]}..." if len(str(value)) > 50 else f"Config {config_id}: Cookie '{key}': {value}")
                    else:
                        logger.warning(f"Config {config_id}: Missing important cookie: {key}")
            else:
                logger.warning(f"Config {config_id}: Cookies không phải dict: {config['cookies']}")
                logger.warning(f"Config {config_id}: Cookies type: {type(config['cookies'])}, value: {config['cookies']}")
            
            bot = CustomBot(
                phone="dummy_phone",  # Truyền giá trị dummy - không dùng để login nếu cookies hợp lệ
                password="dummy_password",  # Truyền giá trị dummy - không dùng để login nếu cookies hợp lệ
                imei=config['imei'],
                cookies=config['cookies'],  # Cookies từ database để authenticate
                config_id=config_id,
                manager=self
            )
            
            self.bots[config_id] = bot
            logger.info(f"✅ Bot config {config_id} đã khởi tạo thành công")
            return True
            
        except Exception as e:
            logger.error(f"Lỗi khởi tạo bot config {config_id}: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return False
    
    def start_bot(self, config_id):
        """Khởi động bot cho config_id cụ thể"""
        if config_id in self.running and self.running[config_id]:
            logger.warning(f"Bot config {config_id} đã đang chạy")
            return False
        
        if config_id not in self.bots:
            if not self.create_bot(config_id):
                return False
        
        def run_bot():
            try:
                logger.info(f"Bắt đầu lắng nghe tin nhắn cho config {config_id}...")
                bot_status[config_id] = 'starting'
                self.running[config_id] = True
                self.bots[config_id].listen()
            except Exception as e:
                logger.error(f"Lỗi khi chạy bot config {config_id}: {e}")
                bot_status[config_id] = 'error'
                self.running[config_id] = False
        
        self.threads[config_id] = threading.Thread(target=run_bot, daemon=True)
        self.threads[config_id].start()
        
        logger.info(f"✅ Bot config {config_id} đã khởi động thành công")
        return True
    
    def stop_bot(self, config_id):
        """Dừng bot cho config_id cụ thể"""
        stop_start_time = datetime.now()
        logger.info(f"🛑 [STOP_BOT] Config {config_id}: Bắt đầu quá trình dừng bot - {stop_start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        if config_id not in self.running or not self.running[config_id]:
            logger.warning(f"⚠️ [STOP_BOT] Config {config_id}: Bot chưa chạy hoặc không tồn tại trong running list")
            return False
        
        try:
            # Đặt flag dừng trước
            logger.info(f"🔄 [STOP_BOT] Config {config_id}: Đặt running flag = False")
            self.running[config_id] = False
            bot_status[config_id] = 'stopping'
            
            # Đóng kết nối WebSocket nếu bot tồn tại
            if config_id in self.bots and self.bots[config_id]:
                try:
                    logger.info(f"🔌 [STOP_BOT] Config {config_id}: Bắt đầu đóng kết nối WebSocket...")
                    self.bots[config_id].stopListening()
                    logger.info(f"✅ [STOP_BOT] Config {config_id}: Đã gọi stopListening() thành công")
                    
                    # Đợi một chút để WebSocket đóng hoàn toàn
                    time.sleep(0.5)
                    
                except Exception as e:
                    logger.error(f"❌ [STOP_BOT] Config {config_id}: Lỗi khi đóng WebSocket: {e}")
            
            # Đợi thread kết thúc với timeout
            if config_id in self.threads and self.threads[config_id].is_alive():
                logger.info(f"🧵 [STOP_BOT] Config {config_id}: Thread đang chạy, bắt đầu đợi kết thúc...")
                self.threads[config_id].join(timeout=3)
                
                if self.threads[config_id].is_alive():
                    logger.warning(f"⚠️ [STOP_BOT] Config {config_id}: Thread vẫn chạy sau timeout")
            
            # Cleanup bot instance
            if config_id in self.bots:
                self.bots[config_id] = None
            
            bot_status[config_id] = 'stopped'
            stop_end_time = datetime.now()
            stop_duration = (stop_end_time - stop_start_time).total_seconds()
            
            logger.info(f"✅ [STOP_BOT] Config {config_id}: Bot đã dừng hoàn toàn trong {stop_duration:.2f}s")
            return True
            
        except Exception as e:
            logger.error(f"❌ [STOP_BOT] Config {config_id}: Lỗi khi dừng bot: {e}")
            bot_status[config_id] = 'error'
            return False
    
    def cleanup_bot(self, config_id):
        """Cleanup hoàn toàn bot instance"""
        cleanup_start_time = datetime.now()
        logger.info(f"🧹 [CLEANUP_BOT] Config {config_id}: Bắt đầu cleanup hoàn toàn")
        
        try:
            # Dừng bot nếu đang chạy
            if config_id in self.running and self.running[config_id]:
                logger.info(f"🛑 [CLEANUP_BOT] Config {config_id}: Bot đang chạy, bắt đầu dừng...")
                self.stop_bot(config_id)
            
            # Xóa bot instance
            if config_id in self.bots:
                self.bots[config_id] = None
                del self.bots[config_id]
            
            # Xóa thread
            if config_id in self.threads:
                del self.threads[config_id]
            
            # Xóa stats
            if config_id in self.stats:
                del self.stats[config_id]
            
            # Xóa message queue
            if config_id in self.message_queues:
                del self.message_queues[config_id]
            
            # Reset status
            if config_id in bot_status:
                bot_status[config_id] = 'stopped'
            
            cleanup_end_time = datetime.now()
            cleanup_duration = (cleanup_end_time - cleanup_start_time).total_seconds()
            
            logger.info(f"✅ [CLEANUP_BOT] Config {config_id}: Cleanup hoàn toàn thành công trong {cleanup_duration:.2f}s")
            return True
            
        except Exception as e:
            logger.error(f"❌ [CLEANUP_BOT] Config {config_id}: Lỗi cleanup: {e}")
            return False
    
    def get_bot_status(self, config_id):
        """Lấy trạng thái bot cho config_id cụ thể"""
        if config_id not in self.stats:
            self.stats[config_id] = {
                'start_time': None,
                'messages_received': 0,
                'messages_sent': 0,
                'last_message_time': None
            }
        
        return {
            'config_id': config_id,
            'running': config_id in self.running and self.running[config_id],
            'status': bot_status.get(config_id, 'stopped'),
            'stats': self.stats[config_id]
        }
    
    def get_messages(self, config_id):
        """Lấy tin nhắn gần đây cho config_id cụ thể"""
        if config_id not in self.message_queues:
            return []
        
        messages = []
        while not self.message_queues[config_id].empty():
            try:
                messages.append(self.message_queues[config_id].get_nowait())
            except queue.Empty:
                break
        
        return messages

# Khởi tạo singleton instance
zalo_bot_manager = ZaloBotManager()

