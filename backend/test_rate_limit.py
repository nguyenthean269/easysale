#!/usr/bin/env python3
"""
Script test rate limiting chi tiết cho EasySale
"""

import requests
import time
import json

BASE_URL = 'http://localhost:5000'

def test_register_rate_limit():
    """Test rate limit cho register API"""
    print("🧪 Testing Register Rate Limit...")
    print("=" * 50)
    
    success_count = 0
    rate_limited_count = 0
    
    for i in range(10):
        data = {
            "username": f"testuser{i}",
            "password": "test123",
            "email": f"test{i}@example.com",
            "full_name": f"Test User {i}",
            "phone": f"012345678{i}"
        }
        
        response = requests.post(f'{BASE_URL}/auth/register', json=data)
        
        if response.status_code == 201:
            success_count += 1
            print(f"✅ Request {i+1}: Đăng ký thành công")
        elif response.status_code == 429:
            rate_limited_count += 1
            print(f"🚫 Request {i+1}: Rate limit exceeded")
            print(f"   Response: {response.json()}")
            break
        else:
            print(f"❌ Request {i+1}: Lỗi {response.status_code}")
            print(f"   Response: {response.json()}")
        
        # Delay nhỏ giữa các request
        time.sleep(0.1)
    
    print(f"\n📊 Kết quả Register Rate Limit:")
    print(f"   - Thành công: {success_count}")
    print(f"   - Rate limited: {rate_limited_count}")
    print(f"   - Tổng cộng: {success_count + rate_limited_count}")

def test_login_rate_limit():
    """Test rate limit cho login API"""
    print("\n🧪 Testing Login Rate Limit...")
    print("=" * 50)
    
    success_count = 0
    rate_limited_count = 0
    
    for i in range(15):
        data = {
            "username": "admin",
            "password": "wrongpassword"  # Sai mật khẩu để test
        }
        
        response = requests.post(f'{BASE_URL}/auth/login', json=data)
        
        if response.status_code == 401:
            success_count += 1
            print(f"✅ Request {i+1}: Login thất bại (đúng - sai mật khẩu)")
        elif response.status_code == 429:
            rate_limited_count += 1
            print(f"🚫 Request {i+1}: Rate limit exceeded")
            print(f"   Response: {response.json()}")
            break
        else:
            print(f"❌ Request {i+1}: Lỗi {response.status_code}")
            print(f"   Response: {response.json()}")
        
        time.sleep(0.1)
    
    print(f"\n📊 Kết quả Login Rate Limit:")
    print(f"   - Thành công (401): {success_count}")
    print(f"   - Rate limited: {rate_limited_count}")
    print(f"   - Tổng cộng: {success_count + rate_limited_count}")

def test_profile_rate_limit():
    """Test rate limit cho profile API"""
    print("\n🧪 Testing Profile Rate Limit...")
    print("=" * 50)
    
    # Đăng nhập trước để lấy token
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    login_response = requests.post(f'{BASE_URL}/auth/login', json=login_data)
    if login_response.status_code != 200:
        print("❌ Không thể đăng nhập để test profile")
        return
    
    token = login_response.json().get('access_token')
    headers = {'Authorization': f'Bearer {token}'}
    
    success_count = 0
    rate_limited_count = 0
    
    for i in range(35):
        response = requests.get(f'{BASE_URL}/auth/profile', headers=headers)
        
        if response.status_code == 200:
            success_count += 1
            print(f"✅ Request {i+1}: Profile thành công")
        elif response.status_code == 429:
            rate_limited_count += 1
            print(f"🚫 Request {i+1}: Rate limit exceeded")
            print(f"   Response: {response.json()}")
            break
        else:
            print(f"❌ Request {i+1}: Lỗi {response.status_code}")
            print(f"   Response: {response.json()}")
        
        time.sleep(0.1)
    
    print(f"\n📊 Kết quả Profile Rate Limit:")
    print(f"   - Thành công: {success_count}")
    print(f"   - Rate limited: {rate_limited_count}")
    print(f"   - Tổng cộng: {success_count + rate_limited_count}")

def test_rate_limit_status():
    """Test endpoint rate limit status"""
    print("\n🧪 Testing Rate Limit Status...")
    print("=" * 50)
    
    for i in range(5):
        response = requests.get(f'{BASE_URL}/auth/rate-limit-status')
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Request {i+1}: Rate limit status thành công")
            print(f"   Data: {json.dumps(data, indent=2)}")
        elif response.status_code == 429:
            print(f"🚫 Request {i+1}: Rate limit status bị limit")
            print(f"   Response: {response.json()}")
            break
        else:
            print(f"❌ Request {i+1}: Lỗi {response.status_code}")
            print(f"   Response: {response.json()}")
        
        time.sleep(0.1)

def main():
    print("🚀 Bắt đầu test Rate Limiting chi tiết...")
    print("=" * 60)
    
    # Test các API khác nhau
    test_register_rate_limit()
    test_login_rate_limit()
    test_profile_rate_limit()
    test_rate_limit_status()
    
    print("\n" + "=" * 60)
    print("🎉 Hoàn thành test Rate Limiting!")
    print("\n💡 Lưu ý:")
    print("- Rate limits được reset sau mỗi khoảng thời gian")
    print("- Có thể chạy lại script sau 1 phút để test lại")
    print("- Rate limits được tính theo IP address")

if __name__ == '__main__':
    main() 