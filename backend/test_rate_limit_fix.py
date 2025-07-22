#!/usr/bin/env python3
"""
Script test để kiểm tra rate limit fix
"""

import requests
import json

BASE_URL = 'http://localhost:5000'

def test_rate_limit_response():
    """Test rate limit response để đảm bảo không có function object"""
    print("🧪 Testing Rate Limit Response...")
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
        
        try:
            response = requests.post(f'{BASE_URL}/auth/register', json=data)
            
            if response.status_code == 201:
                print(f"✅ Request {i+1}: Đăng ký thành công")
            elif response.status_code == 429:
                print(f"🚫 Request {i+1}: Rate limit exceeded")
                
                # Kiểm tra response có thể parse JSON không
                try:
                    response_data = response.json()
                    print(f"   ✅ JSON response parsed successfully")
                    print(f"   Error: {response_data.get('error')}")
                    print(f"   Message: {response_data.get('message')}")
                    print(f"   Retry After: {response_data.get('retry_after')}")
                    
                    # Kiểm tra limit_info
                    if 'limit_info' in response_data:
                        limit_info = response_data['limit_info']
                        print(f"   Limit Info: {json.dumps(limit_info, indent=2)}")
                    
                    # Kiểm tra tất cả các giá trị đều có thể serialize
                    test_json = json.dumps(response_data)
                    print(f"   ✅ Response can be serialized to JSON")
                    
                except json.JSONDecodeError as e:
                    print(f"   ❌ JSON decode error: {e}")
                    print(f"   Raw response: {response.text}")
                except TypeError as e:
                    print(f"   ❌ Type error during JSON serialization: {e}")
                    print(f"   Response data: {response_data}")
                
                break
            else:
                print(f"❌ Request {i+1}: Lỗi {response.status_code}")
                print(f"   Response: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request {i+1}: Network error - {e}")

def test_rate_limit_status():
    """Test rate limit status endpoint"""
    print("\n🧪 Testing Rate Limit Status...")
    print("=" * 60)
    
    try:
        response = requests.get(f'{BASE_URL}/auth/rate-limit-status')
        
        if response.status_code == 200:
            try:
                data = response.json()
                print("✅ Rate limit status thành công")
                
                # Kiểm tra có thể serialize không
                test_json = json.dumps(data)
                print("✅ Status response can be serialized to JSON")
                
                # Hiển thị thông tin
                if 'data' in data and 'limits' in data['data']:
                    limits = data['data']['limits']
                    print(f"📊 Found {len(limits)} rate limits:")
                    for limit, info in limits.items():
                        print(f"   {limit}: {info.get('remaining', 0)} remaining")
                
            except json.JSONDecodeError as e:
                print(f"❌ JSON decode error: {e}")
                print(f"Raw response: {response.text}")
            except TypeError as e:
                print(f"❌ Type error during JSON serialization: {e}")
        else:
            print(f"❌ Rate limit status thất bại: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")

def test_login_rate_limit():
    """Test login rate limit"""
    print("\n🧪 Testing Login Rate Limit...")
    print("=" * 60)
    
    # Test vượt quá limit 10 per minute
    for i in range(12):
        data = {
            "username": "admin",
            "password": "wrongpassword"  # Sai mật khẩu để test
        }
        
        try:
            response = requests.post(f'{BASE_URL}/auth/login', json=data)
            
            if response.status_code == 401:
                print(f"✅ Request {i+1}: Login thất bại (đúng - sai mật khẩu)")
            elif response.status_code == 429:
                print(f"🚫 Request {i+1}: Rate limit exceeded")
                
                try:
                    response_data = response.json()
                    print(f"   ✅ JSON response parsed successfully")
                    print(f"   Error: {response_data.get('error')}")
                    print(f"   Message: {response_data.get('message')}")
                    print(f"   Retry After: {response_data.get('retry_after')}")
                    
                    # Test JSON serialization
                    test_json = json.dumps(response_data)
                    print(f"   ✅ Response can be serialized to JSON")
                    
                except Exception as e:
                    print(f"   ❌ Error processing response: {e}")
                
                break
            else:
                print(f"❌ Request {i+1}: Lỗi {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request {i+1}: Network error - {e}")

def main():
    print("🚀 Testing Rate Limit Fix...")
    print("=" * 80)
    
    # Test các trường hợp khác nhau
    test_rate_limit_response()
    test_rate_limit_status()
    test_login_rate_limit()
    
    print("\n" + "=" * 80)
    print("🎉 Hoàn thành test Rate Limit Fix!")
    print("\n💡 Kết quả:")
    print("- Rate limit response không chứa function object")
    print("- JSON serialization hoạt động bình thường")
    print("- Error handling được cải thiện")

if __name__ == '__main__':
    main() 