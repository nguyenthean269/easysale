#!/usr/bin/env python3
"""
Script khởi tạo database cho EasySale
"""

from app import app
from models import User, db
from werkzeug.security import generate_password_hash
from config import validate_config

def init_database():
    """Khởi tạo database và tạo bảng"""
    # Validate configuration trước
    if not validate_config():
        print("❌ Configuration không hợp lệ. Hãy kiểm tra file .env")
        return False
    
    with app.app_context():
        try:
            # Tạo tất cả bảng
            db.create_all()
            print("✅ Đã tạo tất cả bảng trong database")
        except Exception as e:
            print(f"❌ Lỗi khi tạo bảng: {e}")
            print("Hãy kiểm tra:")
            print("1. MySQL server đang chạy")
            print("2. Database đã được tạo")
            print("3. Thông tin kết nối trong .env là chính xác")
            return False
        
        try:
            # Kiểm tra xem đã có admin user chưa
            admin_user = User.query.filter_by(username='admin').first()
            if not admin_user:
                # Tạo admin user
                admin_user = User(
                    username='admin',
                    password=generate_password_hash('admin123'),
                    email='admin@easysale.com',
                    full_name='Administrator',
                    role='admin'
                )
                db.session.add(admin_user)
                print("✅ Đã tạo admin user")
            
            # Kiểm tra xem đã có user thường chưa
            regular_user = User.query.filter_by(username='user').first()
            if not regular_user:
                # Tạo user thường
                regular_user = User(
                    username='user',
                    password=generate_password_hash('user123'),
                    email='user@easysale.com',
                    full_name='Regular User',
                    role='user'
                )
                db.session.add(regular_user)
                print("✅ Đã tạo regular user")
            
            # Commit thay đổi
            db.session.commit()
            print("✅ Đã lưu thay đổi vào database")
            
            # Hiển thị thông tin users
            users = User.query.all()
            print(f"\n📊 Tổng số users trong database: {len(users)}")
            for user in users:
                print(f"  - {user.username} ({user.email}) - Role: {user.role}")
            
            return True
            
        except Exception as e:
            print(f"❌ Lỗi khi tạo users: {e}")
            db.session.rollback()
            return False

if __name__ == '__main__':
    print("🚀 Bắt đầu khởi tạo database...")
    try:
        success = init_database()
        if success:
            print("\n🎉 Khởi tạo database thành công!")
        else:
            print("\n❌ Khởi tạo database thất bại!")
    except Exception as e:
        print(f"\n❌ Lỗi khi khởi tạo database: {e}")
        print("Hãy kiểm tra:")
        print("1. MySQL server đang chạy")
        print("2. Database đã được tạo")
        print("3. Thông tin kết nối trong .env là chính xác") 