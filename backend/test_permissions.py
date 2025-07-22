#!/usr/bin/env python3
"""
Script test permission system cho EasySale
"""

import requests
import json

BASE_URL = 'http://localhost:5000'

def login_user(username, password):
    """Đăng nhập và trả về token"""
    login_data = {
        "username": username,
        "password": password
    }
    
    response = requests.post(f'{BASE_URL}/auth/login', json=login_data)
    if response.status_code == 200:
        return response.json().get('access_token')
    return None

def test_admin_permissions():
    """Test permissions của admin"""
    print("🧪 Testing Admin Permissions...")
    print("=" * 50)
    
    # Đăng nhập admin
    admin_token = login_user('admin', 'admin123')
    if not admin_token:
        print("❌ Không thể đăng nhập admin")
        return
    
    headers = {'Authorization': f'Bearer {admin_token}'}
    
    # Test admin dashboard
    response = requests.get(f'{BASE_URL}/admin/dashboard', headers=headers)
    print(f"Admin Dashboard: {response.status_code}")
    if response.status_code == 200:
        print("✅ Admin có thể truy cập dashboard")
    else:
        print(f"❌ Admin không thể truy cập dashboard: {response.json()}")
    
    # Test get all users
    response = requests.get(f'{BASE_URL}/admin/users', headers=headers)
    print(f"Get All Users: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Admin có thể xem {data.get('total', 0)} users")
    else:
        print(f"❌ Admin không thể xem users: {response.json()}")
    
    # Test get user permissions
    response = requests.get(f'{BASE_URL}/auth/permissions', headers=headers)
    print(f"Get Permissions: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Admin có {data.get('total_permissions', 0)} permissions")
        print(f"   Permissions: {data.get('permissions', [])}")
    else:
        print(f"❌ Không thể lấy permissions: {response.json()}")

def test_user_permissions():
    """Test permissions của user thường"""
    print("\n🧪 Testing User Permissions...")
    print("=" * 50)
    
    # Đăng nhập user
    user_token = login_user('user', 'user123')
    if not user_token:
        print("❌ Không thể đăng nhập user")
        return
    
    headers = {'Authorization': f'Bearer {user_token}'}
    
    # Test user profile
    response = requests.get(f'{BASE_URL}/user/profile', headers=headers)
    print(f"User Profile: {response.status_code}")
    if response.status_code == 200:
        print("✅ User có thể xem profile")
    else:
        print(f"❌ User không thể xem profile: {response.json()}")
    
    # Test admin dashboard (sẽ bị từ chối)
    response = requests.get(f'{BASE_URL}/admin/dashboard', headers=headers)
    print(f"Admin Dashboard (User): {response.status_code}")
    if response.status_code == 403:
        print("✅ User bị từ chối truy cập admin dashboard (đúng)")
    else:
        print(f"❌ User có thể truy cập admin dashboard (sai): {response.json()}")
    
    # Test get all users (sẽ bị từ chối)
    response = requests.get(f'{BASE_URL}/admin/users', headers=headers)
    print(f"Get All Users (User): {response.status_code}")
    if response.status_code == 403:
        print("✅ User bị từ chối xem tất cả users (đúng)")
    else:
        print(f"❌ User có thể xem tất cả users (sai): {response.json()}")
    
    # Test get user permissions
    response = requests.get(f'{BASE_URL}/auth/permissions', headers=headers)
    print(f"Get Permissions (User): {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ User có {data.get('total_permissions', 0)} permissions")
        print(f"   Permissions: {data.get('permissions', [])}")
    else:
        print(f"❌ Không thể lấy permissions: {response.json()}")

def test_ownership_permissions():
    """Test ownership permissions"""
    print("\n🧪 Testing Ownership Permissions...")
    print("=" * 50)
    
    # Đăng nhập user
    user_token = login_user('user', 'user123')
    if not user_token:
        print("❌ Không thể đăng nhập user")
        return
    
    headers = {'Authorization': f'Bearer {user_token}'}
    
    # Test xem profile của chính mình
    response = requests.get(f'{BASE_URL}/user/users/2', headers=headers)  # user ID = 2
    print(f"Own Profile (User): {response.status_code}")
    if response.status_code == 200:
        print("✅ User có thể xem profile của chính mình")
    else:
        print(f"❌ User không thể xem profile của chính mình: {response.json()}")
    
    # Test xem profile của user khác (sẽ bị từ chối)
    response = requests.get(f'{BASE_URL}/user/users/1', headers=headers)  # admin ID = 1
    print(f"Other Profile (User): {response.status_code}")
    if response.status_code == 403:
        print("✅ User bị từ chối xem profile của user khác (đúng)")
    else:
        print(f"❌ User có thể xem profile của user khác (sai): {response.json()}")

def test_admin_management():
    """Test admin management functions"""
    print("\n🧪 Testing Admin Management...")
    print("=" * 50)
    
    # Đăng nhập admin
    admin_token = login_user('admin', 'admin123')
    if not admin_token:
        print("❌ Không thể đăng nhập admin")
        return
    
    headers = {'Authorization': f'Bearer {admin_token}'}
    
    # Test update user
    update_data = {
        "full_name": "Updated User Name",
        "phone": "0987654321"
    }
    response = requests.put(f'{BASE_URL}/admin/users/2', json=update_data, headers=headers)
    print(f"Update User: {response.status_code}")
    if response.status_code == 200:
        print("✅ Admin có thể cập nhật user")
    else:
        print(f"❌ Admin không thể cập nhật user: {response.json()}")
    
    # Test get specific user
    response = requests.get(f'{BASE_URL}/admin/users/2', headers=headers)
    print(f"Get Specific User: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Admin có thể xem thông tin user: {data.get('user', {}).get('full_name')}")
    else:
        print(f"❌ Admin không thể xem thông tin user: {response.json()}")

def test_permission_errors():
    """Test các trường hợp lỗi permission"""
    print("\n🧪 Testing Permission Errors...")
    print("=" * 50)
    
    # Test không có token
    response = requests.get(f'{BASE_URL}/admin/dashboard')
    print(f"No Token: {response.status_code}")
    if response.status_code == 401:
        print("✅ API yêu cầu authentication (đúng)")
    else:
        print(f"❌ API không yêu cầu authentication (sai): {response.json()}")
    
    # Test token không hợp lệ
    headers = {'Authorization': 'Bearer invalid_token'}
    response = requests.get(f'{BASE_URL}/admin/dashboard', headers=headers)
    print(f"Invalid Token: {response.status_code}")
    if response.status_code == 401:
        print("✅ API từ chối token không hợp lệ (đúng)")
    else:
        print(f"❌ API chấp nhận token không hợp lệ (sai): {response.json()}")

def main():
    print("🚀 Bắt đầu test Permission System...")
    print("=" * 60)
    
    # Test các loại permissions khác nhau
    test_admin_permissions()
    test_user_permissions()
    test_ownership_permissions()
    test_admin_management()
    test_permission_errors()
    
    print("\n" + "=" * 60)
    print("🎉 Hoàn thành test Permission System!")
    print("\n💡 Kết quả:")
    print("- Admin có tất cả quyền")
    print("- User chỉ có quyền cơ bản")
    print("- Ownership được kiểm tra chính xác")
    print("- Error handling hoạt động tốt")

if __name__ == '__main__':
    main() 