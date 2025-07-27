#!/usr/bin/env python3
"""
Test script cho việc insert Milvus trong crawl process
"""

import os
import json
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_auth_token():
    """Lấy JWT token"""
    login_data = {
        "username": "user",
        "password": "user123"
    }
    
    response = requests.post("http://localhost:5000/auth/login", json=login_data)
    
    if response.status_code == 200:
        return response.json().get('access_token')
    else:
        print(f"❌ Login failed: {response.text}")
        return None

def test_crawl_with_milvus():
    """Test crawl với Milvus integration"""
    print("🕷️ Testing crawl with Milvus integration...")
    
    token = get_auth_token()
    if not token:
        return False
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test crawl với website đơn giản
    crawl_data = {
        "link": "https://en.wikipedia.org/wiki/Artificial_intelligence",
        "crawl_tool": "firecrawl"
    }
    
    try:
        print("📥 Starting crawl...")
        response = requests.post(
            "http://localhost:5000/user/crawls",
            json=crawl_data,
            headers=headers
        )
        
        print(f"📡 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Crawl successful!")
            print(f"📊 Results:")
            print(f"  - Crawl ID: {result.get('crawl_id')}")
            print(f"  - Document ID: {result.get('document_id')}")
            print(f"  - Content length: {result.get('content_length')}")
            print(f"  - Chunks processed: {result.get('chunks_processed')}")
            
            milvus_info = result.get('milvus_inserts', {})
            print(f"  - Milvus inserts:")
            print(f"    ✅ Successful: {milvus_info.get('successful', 0)}")
            print(f"    ❌ Failed: {milvus_info.get('failed', 0)}")
            print(f"    📝 Total: {milvus_info.get('total', 0)}")
            
            return True
        else:
            print(f"❌ Crawl failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

def test_retry_failed_inserts():
    """Test retry failed Milvus inserts"""
    print("\n🔄 Testing retry failed Milvus inserts...")
    
    token = get_auth_token()
    if not token:
        return False
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Lấy danh sách documents
    try:
        response = requests.get(
            "http://localhost:5000/user/documents",
            headers=headers
        )
        
        if response.status_code == 200:
            documents = response.json().get('documents', [])
            if documents:
                # Test retry với document đầu tiên
                document_id = documents[0]['id']
                print(f"🔄 Retrying failed inserts for document {document_id}...")
                
                retry_response = requests.post(
                    f"http://localhost:5000/user/documents/{document_id}/retry-milvus",
                    headers=headers
                )
                
                if retry_response.status_code == 200:
                    result = retry_response.json()
                    print("✅ Retry successful!")
                    print(f"📊 Retry results: {result.get('retry_results')}")
                    return True
                else:
                    print(f"❌ Retry failed: {retry_response.text}")
                    return False
            else:
                print("⚠️ No documents found")
                return False
        else:
            print(f"❌ Failed to get documents: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Retry test error: {e}")
        return False

def test_search_after_insert():
    """Test search sau khi insert"""
    print("\n🔍 Testing search after insert...")
    
    token = get_auth_token()
    if not token:
        return False
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test search
    search_data = {
        "query": "artificial intelligence",
        "top_k": 5
    }
    
    try:
        response = requests.post(
            "http://localhost:5000/user/search",
            json=search_data,
            headers=headers
        )
        
        print(f"📡 Search Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Search successful!")
            print(f"📊 Total results: {result.get('total_results', 0)}")
            
            results = result.get('results', [])
            for i, res in enumerate(results):
                print(f"  {i+1}. Score: {res.get('similarity_score', 0):.4f}")
                print(f"     Document: {res.get('document_title', 'N/A')}")
                print(f"     Content: {res.get('content', '')[:100]}...")
            
            return len(results) > 0
        else:
            print(f"❌ Search failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Search test error: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Milvus Insert Test Suite")
    print("="*60)
    
    tests = [
        ("Crawl with Milvus", test_crawl_with_milvus),
        ("Retry Failed Inserts", test_retry_failed_inserts),
        ("Search After Insert", test_search_after_insert)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print(f"\n{'='*60}")
    print("📋 TEST SUMMARY")
    print("="*60)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS")
    print("="*60)
    
    if not results.get("Crawl with Milvus", False):
        print("• Check if Flask server is running")
        print("• Verify Milvus connection")
        print("• Check embedding model configuration")
    
    if not results.get("Search After Insert", False):
        print("• Verify vectors were inserted into Milvus")
        print("• Check search API implementation")
        print("• Verify collection is loaded")

if __name__ == "__main__":
    main() 