#!/usr/bin/env python3
"""
Script test cấu hình cho EasySale
"""

import os
from dotenv import load_dotenv
from config import validate_config, get_config, get_database_url

def test_env_file():
    """Test file .env"""
    print("🧪 Testing .env file...")
    print("=" * 50)
    
    # Kiểm tra file .env có tồn tại không
    if not os.path.exists('.env'):
        print("❌ File .env không tồn tại!")
        print("   Chạy: python create_env.py")
        return False
    
    print("✅ File .env tồn tại")
    
    # Load và kiểm tra các biến
    load_dotenv()
    
    required_vars = [
        'DB_HOST', 'DB_PORT', 'DB_USER', 'DB_PASSWORD', 
        'DB_NAME', 'JWT_SECRET_KEY', 'FLASK_ENV'
    ]
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Ẩn password khi hiển thị
            if 'PASSWORD' in var or 'SECRET' in var:
                display_value = '*' * len(value) if value else 'Not set'
            else:
                display_value = value
            print(f"✅ {var}: {display_value}")
        else:
            print(f"❌ {var}: Not set")
    
    return True

def test_config_validation():
    """Test validation cấu hình"""
    print("\n🧪 Testing configuration validation...")
    print("=" * 50)
    
    if validate_config():
        print("✅ Configuration validation passed")
        return True
    else:
        print("❌ Configuration validation failed")
        return False

def test_database_url():
    """Test database URL generation"""
    print("\n🧪 Testing database URL...")
    print("=" * 50)
    
    db_url = get_database_url()
    print(f"Database URL: {db_url}")
    
    # Kiểm tra format
    if 'mysql://' in db_url and '@' in db_url:
        print("✅ Database URL format is correct")
        return True
    else:
        print("❌ Database URL format is incorrect")
        return False

def test_config_classes():
    """Test configuration classes"""
    print("\n🧪 Testing configuration classes...")
    print("=" * 50)
    
    # Test development config
    dev_config = get_config()
    print(f"Environment: {dev_config.FLASK_ENV}")
    print(f"Debug: {dev_config.DEBUG}")
    print(f"Database URI: {dev_config.SQLALCHEMY_DATABASE_URI}")
    print(f"JWT Secret: {'*' * len(dev_config.JWT_SECRET_KEY) if dev_config.JWT_SECRET_KEY else 'Not set'}")
    
    return True

def test_database_connection():
    """Test kết nối database"""
    print("\n🧪 Testing database connection...")
    print("=" * 50)
    
    try:
        from app import app
        from models import db
        
        with app.app_context():
            # Test kết nối
            db.engine.execute('SELECT 1')
            print("✅ Database connection successful")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("Hãy kiểm tra:")
        print("1. MySQL server đang chạy")
        print("2. Database đã được tạo")
        print("3. Thông tin kết nối trong .env là chính xác")
        return False

def main():
    print("🚀 EasySale Configuration Test")
    print("=" * 60)
    
    tests = [
        ("Environment File", test_env_file),
        ("Configuration Validation", test_config_validation),
        ("Database URL", test_database_url),
        ("Configuration Classes", test_config_classes),
        ("Database Connection", test_database_connection)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 Tất cả tests đều passed! Configuration đã sẵn sàng.")
    else:
        print("⚠️  Một số tests failed. Hãy kiểm tra cấu hình.")
        print("\n💡 Hướng dẫn:")
        print("1. Chạy: python create_env.py")
        print("2. Chỉnh sửa file .env với thông tin thực tế")
        print("3. Chạy lại: python test_config.py")

if __name__ == '__main__':
    main() 