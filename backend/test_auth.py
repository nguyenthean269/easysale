#!/usr/bin/env python3
"""
Test script cho authentication và JWT token
"""

import requests
import json

# Cấu hình
BASE_URL = "http://localhost:5000"
LOGIN_URL = f"{BASE_URL}/auth/login"
PROFILE_URL = f"{BASE_URL}/user/profile"
CRAWLS_URL = f"{BASE_URL}/user/crawls"

def test_login(username, password):
    """Test đăng nhập"""
    print(f"🔐 Testing login for user: {username}")
    
    login_data = {
        "username": username,
        "password": password
    }
    
    try:
        response = requests.post(LOGIN_URL, json=login_data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token')
            print(f"✅ Login successful")
            print(f"Token: {token[:20]}...{token[-20:] if len(token) > 40 else ''}")
            return token
        else:
            print(f"❌ Login failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error during login: {str(e)}")
        return None

def test_profile_with_token(token):
    """Test profile endpoint với token"""
    print(f"\n👤 Testing profile endpoint...")
    
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    try:
        response = requests.get(PROFILE_URL, headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Profile access successful")
            return True
        else:
            print(f"❌ Profile access failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error during profile test: {str(e)}")
        return False

def test_crawls_with_token(token):
    """Test crawls endpoint với token"""
    print(f"\n🕷️ Testing crawls endpoint...")
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    data = {
        'link': 'https://example.com',
        'crawl_tool': 'firecrawl'
    }
    
    try:
        # Test GET crawls
        response = requests.get(CRAWLS_URL, headers=headers)
        print(f"GET Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ GET crawls successful")
        else:
            print(f"❌ GET crawls failed: {response.text}")
        
        # Test POST crawls
        response = requests.post(CRAWLS_URL, json=data, headers=headers)
        print(f"POST Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ POST crawls successful")
            return True
        else:
            print(f"❌ POST crawls failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error during crawls test: {str(e)}")
        return False

def test_without_token():
    """Test endpoint không có token"""
    print(f"\n🚫 Testing without token...")
    
    try:
        response = requests.get(PROFILE_URL)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 401:
            print("✅ Correctly rejected without token")
            return True
        else:
            print(f"❌ Unexpected response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error during no-token test: {str(e)}")
        return False

def test_invalid_token():
    """Test với token không hợp lệ"""
    print(f"\n❌ Testing with invalid token...")
    
    headers = {
        'Authorization': 'Bearer invalid_token_here'
    }
    
    try:
        response = requests.get(PROFILE_URL, headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 401:
            print("✅ Correctly rejected invalid token")
            return True
        else:
            print(f"❌ Unexpected response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error during invalid token test: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🧪 Testing Authentication and JWT")
    print("=" * 50)
    
    # Test 1: Login với user thường
    print("\n1. Testing regular user login...")
    token = test_login('user', 'user123')
    
    if token:
        # Test 2: Profile với token hợp lệ
        test_profile_with_token(token)
        
        # Test 3: Crawls với token hợp lệ
        test_crawls_with_token(token)
    
    # Test 4: Login với admin
    print("\n" + "=" * 50)
    print("\n2. Testing admin login...")
    admin_token = test_login('admin', 'admin123')
    
    if admin_token:
        test_profile_with_token(admin_token)
        test_crawls_with_token(admin_token)
    
    # Test 5: Không có token
    print("\n" + "=" * 50)
    print("\n3. Testing without token...")
    test_without_token()
    
    # Test 6: Token không hợp lệ
    print("\n" + "=" * 50)
    print("\n4. Testing with invalid token...")
    test_invalid_token()
    
    print("\n" + "=" * 50)
    print("✅ Authentication tests completed!")

if __name__ == "__main__":
    main() 