#!/usr/bin/env python3
"""
Test script cho refresh token
"""

import requests
import json
import time

# Cấu hình
BASE_URL = "http://localhost:5000"
LOGIN_URL = f"{BASE_URL}/auth/login"
REFRESH_URL = f"{BASE_URL}/auth/refresh"
PROFILE_URL = f"{BASE_URL}/user/profile"
LOGOUT_URL = f"{BASE_URL}/auth/logout"

def test_login_and_refresh():
    """Test đăng nhập và refresh token"""
    print("🔐 Testing login and refresh token...")
    
    login_data = {
        "username": "user",
        "password": "user123"
    }
    
    try:
        # Bước 1: Đăng nhập
        print("\n1. Login...")
        response = requests.post(LOGIN_URL, json=login_data)
        print(f"Login Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            access_token = data.get('access_token')
            refresh_token = data.get('refresh_token')
            
            print(f"✅ Login successful")
            print(f"Access Token: {access_token[:30]}...{access_token[-30:] if len(access_token) > 60 else ''}")
            print(f"Refresh Token: {refresh_token[:30]}...{refresh_token[-30:] if len(refresh_token) > 60 else ''}")
            
            # Bước 2: Test access token
            print("\n2. Testing access token...")
            headers = {'Authorization': f'Bearer {access_token}'}
            profile_response = requests.get(PROFILE_URL, headers=headers)
            print(f"Profile Status: {profile_response.status_code}")
            
            if profile_response.status_code == 200:
                print("✅ Access token works")
            else:
                print(f"❌ Access token failed: {profile_response.text}")
            
            # Bước 3: Test refresh token
            print("\n3. Testing refresh token...")
            refresh_headers = {'Authorization': f'Bearer {refresh_token}'}
            refresh_response = requests.post(REFRESH_URL, headers=refresh_headers)
            print(f"Refresh Status: {refresh_response.status_code}")
            
            if refresh_response.status_code == 200:
                refresh_data = refresh_response.json()
                new_access_token = refresh_data.get('access_token')
                print("✅ Refresh token works")
                print(f"New Access Token: {new_access_token[:30]}...{new_access_token[-30:] if len(new_access_token) > 60 else ''}")
                
                # Bước 4: Test new access token
                print("\n4. Testing new access token...")
                new_headers = {'Authorization': f'Bearer {new_access_token}'}
                new_profile_response = requests.get(PROFILE_URL, headers=new_headers)
                print(f"New Profile Status: {new_profile_response.status_code}")
                
                if new_profile_response.status_code == 200:
                    print("✅ New access token works")
                else:
                    print(f"❌ New access token failed: {new_profile_response.text}")
                    
            else:
                print(f"❌ Refresh token failed: {refresh_response.text}")
                
            # Bước 5: Test logout
            print("\n5. Testing logout...")
            logout_response = requests.post(LOGOUT_URL, headers=headers)
            print(f"Logout Status: {logout_response.status_code}")
            
            if logout_response.status_code == 200:
                print("✅ Logout successful")
            else:
                print(f"❌ Logout failed: {logout_response.text}")
                
        else:
            print(f"❌ Login failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error during test: {str(e)}")

def test_invalid_refresh():
    """Test với refresh token không hợp lệ"""
    print("\n🔍 Testing invalid refresh token...")
    
    try:
        invalid_refresh_token = "invalid.refresh.token"
        headers = {'Authorization': f'Bearer {invalid_refresh_token}'}
        response = requests.post(REFRESH_URL, headers=headers)
        print(f"Invalid Refresh Status: {response.status_code}")
        
        if response.status_code == 401:
            print("✅ Invalid refresh token correctly rejected")
        else:
            print(f"❌ Unexpected response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error during invalid refresh test: {str(e)}")

def main():
    """Main test function"""
    print("🔄 Refresh Token Test Tool")
    print("=" * 50)
    
    test_login_and_refresh()
    test_invalid_refresh()
    
    print("\n" + "=" * 50)
    print("✅ Test completed!")

if __name__ == "__main__":
    main() 