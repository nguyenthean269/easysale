#!/usr/bin/env python3
"""
Test script để kiểm tra kết nối Milvus
"""

import os
from dotenv import load_dotenv
from pymilvus import connections, utility
import sys

# Load environment variables
load_dotenv()

def test_milvus_connection():
    """Test kết nối đến Milvus server"""
    
    # Lấy cấu hình từ environment
    host = os.getenv('MILVUS_HOST', 'localhost')
    port = os.getenv('MILVUS_PORT', '19530')
    
    print(f"🔍 Testing Milvus connection to {host}:{port}")
    
    try:
        # Thử kết nối
        connections.connect("default", host=host, port=port)
        print("✅ Successfully connected to Milvus!")
        
        # Kiểm tra server info
        from pymilvus import utility
        server_version = utility.get_server_version()
        print(f"📋 Milvus version: {server_version}")
        
        # Liệt kê collections
        collections = utility.list_collections()
        print(f"📚 Collections: {collections}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to connect to Milvus: {e}")
        print("\n🔧 Troubleshooting steps:")
        print("1. Check if Milvus server is running")
        print("2. Verify MILVUS_HOST and MILVUS_PORT in .env file")
        print("3. Check firewall settings")
        print("4. Try restarting Milvus server")
        return False

def check_environment():
    """Kiểm tra cấu hình environment"""
    print("🔧 Checking environment configuration...")
    
    host = os.getenv('MILVUS_HOST', 'localhost')
    port = os.getenv('MILVUS_PORT', '19530')
    collection_name = os.getenv('MILVUS_COLLECTION_NAME', 'document_chunks')
    dimension = os.getenv('MILVUS_DIMENSION', '768')
    
    print(f"  MILVUS_HOST: {host}")
    print(f"  MILVUS_PORT: {port}")
    print(f"  MILVUS_COLLECTION_NAME: {collection_name}")
    print(f"  MILVUS_DIMENSION: {dimension}")
    
    # Kiểm tra file .env
    if os.path.exists('.env'):
        print("  ✅ .env file exists")
    else:
        print("  ⚠️  .env file not found")

def install_milvus_guide():
    """Hướng dẫn cài đặt Milvus"""
    print("\n📖 Milvus Installation Guide:")
    print("="*50)
    
    print("\n1. Install Milvus using Docker:")
    print("   wget https://github.com/milvus-io/milvus/releases/download/v2.3.3/milvus-standalone-docker-compose.yml -O docker-compose.yml")
    print("   docker-compose up -d")
    
    print("\n2. Check Milvus status:")
    print("   docker-compose ps")
    
    print("\n3. View Milvus logs:")
    print("   docker-compose logs milvus-standalone")
    
    print("\n4. Test connection:")
    print("   telnet localhost 19530")
    
    print("\n5. Alternative: Use Milvus Cloud")
    print("   - Sign up at https://cloud.zilliz.com/")
    print("   - Get connection string")
    print("   - Update MILVUS_HOST in .env")

if __name__ == "__main__":
    print("🧪 Milvus Connection Test")
    print("="*50)
    
    # Kiểm tra environment
    check_environment()
    
    print("\n" + "="*50)
    
    # Test kết nối
    success = test_milvus_connection()
    
    if not success:
        print("\n" + "="*50)
        install_milvus_guide()
        sys.exit(1)
    
    print("\n🎉 Milvus connection test completed successfully!") 