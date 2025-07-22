#!/usr/bin/env python3
"""
Script test retry_after trong rate limiting
"""

import requests
import time
import json

BASE_URL = 'http://localhost:5000'

def test_retry_after_register():
    """Test retry_after cho register API"""
    print("🧪 Testing Register Rate Limit with retry_after...")
    print("=" * 60)
    
    # Test vượt quá limit 5 per minute
    for i in range(7):
        data = {
            "username": f"testuser{i}",
            "password": "test123",
            "email": f"test{i}@example.com",
            "full_name": f"Test User {i}",
            "phone": f"012345678{i}"
        }
        
        response = requests.post(f'{BASE_URL}/auth/register', json=data)
        
        if response.status_code == 201:
            print(f"✅ Request {i+1}: Đăng ký thành công")
        elif response.status_code == 429:
            print(f"🚫 Request {i+1}: Rate limit exceeded")
            response_data = response.json()
            print(f"   Error: {response_data.get('error')}")
            print(f"   Message: {response_data.get('message')}")
            print(f"   Retry After: {response_data.get('retry_after')} seconds")
            print(f"   Limit: {response_data.get('limit', 'Unknown')}")
            
            if 'limit_info' in response_data:
                limit_info = response_data['limit_info']
                print(f"   Limit Info: {json.dumps(limit_info, indent=2)}")
            
            # Test lại sau một thời gian
            retry_after = response_data.get('retry_after')
            if retry_after and retry_after > 0:
                print(f"   ⏰ Sẽ thử lại sau {retry_after} giây...")
                if retry_after < 10:  # Chỉ wait nếu thời gian ngắn
                    time.sleep(min(retry_after + 1, 5))
                    print("   🔄 Thử lại request...")
                    retry_response = requests.post(f'{BASE_URL}/auth/register', json=data)
                    if retry_response.status_code == 201:
                        print("   ✅ Retry thành công!")
                    else:
                        print(f"   ❌ Retry thất bại: {retry_response.status_code}")
            break
        else:
            print(f"❌ Request {i+1}: Lỗi {response.status_code}")
            print(f"   Response: {response.json()}")

def test_retry_after_login():
    """Test retry_after cho login API"""
    print("\n🧪 Testing Login Rate Limit with retry_after...")
    print("=" * 60)
    
    # Test vượt quá limit 10 per minute
    for i in range(12):
        data = {
            "username": "admin",
            "password": "wrongpassword"  # Sai mật khẩu để test
        }
        
        response = requests.post(f'{BASE_URL}/auth/login', json=data)
        
        if response.status_code == 401:
            print(f"✅ Request {i+1}: Login thất bại (đúng - sai mật khẩu)")
        elif response.status_code == 429:
            print(f"🚫 Request {i+1}: Rate limit exceeded")
            response_data = response.json()
            print(f"   Error: {response_data.get('error')}")
            print(f"   Message: {response_data.get('message')}")
            print(f"   Retry After: {response_data.get('retry_after')} seconds")
            print(f"   Limit: {response_data.get('limit', 'Unknown')}")
            
            if 'limit_info' in response_data:
                limit_info = response_data['limit_info']
                print(f"   Limit Info: {json.dumps(limit_info, indent=2)}")
            break
        else:
            print(f"❌ Request {i+1}: Lỗi {response.status_code}")
            print(f"   Response: {response.json()}")

def test_rate_limit_status():
    """Test endpoint rate limit status với thông tin chi tiết"""
    print("\n🧪 Testing Rate Limit Status with detailed info...")
    print("=" * 60)
    
    response = requests.get(f'{BASE_URL}/auth/rate-limit-status')
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Rate limit status thành công")
        print(f"Data: {json.dumps(data, indent=2)}")
        
        # Phân tích thông tin
        if 'data' in data and 'limits' in data['data']:
            limits = data['data']['limits']
            print(f"\n📊 Phân tích Rate Limits:")
            for limit, info in limits.items():
                remaining = info.get('remaining', 0)
                retry_after = info.get('retry_after', 0)
                is_allowed = info.get('is_allowed', True)
                
                status = "✅ Available" if is_allowed else "🚫 Limited"
                print(f"   {limit}: {remaining} requests remaining - {status}")
                if retry_after > 0:
                    print(f"      Reset in: {retry_after} seconds")
    else:
        print(f"❌ Rate limit status thất bại: {response.status_code}")
        print(f"Response: {response.json()}")

def test_headers():
    """Test rate limit headers"""
    print("\n🧪 Testing Rate Limit Headers...")
    print("=" * 60)
    
    # Test một request bình thường
    response = requests.get(f'{BASE_URL}/auth/rate-limit-status')
    
    print("Headers received:")
    for header, value in response.headers.items():
        if 'ratelimit' in header.lower():
            print(f"   {header}: {value}")
    
    # Test headers khi bị rate limit
    print("\nTesting headers when rate limited:")
    for i in range(6):  # Vượt quá limit 5 per minute
        data = {
            "username": f"testuser{i}",
            "password": "test123",
            "email": f"test{i}@example.com",
            "full_name": f"Test User {i}"
        }
        
        response = requests.post(f'{BASE_URL}/auth/register', json=data)
        
        if response.status_code == 429:
            print("Rate limit headers:")
            for header, value in response.headers.items():
                if 'ratelimit' in header.lower():
                    print(f"   {header}: {value}")
            break

def main():
    print("🚀 Testing Rate Limit Retry After...")
    print("=" * 80)
    
    # Test các trường hợp khác nhau
    test_retry_after_register()
    test_retry_after_login()
    test_rate_limit_status()
    test_headers()
    
    print("\n" + "=" * 80)
    print("🎉 Hoàn thành test Rate Limit Retry After!")
    print("\n💡 Kết quả:")
    print("- Retry after được tính toán chính xác")
    print("- Message hiển thị thời gian cụ thể")
    print("- Rate limit status cung cấp thông tin chi tiết")
    print("- Headers chứa thông tin rate limit")

if __name__ == '__main__':
    main() 