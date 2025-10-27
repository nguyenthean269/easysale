from flask import Flask, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from models import db
from config import get_config, validate_config
from services.zalo_message_processor import zalo_processor

# Khởi tạo app
app = Flask(__name__)

# Load configuration
app.config.from_object(get_config())

# Validate configuration
if not validate_config():
    print("⚠️  Configuration validation failed. Please check your .env file.")

# CORS
CORS(app)

# Khởi tạo các extension
jwt = JWTManager(app)

# Cấu hình JWT
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = app.config.get('JWT_ACCESS_TOKEN_EXPIRES', 3600)  # 1 hour
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = app.config.get('JWT_REFRESH_TOKEN_EXPIRES', 604800)  # 7 days

db.init_app(app)
migrate = Migrate(app, db)

# Khởi tạo rate limiter
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri=app.config.get('RATE_LIMIT_STORAGE_URI', 'memory://')
)

# Đảm bảo db và limiter có thể truy cập qua current_app
app.db = db
app.limiter = limiter

# Import và đăng ký blueprint
from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.user import user_bp
from routes.facebook import facebook_bp
from routes.content import content_bp
from routes.posts import posts_bp
from routes.zalo_chunks import zalo_chunks_bp

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(user_bp, url_prefix='/user')
app.register_blueprint(facebook_bp, url_prefix='/facebook')
app.register_blueprint(content_bp, url_prefix='/content')
app.register_blueprint(posts_bp, url_prefix='/posts')
app.register_blueprint(zalo_chunks_bp, url_prefix='/zalo-chunks')

# API endpoints cho Zalo Message Processor
@app.route('/api/zalo-processor/status', methods=['GET'])
def zalo_processor_status():
    """Lấy trạng thái của Zalo Message Processor"""
    try:
        status = zalo_processor.get_status()
        return {
            'success': True,
            'data': status
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }, 500

@app.route('/api/zalo-processor/start', methods=['POST'])
def zalo_processor_start():
    """Khởi động Zalo Message Processor"""
    try:
        zalo_processor.start()
        return {
            'success': True,
            'message': 'Zalo Message Processor started successfully'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }, 500

@app.route('/api/zalo-processor/stop', methods=['POST'])
def zalo_processor_stop():
    """Dừng Zalo Message Processor"""
    try:
        zalo_processor.stop()
        return {
            'success': True,
            'message': 'Zalo Message Processor stopped successfully'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }, 500

# Error handler cho JWT
@jwt.invalid_token_loader
def invalid_token_callback(error_string):
    return {
        'error': 'Invalid token',
        'message': 'Token không hợp lệ hoặc đã hết hạn. Vui lòng đăng nhập lại.',
        'details': error_string
    }, 401

@jwt.unauthorized_loader
def missing_token_callback(error_string):
    return {
        'error': 'Missing token',
        'message': 'Token không được cung cấp. Vui lòng đăng nhập để lấy token.',
        'details': error_string
    }, 401

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return {
        'error': 'Expired token',
        'message': 'Token đã hết hạn. Vui lòng đăng nhập lại.',
        'expired_at': jwt_payload.get('exp')
    }, 401

# Error handler cho rate limiting
@app.errorhandler(429)
def ratelimit_handler(e):
    # Lấy thông tin retry_after từ exception
    retry_after = None
    if hasattr(e, 'retry_after') and e.retry_after:
        retry_after = int(e.retry_after)
    elif hasattr(e, 'reset_time'):
        import time
        retry_after = int(e.reset_time - time.time())
    
    # Tạo message dựa trên retry_after
    if retry_after and retry_after > 0:
        if retry_after < 60:
            message = f'Bạn đã vượt quá giới hạn request. Vui lòng thử lại sau {retry_after} giây.'
        elif retry_after < 3600:
            minutes = retry_after // 60
            message = f'Bạn đã vượt quá giới hạn request. Vui lòng thử lại sau {minutes} phút.'
        else:
            hours = retry_after // 3600
            message = f'Bạn đã vượt quá giới hạn request. Vui lòng thử lại sau {hours} giờ.'
    else:
        message = 'Bạn đã vượt quá giới hạn request. Vui lòng thử lại sau.'
    
    # Đảm bảo tất cả giá trị đều có thể serialize
    limit_value = getattr(e, 'limit', 'Unknown')
    if callable(limit_value):
        limit_value = str(limit_value)
    
    remaining_value = getattr(e, 'remaining', 0)
    if callable(remaining_value):
        remaining_value = 0
    
    reset_time_value = getattr(e, 'reset_time', None)
    if callable(reset_time_value):
        reset_time_value = None
    
    return {
        'error': 'Rate limit exceeded',
        'message': message,
        'retry_after': retry_after,
        'limit_info': {
            'limit': limit_value,
            'remaining': remaining_value,
            'reset_time': reset_time_value
        }
    }, 429

if __name__ == '__main__':
    host = app.config.get('HOST', '0.0.0.0')
    port = app.config.get('PORT', 5000)
    debug = app.config.get('DEBUG', True)
    
    print(f"🚀 Starting EasySale server...")
    print(f"   Environment: {app.config.get('FLASK_ENV', 'development')}")
    print(f"   Database: {app.config.get('SQLALCHEMY_DATABASE_URI', 'Not configured')}")
    print(f"   Server: http://{host}:{port}")
    print(f"   Debug: {debug}")
    
    # Khởi động Zalo Message Processor service
    try:
        zalo_processor.start()
        print("✅ Zalo Message Processor service started")
    except Exception as e:
        print(f"❌ Failed to start Zalo Message Processor: {e}")
    
    try:
        app.run(host=host, port=port, debug=debug)
    finally:
        # Dừng service khi app shutdown
        zalo_processor.stop()
        print("🛑 Zalo Message Processor service stopped") 