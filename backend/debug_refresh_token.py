#!/usr/bin/env python3
"""
Debug script cho refresh token
"""

import requests
import json
import jwt
from datetime import datetime

# Cấu hình
BASE_URL = "http://localhost:5000"
LOGIN_URL = f"{BASE_URL}/auth/login"
REFRESH_URL = f"{BASE_URL}/auth/refresh"

def decode_token(token):
    """Decode JWT token để xem thông tin"""
    try:
        decoded = jwt.decode(token, options={"verify_signature": False})
        return decoded
    except Exception as e:
        print(f"❌ Error decoding token: {str(e)}")
        return None

def analyze_tokens(access_token, refresh_token):
    """Phân tích cả access token và refresh token"""
    print("\n🔍 Analyzing tokens...")
    
    # Decode access token
    access_decoded = decode_token(access_token)
    if access_decoded:
        print(f"✅ Access Token decoded:")
        print(f"   Type: {access_decoded.get('type', 'unknown')}")
        print(f"   Subject: {access_decoded.get('sub', 'unknown')}")
        print(f"   Expires: {datetime.fromtimestamp(access_decoded.get('exp', 0))}")
        print(f"   Issued: {datetime.fromtimestamp(access_decoded.get('iat', 0))}")
    
    # Decode refresh token
    refresh_decoded = decode_token(refresh_token)
    if refresh_decoded:
        print(f"✅ Refresh Token decoded:")
        print(f"   Type: {refresh_decoded.get('type', 'unknown')}")
        print(f"   Subject: {refresh_decoded.get('sub', 'unknown')}")
        print(f"   Expires: {datetime.fromtimestamp(refresh_decoded.get('exp', 0))}")
        print(f"   Issued: {datetime.fromtimestamp(refresh_decoded.get('iat', 0))}")

def test_refresh_with_access_token(access_token):
    """Test refresh endpoint với access token (sẽ fail)"""
    print(f"\n🧪 Testing refresh with ACCESS token (should fail)...")
    
    headers = {'Authorization': f'Bearer {access_token}'}
    try:
        response = requests.post(REFRESH_URL, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 401:
            print("✅ Correctly rejected access token for refresh endpoint")
        else:
            print("❌ Unexpected response - should be 401")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_refresh_with_refresh_token(refresh_token):
    """Test refresh endpoint với refresh token (sẽ success)"""
    print(f"\n🧪 Testing refresh with REFRESH token (should succeed)...")
    
    headers = {'Authorization': f'Bearer {refresh_token}'}
    try:
        response = requests.post(REFRESH_URL, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Refresh token works correctly")
            data = response.json()
            new_access_token = data.get('access_token')
            if new_access_token:
                print(f"New access token: {new_access_token[:30]}...{new_access_token[-30:]}")
        else:
            print("❌ Refresh token failed")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def main():
    """Main debug function"""
    print("🔄 Refresh Token Debug Tool")
    print("=" * 50)
    
    # Bước 1: Login để lấy tokens
    print("\n1. Login to get tokens...")
    login_data = {
        "username": "user",
        "password": "user123"
    }
    
    try:
        response = requests.post(LOGIN_URL, json=login_data)
        print(f"Login Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            access_token = data.get('access_token')
            refresh_token = data.get('refresh_token')
            
            if access_token and refresh_token:
                print("✅ Login successful, got both tokens")
                
                # Bước 2: Phân tích tokens
                analyze_tokens(access_token, refresh_token)
                
                # Bước 3: Test với access token (sẽ fail)
                test_refresh_with_access_token(access_token)
                
                # Bước 4: Test với refresh token (sẽ success)
                test_refresh_with_refresh_token(refresh_token)
                
                # Bước 5: Hiển thị curl commands
                print(f"\n📋 Curl commands for testing:")
                print(f"\n# Test with ACCESS token (should fail):")
                print(f"curl -X POST '{REFRESH_URL}' \\")
                print(f"  -H 'Authorization: Bearer {access_token}' \\")
                print(f"  -H 'Content-Type: application/json'")
                
                print(f"\n# Test with REFRESH token (should succeed):")
                print(f"curl -X POST '{REFRESH_URL}' \\")
                print(f"  -H 'Authorization: Bearer {refresh_token}' \\")
                print(f"  -H 'Content-Type: application/json'")
                
            else:
                print("❌ Missing tokens in response")
                print(f"Response: {data}")
        else:
            print(f"❌ Login failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error during login: {str(e)}")
    
    print("\n" + "=" * 50)
    print("✅ Debug completed!")

if __name__ == "__main__":
    main() 