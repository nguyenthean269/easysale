#!/usr/bin/env python3
"""
Test script cho API crawl
"""

import requests
import json
import time

# Cấu hình
BASE_URL = "http://localhost:5000"
LOGIN_URL = f"{BASE_URL}/auth/login"
CRAWLS_URL = f"{BASE_URL}/user/crawls"

def login_and_get_token(username, password):
    """Đăng nhập và lấy token"""
    login_data = {
        "username": username,
        "password": password
    }
    
    response = requests.post(LOGIN_URL, json=login_data)
    
    if response.status_code == 200:
        return response.json().get('access_token')
    else:
        print(f"Login failed: {response.text}")
        return None

def test_create_crawl(token, link, crawl_tool='firecrawl'):
    """Test tạo crawl"""
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    data = {
        'link': link,
        'crawl_tool': crawl_tool
    }
    
    print(f"Testing crawl for link: {link}")
    print(f"Using tool: {crawl_tool}")
    
    response = requests.post(CRAWLS_URL, json=data, headers=headers)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    return response

def test_get_crawls(token):
    """Test lấy danh sách crawls"""
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    print("\nTesting get crawls list...")
    
    response = requests.get(CRAWLS_URL, headers=headers)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    return response

def test_get_crawl_detail(token, crawl_id):
    """Test lấy chi tiết crawl"""
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    print(f"\nTesting get crawl detail for ID: {crawl_id}")
    
    response = requests.get(f"{CRAWLS_URL}/{crawl_id}", headers=headers)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    return response

def main():
    """Main test function"""
    print("🧪 Testing Crawl API")
    print("=" * 50)
    
    # Test với user thường
    print("\n1. Testing with regular user...")
    token = login_and_get_token('user', 'user123')
    
    if not token:
        print("❌ Failed to get token for user")
        return
    
    print("✅ Login successful")
    
    # Test tạo crawl
    test_link = "https://example.com"
    response = test_create_crawl(token, test_link, 'firecrawl')
    
    if response.status_code == 200:
        crawl_id = response.json().get('crawl_id')
        
        # Test lấy danh sách crawls
        test_get_crawls(token)
        
        # Test lấy chi tiết crawl
        if crawl_id:
            test_get_crawl_detail(token, crawl_id)
    
    # Test với admin
    print("\n" + "=" * 50)
    print("\n2. Testing with admin...")
    admin_token = login_and_get_token('admin', 'admin123')
    
    if not admin_token:
        print("❌ Failed to get token for admin")
        return
    
    print("✅ Admin login successful")
    
    # Test tạo crawl với admin
    test_create_crawl(admin_token, "https://httpbin.org/html", 'firecrawl')
    
    # Test lấy danh sách crawls (admin sẽ thấy tất cả)
    test_get_crawls(admin_token)

if __name__ == "__main__":
    main() 