#!/usr/bin/env python3
"""
Test script cho vector search tiếng Việt
"""

import os
import json
import requests
from dotenv import load_dotenv
from pymilvus import connections, Collection, utility
from sentence_transformers import SentenceTransformer

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

def test_vietnamese_embedding():
    """Test embedding với tiếng Việt"""
    print("🇻🇳 Testing Vietnamese embedding...")
    
    try:
        model_name = os.getenv('EMBEDDING_MODEL', 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
        model = SentenceTransformer(model_name)
        
        # Test sentences tiếng Việt
        vietnamese_texts = [
            "Học máy là một nhánh của trí tuệ nhân tạo",
            "Thuật toán học máy rất mạnh mẽ",
            "Xử lý ngôn ngữ tự nhiên",
            "Trí tuệ nhân tạo và machine learning",
            "Deep learning và neural networks"
        ]
        
        print(f"✅ Model loaded: {model_name}")
        
        for i, text in enumerate(vietnamese_texts, 1):
            embedding = model.encode(text)
            print(f"  {i}. '{text[:50]}...' -> Dimension: {len(embedding)}")
        
        return model
    except Exception as e:
        print(f"❌ Vietnamese embedding failed: {e}")
        return None

def test_vietnamese_similarity():
    """Test similarity giữa tiếng Việt và tiếng Anh"""
    print("\n🔍 Testing Vietnamese-English similarity...")
    
    try:
        model_name = os.getenv('EMBEDDING_MODEL', 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
        model = SentenceTransformer(model_name)
        
        # Test pairs
        test_pairs = [
            ("học máy", "machine learning"),
            ("trí tuệ nhân tạo", "artificial intelligence"),
            ("xử lý ngôn ngữ tự nhiên", "natural language processing"),
            ("thuật toán", "algorithm"),
            ("dữ liệu", "data")
        ]
        
        from sklearn.metrics.pairwise import cosine_similarity
        import numpy as np
        
        print("📊 Similarity scores:")
        for vi_text, en_text in test_pairs:
            vi_embedding = model.encode(vi_text).reshape(1, -1)
            en_embedding = model.encode(en_text).reshape(1, -1)
            
            similarity = cosine_similarity(vi_embedding, en_embedding)[0][0]
            print(f"  '{vi_text}' vs '{en_text}': {similarity:.3f}")
        
        return True
    except Exception as e:
        print(f"❌ Similarity test failed: {e}")
        return False

def test_vietnamese_crawl():
    """Test crawl website tiếng Việt"""
    print("\n🕷️ Testing Vietnamese website crawl...")
    
    token = get_auth_token()
    if not token:
        return False
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test với website tiếng Việt
    vietnamese_sites = [
        "https://vi.wikipedia.org/wiki/Học_máy",
        "https://vi.wikipedia.org/wiki/Trí_tuệ_nhân_tạo",
        "https://vi.wikipedia.org/wiki/Xử_lý_ngôn_ngữ_tự_nhiên"
    ]
    
    for site in vietnamese_sites:
        try:
            print(f"📥 Crawling: {site}")
            response = requests.post(
                "http://localhost:5000/user/crawls",
                json={"link": site, "crawl_tool": "firecrawl"},
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Success: {result.get('content_length', 0)} characters")
            else:
                print(f"❌ Failed: {response.text}")
                
        except Exception as e:
            print(f"❌ Error crawling {site}: {e}")
    
    return True

def test_vietnamese_search():
    """Test search với query tiếng Việt"""
    print("\n🔍 Testing Vietnamese search...")
    
    token = get_auth_token()
    if not token:
        return False
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test queries tiếng Việt
    vietnamese_queries = [
        "học máy",
        "trí tuệ nhân tạo", 
        "xử lý ngôn ngữ tự nhiên",
        "thuật toán",
        "deep learning",
        "neural networks"
    ]
    
    for query in vietnamese_queries:
        try:
            print(f"\n🔍 Searching for: '{query}'")
            
            search_data = {
                "query": query,
                "top_k": 3
            }
            
            response = requests.post(
                "http://localhost:5000/user/search",
                json=search_data,
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Found {result.get('total_results', 0)} results")
                
                results = result.get('results', [])
                for i, res in enumerate(results, 1):
                    score = res.get('similarity_score', 0)
                    content = res.get('content', '')[:100]
                    print(f"  {i}. Score: {score:.3f} - {content}...")
            else:
                print(f"❌ Search failed: {response.text}")
                
        except Exception as e:
            print(f"❌ Error searching '{query}': {e}")
    
    return True

def test_mixed_language_search():
    """Test search với cả tiếng Việt và tiếng Anh"""
    print("\n🌍 Testing mixed language search...")
    
    token = get_auth_token()
    if not token:
        return False
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test với query hỗn hợp
    mixed_queries = [
        "machine learning và học máy",
        "AI trí tuệ nhân tạo",
        "NLP xử lý ngôn ngữ",
        "deep learning học sâu",
        "neural networks mạng nơ-ron"
    ]
    
    for query in mixed_queries:
        try:
            print(f"\n🔍 Mixed query: '{query}'")
            
            search_data = {
                "query": query,
                "top_k": 3
            }
            
            response = requests.post(
                "http://localhost:5000/user/search",
                json=search_data,
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Found {result.get('total_results', 0)} results")
                
                results = result.get('results', [])
                for i, res in enumerate(results, 1):
                    score = res.get('similarity_score', 0)
                    content = res.get('content', '')[:100]
                    print(f"  {i}. Score: {score:.3f} - {content}...")
            else:
                print(f"❌ Search failed: {response.text}")
                
        except Exception as e:
            print(f"❌ Error searching '{query}': {e}")
    
    return True

def main():
    """Main test function"""
    print("🇻🇳 Vietnamese Vector Search Test")
    print("="*60)
    
    # Test từng component
    tests = [
        ("Vietnamese Embedding", test_vietnamese_embedding),
        ("Vietnamese Similarity", test_vietnamese_similarity),
        ("Vietnamese Crawl", test_vietnamese_crawl),
        ("Vietnamese Search", test_vietnamese_search),
        ("Mixed Language Search", test_mixed_language_search)
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
    print("📋 VIETNAMESE TEST SUMMARY")
    print("="*60)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    # Recommendations
    print(f"\n💡 VIETNAMESE OPTIMIZATION TIPS")
    print("="*60)
    
    print("1. 🎯 Use Vietnamese queries:")
    print("   - 'học máy' instead of 'machine learning'")
    print("   - 'trí tuệ nhân tạo' instead of 'artificial intelligence'")
    
    print("\n2. 🌍 Mixed language support:")
    print("   - Model supports both Vietnamese and English")
    print("   - Can search with mixed queries")
    
    print("\n3. 📚 Vietnamese content sources:")
    print("   - Wikipedia tiếng Việt")
    print("   - Vietnamese tech blogs")
    print("   - Vietnamese documentation")

if __name__ == "__main__":
    main() 