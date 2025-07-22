#!/usr/bin/env python3
"""
Script test API cho EasySale
"""

import requests
import json

BASE_URL = 'http://localhost:5000'

def test_register():
    """Test chức năng đăng ký"""
    print("🧪 Testing Register API...")
    
    # Test đăng ký thành công
    register_data = {
        "username": "testuser",
        "password": "test123",
        "email": "test@example.com",
        "full_name": "Test User",
        "phone": "0123456789"
    }
    
    response = requests.post(f'{BASE_URL}/auth/register', json=register_data)
    print(f"Register Response: {response.status_code}")
    if response.status_code == 201:
        print("✅ Đăng ký thành công")
        return response.json().get('access_token')
    else:
        print(f"❌ Đăng ký thất bại: {response.json()}")
        return None

def test_login():
    """Test chức năng đăng nhập"""
    print("\n🧪 Testing Login API...")
    
    # Test đăng nhập với admin
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    response = requests.post(f'{BASE_URL}/auth/login', json=login_data)
    print(f"Login Response: {response.status_code}")
    if response.status_code == 200:
        print("✅ Đăng nhập thành công")
        return response.json().get('access_token')
    else:
        print(f"❌ Đăng nhập thất bại: {response.json()}")
        return None

def test_profile(token):
    """Test chức năng lấy profile"""
    print("\n🧪 Testing Profile API...")
    
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(f'{BASE_URL}/auth/profile', headers=headers)
    print(f"Profile Response: {response.status_code}")
    if response.status_code == 200:
        print("✅ Lấy profile thành công")
        print(f"User info: {response.json()}")
    else:
        print(f"❌ Lấy profile thất bại: {response.json()}")

def test_invalid_register():
    """Test đăng ký với dữ liệu không hợp lệ"""
    print("\n🧪 Testing Invalid Register...")
    
    # Test email không hợp lệ
    invalid_data = {
        "username": "testuser2",
        "password": "test123",
        "email": "invalid-email",
        "full_name": "Test User 2"
    }
    
    response = requests.post(f'{BASE_URL}/auth/register', json=invalid_data)
    print(f"Invalid Register Response: {response.status_code}")
    if response.status_code == 400:
        print("✅ Validation hoạt động đúng")
    else:
        print(f"❌ Validation không hoạt động: {response.json()}")

def test_rate_limiting():
    """Test rate limiting"""
    print("\n🧪 Testing Rate Limiting...")
    
    # Test rate limit cho register
    print("Testing register rate limit...")
    for i in range(6):  # Vượt quá limit 5 per minute
        response = requests.post(f'{BASE_URL}/auth/register', json={
            "username": f"testuser{i}",
            "password": "test123",
            "email": f"test{i}@example.com",
            "full_name": f"Test User {i}"
        })
        if response.status_code == 429:
            print(f"✅ Rate limit hoạt động đúng (request {i+1})")
            break
        elif response.status_code == 201:
            print(f"✅ Request {i+1} thành công")
        else:
            print(f"❌ Request {i+1} thất bại: {response.status_code}")
    
    # Test rate limit cho login
    print("Testing login rate limit...")
    for i in range(11):  # Vượt quá limit 10 per minute
        response = requests.post(f'{BASE_URL}/auth/login', json={
            "username": "admin",
            "password": "wrongpassword"
        })
        if response.status_code == 429:
            print(f"✅ Login rate limit hoạt động đúng (request {i+1})")
            break
        elif response.status_code == 401:
            print(f"✅ Login request {i+1} thất bại (sai mật khẩu)")
        else:
            print(f"❌ Login request {i+1} thất bại: {response.status_code}")

def test_rate_limit_status():
    """Test endpoint rate limit status"""
    print("\n🧪 Testing Rate Limit Status...")
    
    response = requests.get(f'{BASE_URL}/auth/rate-limit-status')
    print(f"Rate Limit Status Response: {response.status_code}")
    if response.status_code == 200:
        print("✅ Rate limit status hoạt động")
        print(f"Data: {response.json()}")
    else:
        print(f"❌ Rate limit status thất bại: {response.json()}")

def main():
    print("🚀 Bắt đầu test API...")
    print("=" * 50)
    
    # Test đăng ký
    token = test_register()
    
    # Test đăng nhập
    login_token = test_login()
    
    # Test profile với token đăng nhập
    if login_token:
        test_profile(login_token)
    
    # Test validation
    test_invalid_register()
    
    # Test rate limiting
    test_rate_limiting()
    
    # Test rate limit status
    test_rate_limit_status()
    
    print("\n" + "=" * 50)
    print("🎉 Hoàn thành test API!")

if __name__ == '__main__':
    main() 