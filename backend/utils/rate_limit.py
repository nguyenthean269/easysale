"""
Utility functions cho rate limiting
"""

from functools import wraps
from flask import request, jsonify, current_app
from flask_jwt_extended import get_jwt_identity

def apply_rate_limit(limit_string):
    """
    Decorator để apply rate limiting
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Sử dụng current_app.limiter để apply rate limit
            if hasattr(current_app, 'limiter') and current_app.limiter:
                try:
                    # Sử dụng limit decorator trực tiếp
                    limited_func = current_app.limiter.limit(limit_string)(f)
                    return limited_func(*args, **kwargs)
                except Exception as e:
                    # Nếu có lỗi, trả về error response
                    print(f"Rate limit error: {str(e)}")  # Debug log
                    return jsonify({
                        'error': 'Rate limit error',
                        'message': 'Có lỗi xảy ra khi kiểm tra rate limit',
                        'details': str(e)
                    }), 500
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def user_rate_limit(limit_string):
    """
    Decorator để tạo rate limit dựa trên user ID
    Sử dụng cho các API cần authentication
    """
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            # Lấy user ID từ JWT token
            try:
                identity = get_jwt_identity()
                # Bây giờ identity là string (user_id)
                user_id = identity if identity else 'anonymous'
                key = f"user:{user_id}"
            except:
                # Nếu không có token, sử dụng IP address
                key = f"ip:{request.remote_addr}"
            
            # Kiểm tra rate limit
            if current_app.limiter.is_allowed(key, limit_string):
                return f(*args, **kwargs)
            else:
                # Lấy thông tin rate limit
                try:
                    import time
                    window_stats = current_app.limiter.get_window_stats(key, limit_string)
                    if window_stats and len(window_stats) >= 2:
                        reset_time = window_stats[1]
                        retry_after = max(0, int(reset_time - time.time()))
                    else:
                        retry_after = None
                except:
                    retry_after = None
                
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
                
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'message': message,
                    'retry_after': retry_after,
                    'limit': limit_string
                }), 429
        return wrapped
    return decorator

def ip_rate_limit(limit_string):
    """
    Decorator để tạo rate limit dựa trên IP address
    Sử dụng cho các API không cần authentication
    """
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            key = f"ip:{request.remote_addr}"
            
            if current_app.limiter.is_allowed(key, limit_string):
                return f(*args, **kwargs)
            else:
                # Lấy thông tin rate limit
                try:
                    import time
                    window_stats = current_app.limiter.get_window_stats(key, limit_string)
                    if window_stats and len(window_stats) >= 2:
                        reset_time = window_stats[1]
                        retry_after = max(0, int(reset_time - time.time()))
                    else:
                        retry_after = None
                except:
                    retry_after = None
                
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
                
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'message': message,
                    'retry_after': retry_after,
                    'limit': limit_string
                }), 429
        return wrapped
    return decorator

def get_rate_limit_info():
    """
    Lấy thông tin về rate limit hiện tại
    """
    try:
        identity = get_jwt_identity()
        user_id = identity.get('user_id', 'anonymous')
        key = f"user:{user_id}"
    except:
        key = f"ip:{request.remote_addr}"
    
    # Lấy thông tin rate limit chi tiết
    try:
        import time
        # Lấy thông tin cho các limit khác nhau
        limits_info = {}
        
        # Test với một số limit phổ biến
        common_limits = ["5 per minute", "10 per minute", "30 per minute", "50 per hour", "200 per day"]
        
        for limit in common_limits:
            try:
                window_stats = current_app.limiter.get_window_stats(key, limit)
                if window_stats and len(window_stats) >= 2:
                    remaining, reset_time = window_stats[0], window_stats[1]
                    retry_after = max(0, int(reset_time - time.time()))
                    
                    limits_info[limit] = {
                        'remaining': remaining,
                        'reset_time': reset_time,
                        'retry_after': retry_after,
                        'is_allowed': remaining > 0
                    }
            except:
                continue
        
        # Đảm bảo storage name có thể serialize
        storage_name = 'Unknown'
        try:
            if hasattr(current_app.limiter, 'storage') and current_app.limiter.storage:
                storage_name = current_app.limiter.storage.__class__.__name__
        except:
            storage_name = 'Unknown'
        
        return {
            'key': key,
            'current_time': int(time.time()),
            'limits': limits_info,
            'storage': storage_name
        }
    except Exception as e:
        # Đảm bảo storage name có thể serialize trong exception handler
        storage_name = 'Unknown'
        try:
            if hasattr(current_app.limiter, 'storage') and current_app.limiter.storage:
                storage_name = current_app.limiter.storage.__class__.__name__
        except:
            storage_name = 'Unknown'
        
        return {
            'key': key,
            'error': str(e),
            'storage': storage_name
        } 