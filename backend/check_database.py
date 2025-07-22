#!/usr/bin/env python3
"""
Script kiểm tra database và users
"""

from app import app
from models import User, db
from werkzeug.security import check_password_hash

def check_database():
    """Kiểm tra database và users"""
    print("🔍 Kiểm tra database...")
    
    with app.app_context():
        try:
            # Kiểm tra kết nối database
            with db.engine.connect() as conn:
                conn.execute(db.text("SELECT 1"))
            print("✅ Kết nối database thành công")
            
            # Kiểm tra bảng users
            with db.engine.connect() as conn:
                result = conn.execute(db.text("SHOW TABLES LIKE 'users'"))
                if result.fetchone():
                    print("✅ Bảng users tồn tại")
                else:
                    print("❌ Bảng users không tồn tại")
                    return False
            
            # Đếm số users
            user_count = User.query.count()
            print(f"📊 Số lượng users trong database: {user_count}")
            
            # Liệt kê tất cả users
            users = User.query.all()
            if users:
                print("\n👥 Danh sách users:")
                for user in users:
                    print(f"  - ID: {user.id}")
                    print(f"    Username: {user.username}")
                    print(f"    Email: {user.email}")
                    print(f"    Role: {user.role}")
                    print(f"    Active: {user.is_active}")
                    print(f"    Created: {user.created_at}")
                    print()
            else:
                print("❌ Không có users nào trong database")
                return False
            
            # Test password cho user 'user'
            user = User.query.filter_by(username='user').first()
            if user:
                print("🔐 Testing password for user 'user':")
                is_valid = check_password_hash(user.password, 'user123')
                print(f"  Password 'user123' is valid: {is_valid}")
                
                if not is_valid:
                    print("  ❌ Password không đúng!")
                    return False
            else:
                print("❌ Không tìm thấy user 'user'")
                return False
            
            # Test password cho admin
            admin = User.query.filter_by(username='admin').first()
            if admin:
                print("🔐 Testing password for user 'admin':")
                is_valid = check_password_hash(admin.password, 'admin123')
                print(f"  Password 'admin123' is valid: {is_valid}")
                
                if not is_valid:
                    print("  ❌ Password không đúng!")
                    return False
            else:
                print("❌ Không tìm thấy user 'admin'")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Lỗi khi kiểm tra database: {e}")
            return False

def test_login_directly():
    """Test login trực tiếp với database"""
    print("\n🧪 Testing login trực tiếp...")
    
    with app.app_context():
        try:
            # Test user login
            user = User.query.filter_by(username='user').first()
            if user and check_password_hash(user.password, 'user123'):
                print("✅ User login test passed")
            else:
                print("❌ User login test failed")
                return False
            
            # Test admin login
            admin = User.query.filter_by(username='admin').first()
            if admin and check_password_hash(admin.password, 'admin123'):
                print("✅ Admin login test passed")
            else:
                print("❌ Admin login test failed")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Lỗi khi test login: {e}")
            return False

def main():
    """Main function"""
    print("🔧 Database Check Tool")
    print("=" * 50)
    
    # Kiểm tra database
    db_ok = check_database()
    
    if db_ok:
        # Test login
        login_ok = test_login_directly()
        
        if login_ok:
            print("\n✅ Tất cả kiểm tra đều thành công!")
            print("💡 Nếu vẫn gặp lỗi login, có thể do:")
            print("  1. Server chưa được khởi động lại")
            print("  2. Cache hoặc session cũ")
            print("  3. JWT configuration vấn đề")
        else:
            print("\n❌ Login test thất bại!")
    else:
        print("\n❌ Database check thất bại!")
        print("💡 Hãy chạy: python init_db.py")

if __name__ == "__main__":
    main() 