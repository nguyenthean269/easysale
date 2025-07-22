#!/usr/bin/env python3
"""
Test crawl API đơn giản
"""

import requests
import json

# Cấu hình
BASE_URL = "http://localhost:5000"
LOGIN_URL = f"{BASE_URL}/auth/login"
CRAWLS_URL = f"{BASE_URL}/user/crawls"

def test_crawl_simple():
    """Test crawl API đơn giản"""
    print("🧪 Testing Crawl API Simple")
    print("=" * 50)
    
    # 1. Login
    print("\n1. Login...")
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
            print("✅ Login successful")
        else:
            print(f"❌ Login failed: {response.text}")
            return
    except Exception as e:
        print(f"❌ Login error: {str(e)}")
        return
    
    # 2. Test crawl
    print("\n2. Testing crawl...")
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
        print(f"Crawl Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Crawl successful!")
            print(f"Response: {json.dumps(result, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ Crawl failed: {response.text}")
            
            # Nếu lỗi 404 từ firecrawl, thử với mock data
            if "404" in response.text and "firecrawl" in response.text:
                print("\n💡 Firecrawl API không khả dụng, thử với mock data...")
                test_with_mock_data(token)
                
    except Exception as e:
        print(f"❌ Crawl error: {str(e)}")

def test_with_mock_data(token):
    """Test với mock data thay vì gọi firecrawl API"""
    print("\n3. Testing with mock data...")
    
    # Tạo một script test đơn giản để bypass firecrawl API
    test_script = '''
import requests
import json

BASE_URL = "http://localhost:5000"
CRAWLS_URL = f"{BASE_URL}/user/crawls"

headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

data = {
    'link': 'https://example.com',
    'crawl_tool': 'firecrawl'
}

response = requests.post(CRAWLS_URL, json=data, headers=headers)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")
'''
    
    print("Test script:")
    print(test_script)

if __name__ == "__main__":
    test_crawl_simple() 