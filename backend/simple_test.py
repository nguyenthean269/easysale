#!/usr/bin/env python3
import requests
import json

BASE_URL = "http://localhost:5000"

def test_refresh():
    print("🔄 Testing refresh token...")
    
    # 1. Login
    login_data = {"username": "user", "password": "user123"}
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    
    if response.status_code == 200:
        data = response.json()
        access_token = data.get('access_token')
        refresh_token = data.get('refresh_token')
        
        print(f"✅ Login: access_token={bool(access_token)}, refresh_token={bool(refresh_token)}")
        
        # 2. Test refresh với refresh token
        headers = {'Authorization': f'Bearer {refresh_token}'}
        refresh_response = requests.post(f"{BASE_URL}/auth/refresh", headers=headers)
        
        print(f"Refresh status: {refresh_response.status_code}")
        if refresh_response.status_code == 200:
            print("✅ Refresh successful!")
        else:
            print(f"❌ Refresh failed: {refresh_response.text}")
    else:
        print(f"❌ Login failed: {response.text}")

if __name__ == "__main__":
    test_refresh() 