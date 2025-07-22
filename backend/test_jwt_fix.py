#!/usr/bin/env python3
"""
Test script để kiểm tra JWT đã được sửa
"""

import requests
import json

# Cấu hình
BASE_URL = "http://localhost:5000"
LOGIN_URL = f"{BASE_URL}/auth/login"
CRAWLS_URL = f"{BASE_URL}/user/crawls"
PROFILE_URL = f"{BASE_URL}/user/profile"

def test_login_and_token():
    """Test đăng nhập và lấy token"""
    print("🔐 Testing login and token generation...")
    
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
            print(f"✅ Login successful")
            print(f"Token: {token[:30]}...{token[-30:] if len(token) > 60 else ''}")
            return token
        else:
            print(f"❌ Login failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error during login: {str(e)}")
        return None

def test_crawl_with_token(token):
    """Test crawl API với token"""
    print(f"\n🕷️ Testing crawl API with token...")
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    data = {
        'link': 'https://example.com',
        'crawl_tool': 'firecrawl'
    }
    
    try:
        response = requests.post(CRAWLS_URL, json=data, headers=headers)
        print(f"Crawl Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Crawl API successful")
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2, ensure_ascii=False)}")
            return True
        else:
            print(f"❌ Crawl API failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error during crawl test: {str(e)}")
        return False

def test_profile_with_token(token):
    """Test profile API với token"""
    print(f"\n👤 Testing profile API with token...")
    
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    try:
        response = requests.get(PROFILE_URL, headers=headers)
        print(f"Profile Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Profile API successful")
            result = response.json()
            print(f"User: {result.get('user', {}).get('username', 'Unknown')}")
            return True
        else:
            print(f"❌ Profile API failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error during profile test: {str(e)}")
        return False

def test_admin_login():
    """Test đăng nhập admin"""
    print(f"\n👑 Testing admin login...")
    
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        response = requests.post(LOGIN_URL, json=login_data)
        print(f"Admin Login Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token')
            print(f"✅ Admin login successful")
            return token
        else:
            print(f"❌ Admin login failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error during admin login: {str(e)}")
        return None

def test_admin_crawl(token):
    """Test crawl với admin token"""
    print(f"\n👑 Testing crawl with admin token...")
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    data = {
        'link': 'https://httpbin.org/html',
        'crawl_tool': 'firecrawl'
    }
    
    try:
        response = requests.post(CRAWLS_URL, json=data, headers=headers)
        print(f"Admin Crawl Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Admin crawl successful")
            return True
        else:
            print(f"❌ Admin crawl failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error during admin crawl test: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🧪 Testing JWT Fix")
    print("=" * 50)
    
    # Test 1: User login và crawl
    print("\n1. Testing user login and crawl...")
    token = test_login_and_token()
    
    if token:
        test_crawl_with_token(token)
        test_profile_with_token(token)
    
    # Test 2: Admin login và crawl
    print("\n" + "=" * 50)
    print("\n2. Testing admin login and crawl...")
    admin_token = test_admin_login()
    
    if admin_token:
        test_admin_crawl(admin_token)
    
    print("\n" + "=" * 50)
    print("✅ JWT fix test completed!")

if __name__ == "__main__":
    main() 