#!/usr/bin/env python3
"""
Debug script cho JWT token
"""

import requests
import json
import jwt
from datetime import datetime

# Cấu hình
BASE_URL = "http://localhost:5000"
LOGIN_URL = f"{BASE_URL}/auth/login"
CRAWLS_URL = f"{BASE_URL}/user/crawls"

def decode_jwt_token(token):
    """Decode JWT token (không verify signature)"""
    try:
        # Decode không verify signature để xem payload
        decoded = jwt.decode(token, options={"verify_signature": False})
        return decoded
    except Exception as e:
        print(f"❌ Error decoding token: {str(e)}")
        return None

def analyze_token(token):
    """Phân tích JWT token"""
    print(f"\n🔍 Analyzing JWT token...")
    print(f"Token length: {len(token)} characters")
    print(f"Token preview: {token[:50]}...{token[-50:] if len(token) > 100 else ''}")
    
    # Decode token
    decoded = decode_jwt_token(token)
    if decoded:
        print(f"✅ Token decoded successfully")
        print(f"Header: {json.dumps(decoded.get('header', {}), indent=2)}")
        print(f"Payload: {json.dumps(decoded.get('payload', decoded), indent=2)}")
        
        # Kiểm tra expiration
        exp = decoded.get('exp')
        if exp:
            exp_time = datetime.fromtimestamp(exp)
            now = datetime.now()
            print(f"Expiration: {exp_time}")
            print(f"Current time: {now}")
            if exp_time > now:
                print(f"✅ Token is still valid")
            else:
                print(f"❌ Token has expired")
        
        return decoded
    else:
        print(f"❌ Failed to decode token")
        return None

def test_token_in_request(token):
    """Test token trong request thực tế"""
    print(f"\n🌐 Testing token in actual request...")
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Test với profile endpoint
    try:
        response = requests.get(f"{BASE_URL}/user/profile", headers=headers)
        print(f"Profile endpoint - Status: {response.status_code}")
        if response.status_code != 200:
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {str(e)}")
    
    # Test với crawls endpoint
    try:
        data = {'link': 'https://example.com', 'crawl_tool': 'firecrawl'}
        response = requests.post(CRAWLS_URL, json=data, headers=headers)
        print(f"Crawls endpoint - Status: {response.status_code}")
        if response.status_code != 200:
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {str(e)}")

def test_different_token_formats():
    """Test các format token khác nhau"""
    print(f"\n🧪 Testing different token formats...")
    
    # Test 1: Token không có "Bearer "
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test"
    headers = {'Authorization': token}
    try:
        response = requests.get(f"{BASE_URL}/user/profile", headers=headers)
        print(f"Token without 'Bearer ' - Status: {response.status_code}")
    except Exception as e:
        print(f"Error: {str(e)}")
    
    # Test 2: Token rỗng
    headers = {'Authorization': 'Bearer '}
    try:
        response = requests.get(f"{BASE_URL}/user/profile", headers=headers)
        print(f"Empty token - Status: {response.status_code}")
    except Exception as e:
        print(f"Error: {str(e)}")
    
    # Test 3: Không có Authorization header
    try:
        response = requests.get(f"{BASE_URL}/user/profile")
        print(f"No Authorization header - Status: {response.status_code}")
    except Exception as e:
        print(f"Error: {str(e)}")

def main():
    """Main debug function"""
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
                analyze_token(token)
                
                # Bước 3: Test token trong request
                test_token_in_request(token)
                
                # Bước 4: Test các format khác
                test_different_token_formats()
                
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