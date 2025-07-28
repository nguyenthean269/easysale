#!/usr/bin/env python3
import requests
import json
import jwt
from datetime import datetime

BASE_URL = "http://localhost:5000"

def decode_token(token):
    """Decode JWT token để xem thông tin"""
    try:
        decoded = jwt.decode(token, options={"verify_signature": False})
        return decoded
    except Exception as e:
        print(f"❌ Error decoding token: {str(e)}")
        return None

def test_token_issue():
    print("🔍 Debugging token issue...")
    
    # 1. Login để lấy tokens
    login_data = {"username": "user", "password": "user123"}
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    
    if response.status_code == 200:
        data = response.json()
        access_token = data.get('access_token')
        refresh_token = data.get('refresh_token')
        
        print("✅ Login successful")
        
        # 2. Decode và phân tích tokens
        print("\n🔍 Analyzing tokens...")
        
        access_decoded = decode_token(access_token)
        if access_decoded:
            print("Access Token:")
            print(f"  Type: {access_decoded.get('type', 'unknown')}")
            print(f"  Subject: {access_decoded.get('sub', 'unknown')}")
            print(f"  Expires: {datetime.fromtimestamp(access_decoded.get('exp', 0))}")
        
        refresh_decoded = decode_token(refresh_token)
        if refresh_decoded:
            print("Refresh Token:")
            print(f"  Type: {refresh_decoded.get('type', 'unknown')}")
            print(f"  Subject: {refresh_decoded.get('sub', 'unknown')}")
            print(f"  Expires: {datetime.fromtimestamp(refresh_decoded.get('exp', 0))}")
        
        # 3. Test refresh với refresh token
        print("\n🧪 Testing refresh with refresh token...")
        headers = {'Authorization': f'Bearer {refresh_token}'}
        refresh_response = requests.post(f"{BASE_URL}/auth/refresh", headers=headers)
        
        print(f"Status: {refresh_response.status_code}")
        print(f"Response: {refresh_response.text}")
        
        if refresh_response.status_code == 200:
            print("✅ Refresh successful!")
        else:
            print("❌ Refresh failed")
            
            # 4. Test với access token để so sánh
            print("\n🧪 Testing refresh with access token (should fail)...")
            headers = {'Authorization': f'Bearer {access_token}'}
            wrong_response = requests.post(f"{BASE_URL}/auth/refresh", headers=headers)
            print(f"Wrong Status: {wrong_response.status_code}")
            print(f"Wrong Response: {wrong_response.text}")
            
    else:
        print(f"❌ Login failed: {response.text}")

if __name__ == "__main__":
    test_token_issue() 