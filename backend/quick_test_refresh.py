#!/usr/bin/env python3
"""
Quick test cho refresh token
"""

import requests
import json

# Cấu hình
BASE_URL = "http://localhost:5000"
LOGIN_URL = f"{BASE_URL}/auth/login"
REFRESH_URL = f"{BASE_URL}/auth/refresh"

def main():
    print("🔄 Quick Refresh Token Test")
    print("=" * 40)
    
    # Test 1: Login
    print("\n1. Testing login...")
    login_data = {"username": "user", "password": "user123"}
    
    try:
        response = requests.post(LOGIN_URL, json=login_data)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            access_token = data.get('access_token')
            refresh_token = data.get('refresh_token')
            
            print("✅ Login successful")
            print(f"Access token: {access_token[:30]}..." if access_token else "❌ No access token")
            print(f"Refresh token: {refresh_token[:30]}..." if refresh_token else "❌ No refresh token")
            
            if access_token and refresh_token:
                # Test 2: Refresh với refresh token
                print("\n2. Testing refresh with refresh token...")
                headers = {'Authorization': f'Bearer {refresh_token}'}
                refresh_response = requests.post(REFRESH_URL, headers=headers)
                print(f"Refresh Status: {refresh_response.status_code}")
                print(f"Response: {refresh_response.text}")
                
                if refresh_response.status_code == 200:
                    print("✅ Refresh successful!")
                else:
                    print("❌ Refresh failed")
                    
                # Test 3: Refresh với access token (sẽ fail)
                print("\n3. Testing refresh with access token (should fail)...")
                headers = {'Authorization': f'Bearer {access_token}'}
                wrong_refresh_response = requests.post(REFRESH_URL, headers=headers)
                print(f"Wrong Refresh Status: {wrong_refresh_response.status_code}")
                print(f"Response: {wrong_refresh_response.text}")
                
                if wrong_refresh_response.status_code == 401:
                    print("✅ Correctly rejected access token")
                else:
                    print("❌ Should have rejected access token")
        else:
            print(f"❌ Login failed: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Is it running?")
        print("   Start server with: python app.py")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main() 