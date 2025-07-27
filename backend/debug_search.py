#!/usr/bin/env python3
"""
Debug script cho vector search - Phiên bản chi tiết
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

def test_milvus_connection():
    """Test kết nối Milvus"""
    print("🔌 Testing Milvus connection...")
    
    try:
        host = os.getenv('MILVUS_HOST', 'localhost')
        port = os.getenv('MILVUS_PORT', '19530')
        
        connections.connect("default", host=host, port=port)
        print("✅ Milvus connection OK")
        
        # Kiểm tra collections
        collections = utility.list_collections()
        print(f"📚 Collections: {collections}")
        
        return True
    except Exception as e:
        print(f"❌ Milvus connection failed: {e}")
        return False

def check_collection_data():
    """Kiểm tra dữ liệu trong collection"""
    print("\n📊 Checking collection data...")
    
    try:
        collection_name = os.getenv('MILVUS_COLLECTION_NAME', 'document_chunks')
        
        if not utility.has_collection(collection_name):
            print(f"❌ Collection '{collection_name}' does not exist")
            return False
        
        collection = Collection(collection_name)
        collection.load()
        
        # Đếm số lượng entities
        num_entities = collection.num_entities
        print(f"📈 Total entities in collection: {num_entities}")
        
        if num_entities == 0:
            print("❌ Collection is empty!")
            return False
        
        # Lấy sample data
        results = collection.query(
            expr="id != ''",
            output_fields=["id", "document_id", "chunk_index"],
            limit=5
        )
        
        print(f"📋 Sample data (first 5 records):")
        for i, record in enumerate(results):
            print(f"  {i+1}. ID: {record['id']}, DocID: {record['document_id']}, Chunk: {record['chunk_index']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking collection: {e}")
        return False

def check_database_details():
    """Kiểm tra chi tiết database"""
    print("\n🗄️ Checking database details...")
    
    try:
        # Import database models
        import sys
        sys.path.append('.')
        
        from app import app
        from models import DocumentChunk, Document, db
        
        with app.app_context():
            # Đếm documents
            total_documents = Document.query.count()
            print(f"📄 Total documents: {total_documents}")
            
            # Đếm chunks
            total_chunks = DocumentChunk.query.count()
            print(f"📝 Total chunks: {total_chunks}")
            
            # Chunks có milvus_id
            chunks_with_milvus = DocumentChunk.query.filter(DocumentChunk.milvus_id.isnot(None)).count()
            print(f"🔗 Chunks with milvus_id: {chunks_with_milvus}")
            
            # Chunks không có milvus_id
            chunks_without_milvus = total_chunks - chunks_with_milvus
            print(f"⚠️ Chunks without milvus_id: {chunks_without_milvus}")
            
            if total_documents == 0:
                print("❌ No documents in database!")
                return False
            
            # Lấy document đầu tiên
            first_document = Document.query.first()
            print(f"\n📄 First document:")
            print(f"  ID: {first_document.id}")
            print(f"  Title: {first_document.title}")
            print(f"  Source: {first_document.source_path}")
            print(f"  Created: {first_document.created_at}")
            
            # Lấy chunks của document đầu tiên
            first_doc_chunks = DocumentChunk.query.filter_by(document_id=first_document.id).all()
            print(f"  📝 Chunks in first document: {len(first_doc_chunks)}")
            
            # Hiển thị chunk đầu tiên
            if first_doc_chunks:
                first_chunk = first_doc_chunks[0]
                print(f"\n📝 First chunk:")
                print(f"  ID: {first_chunk.id}")
                print(f"  Document ID: {first_chunk.document_id}")
                print(f"  Chunk Index: {first_chunk.chunk_index}")
                print(f"  Milvus ID: {first_chunk.milvus_id}")
                print(f"  Content preview: {first_chunk.content[:200]}...")
            
            # Thống kê theo document
            print(f"\n📊 Statistics by document:")
            documents = Document.query.all()
            for doc in documents[:5]:  # Chỉ hiển thị 5 document đầu
                doc_chunks = DocumentChunk.query.filter_by(document_id=doc.id).count()
                doc_chunks_with_milvus = DocumentChunk.query.filter(
                    DocumentChunk.document_id == doc.id,
                    DocumentChunk.milvus_id.isnot(None)
                ).count()
                print(f"  Document {doc.id} ({doc.title[:30]}...): {doc_chunks} chunks, {doc_chunks_with_milvus} with milvus_id")
            
            return total_documents > 0
            
    except Exception as e:
        print(f"❌ Database check error: {e}")
        return False

def check_milvus_details():
    """Kiểm tra chi tiết Milvus collection"""
    print("\n🔍 Checking Milvus collection details...")
    
    try:
        collection_name = os.getenv('MILVUS_COLLECTION_NAME', 'document_chunks')
        
        if not utility.has_collection(collection_name):
            print(f"❌ Collection '{collection_name}' does not exist")
            return False
        
        collection = Collection(collection_name)
        collection.load()
        
        # Thông tin collection
        print(f"📚 Collection: {collection_name}")
        print(f"📈 Total entities: {collection.num_entities}")
        
        # Schema info
        schema = collection.schema
        print(f"📋 Schema fields:")
        for field in schema.fields:
            print(f"  - {field.name}: {field.dtype} (dim: {field.params.get('dim', 'N/A')})")
        
        # Lấy entry đầu tiên
        if collection.num_entities > 0:
            first_entry = collection.query(
                expr="id != ''",
                output_fields=["id", "document_id", "chunk_index"],
                limit=1
            )
            
            if first_entry:
                print(f"\n🔍 First entry in Milvus:")
                entry = first_entry[0]
                print(f"  ID: {entry['id']}")
                print(f"  Document ID: {entry['document_id']}")
                print(f"  Chunk Index: {entry['chunk_index']}")
        
        # Thống kê theo document_id
        print(f"\n📊 Statistics by document_id in Milvus:")
        try:
            # Lấy tất cả document_ids
            all_entries = collection.query(
                expr="document_id >= 0",
                output_fields=["document_id"],
                limit=1000
            )
            
            if all_entries:
                doc_counts = {}
                for entry in all_entries:
                    doc_id = entry['document_id']
                    doc_counts[doc_id] = doc_counts.get(doc_id, 0) + 1
                
                for doc_id, count in sorted(doc_counts.items())[:5]:
                    print(f"  Document {doc_id}: {count} entries")
        except Exception as e:
            print(f"  ⚠️ Could not get document statistics: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Milvus details check error: {e}")
        return False

def test_embedding_model():
    """Test embedding model"""
    print("\n🤖 Testing embedding model...")
    
    try:
        model_name = os.getenv('EMBEDDING_MODEL', 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
        model = SentenceTransformer(model_name)
        
        # Test embedding
        test_text = "This is a test sentence"
        embedding = model.encode(test_text)
        
        print(f"✅ Embedding model loaded: {model_name}")
        print(f"📏 Embedding dimension: {len(embedding)}")
        print(f"📊 Sample embedding (first 5 values): {embedding[:5]}")
        
        return model
    except Exception as e:
        print(f"❌ Embedding model error: {e}")
        return None

def test_vector_search():
    """Test vector search trực tiếp"""
    print("\n🔍 Testing vector search directly...")
    
    try:
        collection_name = os.getenv('MILVUS_COLLECTION_NAME', 'document_chunks')
        collection = Collection(collection_name)
        collection.load()
        
        # Tạo test query
        model_name = os.getenv('EMBEDDING_MODEL', 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
        model = SentenceTransformer(model_name)
        
        test_query = "machine learning"
        query_embedding = model.encode(test_query).tolist()
        
        print(f"🔍 Searching for: '{test_query}'")
        
        # Thực hiện search
        search_params = {
            "metric_type": "COSINE",
            "params": {"nprobe": 10}
        }
        
        results = collection.search(
            data=[query_embedding],
            anns_field="embedding",
            param=search_params,
            limit=5,
            output_fields=["document_id", "chunk_index"]
        )
        
        print(f"📊 Search results: {len(results[0])} hits")
        
        for i, hit in enumerate(results[0]):
            print(f"  {i+1}. ID: {hit.id}, Score: {hit.score:.4f}, DocID: {hit.entity.get('document_id')}, Chunk: {hit.entity.get('chunk_index')}")
        
        return len(results[0]) > 0
        
    except Exception as e:
        print(f"❌ Vector search error: {e}")
        return False

def test_api_search():
    """Test search API"""
    print("\n🌐 Testing search API...")
    
    token = get_auth_token()
    if not token:
        print("❌ Cannot get auth token")
        return False
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test search
    search_data = {
        "query": "machine learning",
        "top_k": 5
    }
    
    try:
        response = requests.post(
            "http://localhost:5000/user/search",
            json=search_data,
            headers=headers
        )
        
        print(f"📡 API Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ API Search successful")
            print(f"📊 Total results: {result.get('total_results', 0)}")
            
            results = result.get('results', [])
            for i, res in enumerate(results):
                print(f"  {i+1}. Score: {res.get('similarity_score', 0):.4f}")
                print(f"     Document: {res.get('document_title', 'N/A')}")
                print(f"     Content: {res.get('content', '')[:100]}...")
            
            return len(results) > 0
        else:
            print(f"❌ API Search failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ API test error: {e}")
        return False

def debug_crawl_process():
    """Debug crawl process"""
    print("\n🕷️ Debugging crawl process...")
    
    token = get_auth_token()
    if not token:
        return False
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test crawl
    crawl_data = {
        "link": "https://en.wikipedia.org/wiki/Artificial_intelligence",
        "crawl_tool": "firecrawl"
    }
    
    try:
        print("📥 Testing crawl...")
        response = requests.post(
            "http://localhost:5000/user/crawls",
            json=crawl_data,
            headers=headers
        )
        
        print(f"📡 Crawl Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Crawl successful")
            print(f"📊 Content length: {result.get('content_length', 0)}")
            return True
        else:
            print(f"❌ Crawl failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Crawl test error: {e}")
        return False

def main():
    """Main debug function"""
    print("🔍 Vector Search Debug Tool - Detailed Version")
    print("="*70)
    
    # Test từng component
    tests = [
        ("Milvus Connection", test_milvus_connection),
        ("Database Details", check_database_details),
        ("Milvus Details", check_milvus_details),
        ("Collection Data", check_collection_data),
        ("Embedding Model", test_embedding_model),
        ("Vector Search", test_vector_search),
        ("API Search", test_api_search),
        ("Crawl Process", debug_crawl_process)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*25} {test_name} {'='*25}")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print(f"\n{'='*70}")
    print("📋 DEBUG SUMMARY")
    print("="*70)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS")
    print("="*70)
    
    if not results.get("Milvus Connection", False):
        print("• Check Milvus server is running")
        print("• Verify MILVUS_HOST and MILVUS_PORT in .env")
    
    if not results.get("Database Details", False):
        print("• No documents in database - need to crawl documents first")
        print("• Run crawl process to create documents and chunks")
    
    if not results.get("Milvus Details", False):
        print("• Collection is empty - vectors not inserted properly")
        print("• Check vector insertion process")
    
    if not results.get("Vector Search", False):
        print("• Vector search not working - check embedding model")
        print("• Verify collection schema and index")
    
    if not results.get("API Search", False):
        print("• API search failing - check Flask server and routes")
        print("• Verify authentication and permissions")

if __name__ == "__main__":
    main() 