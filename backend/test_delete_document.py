#!/usr/bin/env python3
"""
Test script for delete document API
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:5000"
LOGIN_URL = f"{BASE_URL}/auth/login"
DOCUMENTS_URL = f"{BASE_URL}/user/documents"

def login_and_get_token(username, password):
    """Đăng nhập và lấy JWT token"""
    login_data = {
        "username": username,
        "password": password
    }
    
    response = requests.post(LOGIN_URL, json=login_data)
    
    if response.status_code == 200:
        token = response.json().get('access_token')
        print(f"✅ Login successful for {username}")
        return token
    else:
        print(f"❌ Login failed for {username}: {response.text}")
        return None

def get_documents(token):
    """Lấy danh sách documents"""
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    response = requests.get(DOCUMENTS_URL, headers=headers)
    
    if response.status_code == 200:
        documents = response.json().get('documents', [])
        print(f"✅ Found {len(documents)} documents")
        return documents
    else:
        print(f"❌ Failed to get documents: {response.text}")
        return []

def delete_document(token, document_id):
    """Xóa document"""
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    delete_url = f"{BASE_URL}/user/documents/{document_id}"
    response = requests.delete(delete_url, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Document {document_id} deleted successfully")
        print(f"   Chunks deleted: {result.get('chunks_deleted')}")
        print(f"   Milvus deletion: {result.get('milvus_deletion')}")
        return True
    else:
        print(f"❌ Failed to delete document {document_id}: {response.text}")
        return False

def main():
    """Main test function"""
    print("🧪 Testing Delete Document API")
    print("=" * 50)
    
    # Test với user thường
    print("\n1. Testing with regular user...")
    token = login_and_get_token("testuser", "password123")
    
    if not token:
        print("❌ Cannot proceed without valid token")
        return
    
    # Lấy danh sách documents
    documents = get_documents(token)
    
    if not documents:
        print("❌ No documents found to test deletion")
        return
    
    # Hiển thị danh sách documents
    print("\n📋 Available documents:")
    for doc in documents:
        print(f"   ID: {doc['id']}, Title: {doc['title']}, Source: {doc['source_path']}")
    
    # Chọn document đầu tiên để xóa
    if documents:
        doc_to_delete = documents[0]
        print(f"\n🗑️  Attempting to delete document: {doc_to_delete['title']} (ID: {doc_to_delete['id']})")
        
        # Xác nhận trước khi xóa
        confirm = input("Are you sure you want to delete this document? (y/N): ")
        if confirm.lower() == 'y':
            success = delete_document(token, doc_to_delete['id'])
            if success:
                print("✅ Document deletion test completed successfully")
            else:
                print("❌ Document deletion test failed")
        else:
            print("❌ Deletion cancelled by user")
    else:
        print("❌ No documents available for testing")

if __name__ == "__main__":
    main() 