#!/usr/bin/env python3
"""
Script để debug user role và kiểm tra tại sao API /zalo-chunks/sessions trả về 401
"""

import requests
import json
import sys
import os

# Thêm backend vào path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import get_config

config = get_config()
BASE_URL = f"http://localhost:{config.PORT}"

def login_and_get_token():
    """Đăng nhập và lấy token"""
    print("🔐 Đang đăng nhập...")
    
    login_data = {
        "username": "admin",  # Thay đổi username nếu cần
        "password": "admin123"  # Thay đổi password nếu cần
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        print(f"Login Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token')
            print(f"✅ Đăng nhập thành công")
            print(f"Token: {token[:50]}...")
            return token
        else:
            print(f"❌ Login failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Login error: {str(e)}")
        return None

def check_user_profile(token):
    """Kiểm tra profile của user hiện tại"""
    print("\n👤 Kiểm tra user profile...")
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(f"{BASE_URL}/auth/profile", headers=headers)
        print(f"Profile Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Profile retrieved successfully")
            print(f"User ID: {data.get('id')}")
            print(f"Username: {data.get('username')}")
            print(f"Role: {data.get('role')}")
            print(f"Email: {data.get('email')}")
            return data
        else:
            print(f"❌ Profile failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Profile error: {str(e)}")
        return None

def check_user_permissions(token):
    """Kiểm tra permissions của user"""
    print("\n🔑 Kiểm tra user permissions...")
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(f"{BASE_URL}/auth/permissions", headers=headers)
        print(f"Permissions Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Permissions retrieved successfully")
            print(f"Role: {data.get('role')}")
            print(f"Permissions: {data.get('permissions')}")
            return data
        else:
            print(f"❌ Permissions failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Permissions error: {str(e)}")
        return None

def test_zalo_sessions_api(token):
    """Test API /zalo-chunks/sessions"""
    print("\n📋 Testing /zalo-chunks/sessions API...")
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(f"{BASE_URL}/zalo-chunks/sessions", headers=headers)
        print(f"Sessions API Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Sessions API successful")
            print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
            return True
        else:
            print(f"❌ Sessions API failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Sessions API error: {str(e)}")
        return False

def test_other_apis(token):
    """Test các API khác để so sánh"""
    print("\n🔄 Testing other APIs for comparison...")
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Test user profile API
    try:
        response = requests.get(f"{BASE_URL}/user/profile", headers=headers)
        print(f"User Profile API Status: {response.status_code}")
    except Exception as e:
        print(f"User Profile API Error: {str(e)}")
    
    # Test posts API
    try:
        response = requests.get(f"{BASE_URL}/posts/", headers=headers)
        print(f"Posts API Status: {response.status_code}")
    except Exception as e:
        print(f"Posts API Error: {str(e)}")
    
    # Test content API
    try:
        response = requests.post(f"{BASE_URL}/content/generate", 
                               json={"prompt": "test"}, headers=headers)
        print(f"Content API Status: {response.status_code}")
    except Exception as e:
        print(f"Content API Error: {str(e)}")

def main():
    print("🚀 Debug User Role và API /zalo-chunks/sessions")
    print("=" * 60)
    
    # Đăng nhập
    token = login_and_get_token()
    if not token:
        print("❌ Không thể đăng nhập. Kết thúc.")
        return
    
    # Kiểm tra profile
    profile = check_user_profile(token)
    if not profile:
        print("❌ Không thể lấy profile. Kết thúc.")
        return
    
    # Kiểm tra permissions
    permissions = check_user_permissions(token)
    if not permissions:
        print("❌ Không thể lấy permissions. Kết thúc.")
        return
    
    # Test zalo sessions API
    sessions_success = test_zalo_sessions_api(token)
    
    # Test các API khác
    test_other_apis(token)
    
    print("\n" + "=" * 60)
    print("📊 TÓM TẮT:")
    print(f"User Role: {profile.get('role')}")
    print(f"Zalo Sessions API: {'✅ Thành công' if sessions_success else '❌ Thất bại'}")
    
    if not sessions_success:
        print("\n🔍 PHÂN TÍCH:")
        print("- API /zalo-chunks/sessions yêu cầu role 'admin' hoặc 'manager'")
        print("- Nếu user có role khác, sẽ nhận lỗi 401/403")
        print("- Kiểm tra lại role của user trong database")

if __name__ == "__main__":
    main()






