#!/usr/bin/env python3
"""
Test script cho Zalo Chunks API
"""

import requests
import json

# Cấu hình
BASE_URL = "http://localhost:5000"
LOGIN_URL = f"{BASE_URL}/auth/login"
ZALO_CHUNKS_URL = f"{BASE_URL}/zalo-chunks"

def login_and_get_token():
    """Đăng nhập và lấy token"""
    print("🔐 Logging in...")
    
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        response = requests.post(LOGIN_URL, json=login_data)
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token')
            print(f"✅ Login successful")
            return token
        else:
            print(f"❌ Login failed: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Login error: {str(e)}")
        return None

def test_get_sessions(token):
    """Test lấy danh sách sessions"""
    print("\n📋 Testing get sessions...")
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(f"{ZALO_CHUNKS_URL}/sessions", headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Sessions retrieved successfully")
            print(f"Total sessions: {data.get('total_sessions', 0)}")
            
            sessions = data.get('sessions', [])
            for session in sessions:
                print(f"  - Session {session['session_id']}: {session['total_messages']} messages, {session['processing_percentage']}% processed")
            
            return sessions
        else:
            print(f"❌ Get sessions failed: {response.text}")
            return []
            
    except Exception as e:
        print(f"❌ Get sessions error: {str(e)}")
        return []

def test_get_stats(token, session_id):
    """Test lấy thống kê"""
    print(f"\n📊 Testing get stats for session {session_id}...")
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(f"{ZALO_CHUNKS_URL}/stats?session_id={session_id}", headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Stats retrieved successfully")
            print(f"  - Total messages: {data.get('total_messages', 0)}")
            print(f"  - Processed: {data.get('processed_messages', 0)}")
            print(f"  - Unprocessed: {data.get('unprocessed_messages', 0)}")
            print(f"  - Total chunks: {data.get('total_chunks', 0)}")
            print(f"  - Processing percentage: {data.get('processing_percentage', 0)}%")
            return data
        else:
            print(f"❌ Get stats failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Get stats error: {str(e)}")
        return None

def test_process_messages(token, session_id, chunk_size=50):
    """Test xử lý tin nhắn"""
    print(f"\n⚙️ Testing process messages for session {session_id}...")
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    data = {
        "session_id": session_id,
        "chunk_size": chunk_size
    }
    
    try:
        response = requests.post(f"{ZALO_CHUNKS_URL}/process-messages", json=data, headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Process messages successful")
            print(f"  - Processed count: {result.get('processed_count', 0)}")
            print(f"  - Chunks created: {result.get('chunks_created', 0)}")
            print(f"  - Total messages: {result.get('total_messages', 0)}")
            return result
        else:
            print(f"❌ Process messages failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Process messages error: {str(e)}")
        return None

def main():
    """Main test function"""
    print("🧪 Testing Zalo Chunks API")
    print("=" * 50)
    
    # Step 1: Login
    token = login_and_get_token()
    if not token:
        print("❌ Cannot proceed without authentication token")
        return
    
    # Step 2: Get sessions
    sessions = test_get_sessions(token)
    if not sessions:
        print("❌ No sessions found, cannot test further")
        return
    
    # Step 3: Test with first session
    first_session = sessions[0]
    session_id = first_session['session_id']
    
    # Get stats before processing
    stats_before = test_get_stats(token, session_id)
    
    # Process messages
    process_result = test_process_messages(token, session_id, chunk_size=10)  # Small chunk size for testing
    
    # Get stats after processing
    stats_after = test_get_stats(token, session_id)
    
    # Compare results
    if stats_before and stats_after and process_result:
        print(f"\n📈 Results comparison:")
        print(f"  - Messages processed: {process_result.get('processed_count', 0)}")
        print(f"  - Chunks created: {process_result.get('chunks_created', 0)}")
        print(f"  - Processing percentage before: {stats_before.get('processing_percentage', 0)}%")
        print(f"  - Processing percentage after: {stats_after.get('processing_percentage', 0)}%")
    
    print("\n" + "=" * 50)
    print("✅ Zalo Chunks API tests completed!")

if __name__ == "__main__":
    main()






