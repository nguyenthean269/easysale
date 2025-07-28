#!/usr/bin/env python3
import requests
import json

BASE_URL = "http://localhost:5000"

def test_refresh_with_validation():
    print("🔄 Testing refresh token with validation...")
    
    # 1. Login để lấy tokens
    login_data = {"username": "user", "password": "user123"}
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    
    if response.status_code == 200:
        data = response.json()
        access_token = data.get('access_token')
        refresh_token = data.get('refresh_token')
        
        print("✅ Login successful")
        print(f"Access token: {access_token[:30]}..." if access_token else "❌ No access token")
        print(f"Refresh token: {refresh_token[:30]}..." if refresh_token else "❌ No refresh token")
        
        if access_token and refresh_token:
            # 2. Test refresh với access token (sẽ fail)
            print("\n🧪 Testing refresh with ACCESS token (should fail)...")
            headers = {'Authorization': f'Bearer {access_token}'}
            wrong_response = requests.post(f"{BASE_URL}/auth/refresh", headers=headers)
            print(f"Status: {wrong_response.status_code}")
            print(f"Response: {wrong_response.text}")
            
            if wrong_response.status_code == 401:
                print("✅ Correctly rejected access token")
            else:
                print("❌ Should have rejected access token")
            
            # 3. Test refresh với refresh token (sẽ success)
            print("\n🧪 Testing refresh with REFRESH token (should succeed)...")
            headers = {'Authorization': f'Bearer {refresh_token}'}
            correct_response = requests.post(f"{BASE_URL}/auth/refresh", headers=headers)
            print(f"Status: {correct_response.status_code}")
            print(f"Response: {correct_response.text}")
            
            if correct_response.status_code == 200:
                print("✅ Refresh successful!")
                refresh_data = correct_response.json()
                new_access_token = refresh_data.get('access_token')
                if new_access_token:
                    print(f"New access token: {new_access_token[:30]}...")
            else:
                print("❌ Refresh failed")
        else:
            print("❌ Missing tokens")
    else:
        print(f"❌ Login failed: {response.text}")

if __name__ == "__main__":
    test_refresh_with_validation() 