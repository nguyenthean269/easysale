#!/usr/bin/env python3
"""
Test script cho các API mới: update crawl content và recrawl
"""

import requests
import json
import time

# Cấu hình
BASE_URL = "http://localhost:5000"
LOGIN_URL = f"{BASE_URL}/auth/login"
CRAWLS_URL = f"{BASE_URL}/user/crawls"

def login():
    """Đăng nhập để lấy token"""
    login_data = {
        "username": "user",
        "password": "user123"
    }
    
    response = requests.post(LOGIN_URL, json=login_data)
    if response.status_code == 200:
        data = response.json()
        return data.get('access_token')
    else:
        print(f"Login failed: {response.status_code} - {response.text}")
        return None

def get_crawls(token):
    """Lấy danh sách crawls"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(CRAWLS_URL, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        return data.get('crawls', [])
    else:
        print(f"Failed to get crawls: {response.status_code} - {response.text}")
        return []

def test_update_crawl_content(token, crawl_id):
    """Test API update crawl content"""
    print(f"\n🧪 Testing update crawl content for crawl ID: {crawl_id}")
    
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # Nội dung mới để test
    new_content = f"""
    Updated content for crawl {crawl_id}
    
    This is a test update to verify that:
    1. Content is updated in the database
    2. Old chunks are deleted from database and Milvus
    3. New chunks are created and inserted into Milvus
    
    The content includes some technical information about:
    - Database operations
    - Vector processing
    - Milvus integration
    - Chunk management
    
    This should generate multiple chunks for testing purposes.
    """
    
    update_data = {"content": new_content}
    
    response = requests.put(f"{CRAWLS_URL}/{crawl_id}", json=update_data, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Update successful!")
        print(f"   Message: {data.get('message')}")
        print(f"   Content length: {data.get('content_length')}")
        print(f"   Chunks processed: {data.get('chunks_processed')}")
        print(f"   Milvus inserts: {data.get('milvus_inserts')}")
        return True
    else:
        print(f"❌ Update failed: {response.status_code} - {response.text}")
        return False

def test_recrawl_content(token, crawl_id):
    """Test API recrawl content"""
    print(f"\n🔄 Testing recrawl content for crawl ID: {crawl_id}")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.post(f"{CRAWLS_URL}/{crawl_id}/recrawl", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Recrawl successful!")
        print(f"   Message: {data.get('message')}")
        print(f"   Link: {data.get('link')}")
        print(f"   Content length: {data.get('content_length')}")
        print(f"   Chunks processed: {data.get('chunks_processed')}")
        print(f"   Milvus inserts: {data.get('milvus_inserts')}")
        return True
    else:
        print(f"❌ Recrawl failed: {response.status_code} - {response.text}")
        return False

def main():
    """Main test function"""
    print("🚀 Starting crawl update and recrawl tests...")
    
    # Đăng nhập
    token = login()
    if not token:
        print("❌ Cannot proceed without authentication token")
        return
    
    print(f"✅ Login successful, token: {token[:20]}...")
    
    # Lấy danh sách crawls
    crawls = get_crawls(token)
    if not crawls:
        print("❌ No crawls found. Please create some crawls first.")
        return
    
    print(f"📋 Found {len(crawls)} crawls")
    
    # Chọn crawl đầu tiên để test
    test_crawl = crawls[0]
    crawl_id = test_crawl['id']
    
    print(f"🎯 Using crawl ID {crawl_id} for testing")
    print(f"   Link: {test_crawl['link']}")
    print(f"   Current content length: {len(test_crawl['content'])}")
    
    # Test 1: Update crawl content
    print("\n" + "="*50)
    print("TEST 1: UPDATE CRAWL CONTENT")
    print("="*50)
    
    success1 = test_update_crawl_content(token, crawl_id)
    
    if success1:
        print("\n⏳ Waiting 2 seconds before next test...")
        time.sleep(2)
        
        # Test 2: Recrawl content
        print("\n" + "="*50)
        print("TEST 2: RECRAWL CONTENT")
        print("="*50)
        
        success2 = test_recrawl_content(token, crawl_id)
        
        if success2:
            print("\n✅ All tests completed successfully!")
        else:
            print("\n❌ Recrawl test failed")
    else:
        print("\n❌ Update test failed, skipping recrawl test")
    
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    print("1. Update crawl content: " + ("✅ PASS" if success1 else "❌ FAIL"))
    print("2. Recrawl content: " + ("✅ PASS" if success1 and success2 else "❌ FAIL"))

if __name__ == "__main__":
    main() 