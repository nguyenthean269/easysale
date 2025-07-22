#!/usr/bin/env python3
"""
Debug JWT token chi tiết
"""

import requests
import json
import jwt
from datetime import datetime

# Cấu hình
BASE_URL = "http://localhost:5000"
LOGIN_URL = f"{BASE_URL}/auth/login"

def decode_and_analyze_token(token):
    """Decode và phân tích JWT token"""
    print(f"\n🔍 Analyzing JWT token...")
    print(f"Token length: {len(token)} characters")
    print(f"Token preview: {token[:50]}...{token[-50:] if len(token) > 100 else ''}")
    
    try:
        # Decode không verify signature
        decoded = jwt.decode(token, options={"verify_signature": False})
        print(f"✅ Token decoded successfully")
        print(f"Decoded payload: {json.dumps(decoded, indent=2, ensure_ascii=False)}")
        
        # Kiểm tra các field quan trọng
        sub = decoded.get('sub')
        exp = decoded.get('exp')
        iat = decoded.get('iat')
        
        print(f"\n📋 Token fields:")
        print(f"  sub (subject): {sub} (type: {type(sub)})")
        print(f"  exp (expiration): {exp}")
        print(f"  iat (issued at): {iat}")
        
        if exp:
            exp_time = datetime.fromtimestamp(exp)
            now = datetime.now()
            print(f"  Expiration time: {exp_time}")
            print(f"  Current time: {now}")
            if exp_time > now:
                print(f"  ✅ Token is still valid")
            else:
                print(f"  ❌ Token has expired")
        
        return decoded
        
    except Exception as e:
        print(f"❌ Error decoding token: {str(e)}")
        return None

def test_token_with_different_endpoints(token):
    """Test token với các endpoint khác nhau"""
    print(f"\n🌐 Testing token with different endpoints...")
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    endpoints = [
        ('/user/profile', 'GET'),
        ('/user/crawls', 'GET'),
        ('/auth/permissions', 'GET')
    ]
    
    for endpoint, method in endpoints:
        try:
            url = f"{BASE_URL}{endpoint}"
            if method == 'GET':
                response = requests.get(url, headers=headers)
            else:
                response = requests.post(url, headers=headers)
            
            print(f"  {method} {endpoint}: {response.status_code}")
            if response.status_code != 200:
                print(f"    Response: {response.text}")
                
        except Exception as e:
            print(f"  {method} {endpoint}: Error - {str(e)}")

def test_with_curl_equivalent(token):
    """Test với curl equivalent"""
    print(f"\n🔧 Testing with curl equivalent...")
    
    # Test profile endpoint
    curl_command = f'''curl -X GET "{BASE_URL}/user/profile" \\
  -H "Authorization: Bearer {token}" \\
  -H "Content-Type: application/json"'''
    
    print(f"Profile test command:")
    print(f"  {curl_command}")
    
    # Test crawls endpoint
    curl_command = f'''curl -X POST "{BASE_URL}/user/crawls" \\
  -H "Authorization: Bearer {token}" \\
  -H "Content-Type: application/json" \\
  -d '{{"link": "https://example.com", "crawl_tool": "firecrawl"}}' '''
    
    print(f"\nCrawls test command:")
    print(f"  {curl_command}")

def main():
    """Main function"""
    print("🔧 JWT Token Debug Tool")
    print("=" * 50)
    
    # Bước 1: Lấy token
    print("\n1. Getting JWT token...")
    login_data = {
        "username": "user",
        "password": "user123"
    }
    
    try:
        response = requests.post(LOGIN_URL, json=login_data)
        print(f"Login Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token')
            
            if token:
                print("✅ Token received successfully")
                
                # Bước 2: Phân tích token
                decoded = decode_and_analyze_token(token)
                
                # Bước 3: Test với các endpoint
                test_token_with_different_endpoints(token)
                
                # Bước 4: Hiển thị curl commands
                test_with_curl_equivalent(token)
                
            else:
                print("❌ No token in response")
                print(f"Response: {data}")
        else:
            print(f"❌ Login failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error during login: {str(e)}")
    
    print("\n" + "=" * 50)
    print("✅ Debug completed!")

if __name__ == "__main__":
    main() 