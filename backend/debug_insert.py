#!/usr/bin/env python3
"""
Debug script cho insert vào Milvus
"""

import os
import uuid
import logging
from dotenv import load_dotenv
from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType, utility
from sentence_transformers import SentenceTransformer

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment
load_dotenv()

def test_milvus_connection():
    """Test kết nối Milvus"""
    print("🔌 Testing Milvus connection...")
    
    try:
        host = os.getenv('MILVUS_HOST', 'localhost')
        port = os.getenv('MILVUS_PORT', '19530')
        
        connections.connect("default", host=host, port=port)
        print(f"✅ Connected to Milvus at {host}:{port}")
        return True
    except Exception as e:
        print(f"❌ Milvus connection failed: {e}")
        return False

def test_embedding_model():
    """Test embedding model"""
    print("\n🤖 Testing embedding model...")
    
    try:
        model_name = os.getenv('EMBEDDING_MODEL', 'sentence-transformers/all-MiniLM-L6-v2')
        model = SentenceTransformer(model_name)
        
        # Test với text ngắn
        test_text = "This is a test sentence"
        embedding = model.encode(test_text)
        
        print(f"✅ Model loaded: {model_name}")
        print(f"📏 Embedding dimension: {len(embedding)}")
        print(f"📊 Sample values: {embedding[:5]}")
        
        return model
    except Exception as e:
        print(f"❌ Embedding model failed: {e}")
        return None

def test_collection_creation():
    """Test tạo collection"""
    print("\n📚 Testing collection creation...")
    
    try:
        collection_name = os.getenv('MILVUS_COLLECTION_NAME', 'document_chunks')
        dimension = int(os.getenv('MILVUS_DIMENSION', '768'))
        
        # Xóa collection cũ nếu có
        if utility.has_collection(collection_name):
            utility.drop_collection(collection_name)
            print(f"🗑️ Dropped existing collection '{collection_name}'")
        
        # Tạo collection mới
        fields = [
            FieldSchema(name="id", dtype=DataType.VARCHAR, is_primary=True, max_length=100),
            FieldSchema(name="document_id", dtype=DataType.INT64),
            FieldSchema(name="chunk_index", dtype=DataType.INT64),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=dimension)
        ]
        schema = CollectionSchema(fields, description="Document chunks with embeddings")
        collection = Collection(collection_name, schema)
        
        print(f"✅ Created collection '{collection_name}'")
        
        # Tạo index
        index_params = {
            "metric_type": "COSINE",
            "index_type": "IVF_FLAT",
            "params": {"nlist": 1024}
        }
        collection.create_index("embedding", index_params)
        print("✅ Created index")
        
        # Load collection
        collection.load()
        print("✅ Loaded collection")
        
        return collection
    except Exception as e:
        print(f"❌ Collection creation failed: {e}")
        return None

def test_insert_single_chunk(collection, model):
    """Test insert một chunk"""
    print("\n📝 Testing single chunk insert...")
    
    try:
        # Test data
        test_content = "This is a test document chunk for vector search testing."
        document_id = 1
        chunk_index = 0
        
        # Tạo embedding
        print("🔢 Creating embedding...")
        embedding = model.encode(test_content).tolist()
        print(f"✅ Embedding created, length: {len(embedding)}")
        
        # Tạo ID
        chunk_id = str(uuid.uuid4())
        print(f"🆔 Generated ID: {chunk_id}")
        
        # Prepare data
        data = [
            [chunk_id],
            [document_id],
            [chunk_index],
            [embedding]
        ]
        
        print("📊 Data prepared:")
        print(f"  ID: {data[0]}")
        print(f"  Document ID: {data[1]}")
        print(f"  Chunk Index: {data[2]}")
        print(f"  Embedding length: {len(data[3][0])}")
        
        # Insert
        print("💾 Inserting into Milvus...")
        collection.insert(data)
        print("✅ Insert completed")
        
        # Flush để đảm bảo data được lưu
        collection.flush()
        print("✅ Flush completed")
        
        # Kiểm tra số lượng entities
        num_entities = collection.num_entities
        print(f"📈 Total entities: {num_entities}")
        
        return chunk_id
    except Exception as e:
        print(f"❌ Insert failed: {e}")
        return None

def test_query_chunk(collection, chunk_id):
    """Test query chunk đã insert"""
    print(f"\n🔍 Testing query for chunk {chunk_id}...")
    
    try:
        # Query theo ID
        results = collection.query(
            expr=f'id == "{chunk_id}"',
            output_fields=["id", "document_id", "chunk_index"]
        )
        
        if results:
            print("✅ Query successful:")
            for record in results:
                print(f"  ID: {record['id']}")
                print(f"  Document ID: {record['document_id']}")
                print(f"  Chunk Index: {record['chunk_index']}")
            return True
        else:
            print("❌ No results found")
            return False
    except Exception as e:
        print(f"❌ Query failed: {e}")
        return False

def test_search(collection, model):
    """Test search"""
    print("\n🔍 Testing search...")
    
    try:
        # Test query
        query = "test document"
        query_embedding = model.encode(query).tolist()
        
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
        
        print(f"✅ Search completed, found {len(results[0])} results")
        for i, hit in enumerate(results[0]):
            print(f"  {i+1}. Score: {hit.score:.4f}, DocID: {hit.entity.get('document_id')}")
        
        return len(results[0]) > 0
    except Exception as e:
        print(f"❌ Search failed: {e}")
        return False

def main():
    """Main debug function"""
    print("🔍 Milvus Insert Debug Tool")
    print("="*50)
    
    # Test connection
    if not test_milvus_connection():
        return
    
    # Test embedding model
    model = test_embedding_model()
    if model is None:
        return
    
    # Test collection creation
    collection = test_collection_creation()
    if collection is None:
        return
    
    # Test insert
    chunk_id = test_insert_single_chunk(collection, model)
    if chunk_id is None:
        return
    
    # Test query
    if not test_query_chunk(collection, chunk_id):
        print("❌ Query test failed - data not properly inserted")
        return
    
    # Test search
    if not test_search(collection, model):
        print("❌ Search test failed")
        return
    
    print("\n🎉 All tests passed! Milvus insert is working correctly.")

if __name__ == "__main__":
    main() 