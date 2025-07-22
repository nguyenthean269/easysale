#!/usr/bin/env python3
"""
Script tạo file .env từ env.example
"""

import os
import shutil

def create_env_file():
    """Tạo file .env từ env.example"""
    
    # Kiểm tra xem file .env đã tồn tại chưa
    if os.path.exists('.env'):
        print("⚠️  File .env đã tồn tại!")
        response = input("Bạn có muốn ghi đè không? (y/N): ")
        if response.lower() != 'y':
            print("❌ Không tạo file .env")
            return False
    
    # Kiểm tra file env.example có tồn tại không
    if not os.path.exists('env.example'):
        print("❌ File env.example không tồn tại!")
        return False
    
    try:
        # Copy env.example thành .env
        shutil.copy('env.example', '.env')
        print("✅ Đã tạo file .env thành công!")
        print("\n📝 Hãy chỉnh sửa file .env với thông tin database của bạn:")
        print("   - DB_USER: Tên user MySQL")
        print("   - DB_PASSWORD: Mật khẩu MySQL")
        print("   - DB_NAME: Tên database")
        print("   - JWT_SECRET_KEY: Secret key cho JWT")
        return True
        
    except Exception as e:
        print(f"❌ Lỗi khi tạo file .env: {e}")
        return False

def validate_env_file():
    """Validate file .env"""
    if not os.path.exists('.env'):
        print("❌ File .env không tồn tại!")
        return False
    
    # Đọc file .env và kiểm tra các biến quan trọng
    with open('.env', 'r', encoding='utf-8') as f:
        content = f.read()
    
    required_vars = ['DB_USER', 'DB_PASSWORD', 'DB_NAME', 'JWT_SECRET_KEY']
    missing_vars = []
    
    for var in required_vars:
        if f'{var}=' not in content or f'{var}=your_' in content:
            missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️  Các biến sau chưa được cấu hình: {', '.join(missing_vars)}")
        print("   Hãy chỉnh sửa file .env với giá trị thực tế.")
        return False
    
    print("✅ File .env đã được cấu hình đúng!")
    return True

def main():
    print("🔧 EasySale Environment Setup")
    print("=" * 40)
    
    # Tạo file .env
    if create_env_file():
        print("\n" + "=" * 40)
        print("📋 Hướng dẫn cấu hình:")
        print("1. Mở file .env trong editor")
        print("2. Thay đổi các giá trị sau:")
        print("   DB_USER=root")
        print("   DB_PASSWORD=your_mysql_password")
        print("   DB_NAME=easysale_db")
        print("   JWT_SECRET_KEY=your-super-secret-key")
        print("3. Lưu file và chạy lại script này để validate")
        
        # Validate sau khi tạo
        print("\n" + "=" * 40)
        validate_env_file()
    else:
        # Nếu file .env đã tồn tại, chỉ validate
        print("\n" + "=" * 40)
        validate_env_file()

if __name__ == '__main__':
    main() 