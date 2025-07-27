#!/usr/bin/env python3
"""
Test script for vector search functionality
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:5000"
USERNAME = "user"
PASSWORD = "user123"

def get_auth_token():
    """Lấy JWT token để authenticate"""
    login_data = {
        "username": USERNAME,
        "password": PASSWORD
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    
    if response.status_code == 200:
        return response.json().get('access_token')
    else:
        print(f"❌ Login failed: {response.text}")
        return None

def test_crawl_and_vector_search():
    """Test crawl và vector search"""
    token = get_auth_token()
    if not token:
        return False
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print("🚀 Testing crawl and vector search...")
    
    # 1. Tạo crawl request
    crawl_data = {
        "link": "https://en.wikipedia.org/wiki/Artificial_intelligence",
        "crawl_tool": "firecrawl"
    }
    
    print("📥 Creating crawl request...")
    response = requests.post(f"{BASE_URL}/user/crawls", json=crawl_data, headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Crawl failed: {response.text}")
        return False
    
    crawl_result = response.json()
    print(f"✅ Crawl completed: {crawl_result['message']}")
    
    # Đợi một chút để đảm bảo vector processing hoàn tất
    time.sleep(2)
    
    # 2. Test vector search
    search_data = {
        "query": "machine learning algorithms",
        "top_k": 3
    }
    
    print("🔍 Testing vector search...")
    response = requests.post(f"{BASE_URL}/user/search", json=search_data, headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Search failed: {response.text}")
        return False
    
    search_result = response.json()
    print(f"✅ Search completed: Found {search_result['total_results']} results")
    
    # Hiển thị kết quả
    for i, result in enumerate(search_result['results'], 1):
        print(f"\n📄 Result {i}:")
        print(f"  Document: {result['document_title']}")
        print(f"  Chunk Index: {result['chunk_index']}")
        print(f"  Similarity Score: {result['similarity_score']:.4f}")
        print(f"  Content Preview: {result['content'][:200]}...")
    
    return True

def test_search_only():
    """Test chỉ vector search (không crawl)"""
    token = get_auth_token()
    if not token:
        return False
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print("🔍 Testing vector search only...")
    
    # Test với các query khác nhau
    test_queries = [
        "neural networks",
        "deep learning",
        "natural language processing",
        "computer vision"
    ]
    
    for query in test_queries:
        search_data = {
            "query": query,
            "top_k": 2
        }
        
        print(f"\n🔍 Searching for: '{query}'")
        response = requests.post(f"{BASE_URL}/user/search", json=search_data, headers=headers)
        
        if response.status_code == 200:
            search_result = response.json()
            print(f"✅ Found {search_result['total_results']} results")
            
            for i, result in enumerate(search_result['results'], 1):
                print(f"  {i}. Score: {result['similarity_score']:.4f} - {result['content'][:100]}...")
        else:
            print(f"❌ Search failed: {response.text}")
    
    return True

def test_error_handling():
    """Test error handling"""
    token = get_auth_token()
    if not token:
        return False
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print("⚠️ Testing error handling...")
    
    # Test với query rỗng
    search_data = {"query": ""}
    response = requests.post(f"{BASE_URL}/user/search", json=search_data, headers=headers)
    print(f"Empty query response: {response.status_code} - {response.text}")
    
    # Test với query quá dài
    long_query = "a" * 10000
    search_data = {"query": long_query}
    response = requests.post(f"{BASE_URL}/user/search", json=search_data, headers=headers)
    print(f"Long query response: {response.status_code} - {response.text}")
    
    return True

if __name__ == "__main__":
    print("🧪 Starting vector search tests...")
    
    # Test 1: Crawl và search
    print("\n" + "="*50)
    print("TEST 1: Crawl and Vector Search")
    print("="*50)
    test_crawl_and_vector_search()
    
    # Test 2: Search only
    print("\n" + "="*50)
    print("TEST 2: Vector Search Only")
    print("="*50)
    test_search_only()
    
    # Test 3: Error handling
    print("\n" + "="*50)
    print("TEST 3: Error Handling")
    print("="*50)
    test_error_handling()
    
    print("\n🎉 All tests completed!") 