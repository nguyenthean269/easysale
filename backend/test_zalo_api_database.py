#!/usr/bin/env python3
"""
Test script để kiểm tra API /api/zalo-test/unprocessed-messages
Kiểm tra xem có đang lấy dữ liệu từ bảng zalo_received_messages trong database easychat không
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_unprocessed_messages_api():
    """Test API unprocessed-messages với các tham số khác nhau"""
    
    base_url = "http://localhost:5000/api/zalo-test/unprocessed-messages"
    
    test_cases = [
        {"warehouse_id": "ALL", "limit": 10, "description": "Tất cả messages"},
        {"warehouse_id": "NULL", "limit": 10, "description": "Messages chưa push vào warehouse"},
        {"warehouse_id": "NOT_NULL", "limit": 10, "description": "Messages đã push vào warehouse"},
    ]
    
    print("🧪 Testing API /api/zalo-test/unprocessed-messages")
    print("=" * 60)
    
    for test_case in test_cases:
        print(f"\n📋 Test: {test_case['description']}")
        print(f"   Parameters: warehouse_id={test_case['warehouse_id']}, limit={test_case['limit']}")
        
        try:
            # Gọi API
            response = requests.get(
                base_url,
                params={
                    'warehouse_id': test_case['warehouse_id'],
                    'limit': test_case['limit']
                },
                timeout=10
            )
            
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Success: {data.get('success', False)}")
                print(f"   Count: {data.get('count', 0)}")
                print(f"   Warehouse ID Filter: {data.get('warehouse_id_filter', 'N/A')}")
                
                # Kiểm tra cấu trúc dữ liệu
                if 'data' in data and len(data['data']) > 0:
                    message = data['data'][0]
                    print(f"   Sample message fields:")
                    for key in message.keys():
                        print(f"     - {key}: {type(message[key]).__name__}")
                    
                    # Kiểm tra các trường quan trọng
                    required_fields = ['id', 'session_id', 'content', 'received_at', 'warehouse_id']
                    missing_fields = [field for field in required_fields if field not in message]
                    
                    if missing_fields:
                        print(f"   ⚠️  Missing fields: {missing_fields}")
                    else:
                        print(f"   ✅ All required fields present")
                        
                    # Kiểm tra warehouse_id
                    if test_case['warehouse_id'] == 'NULL':
                        null_count = sum(1 for msg in data['data'] if msg.get('warehouse_id') is None)
                        print(f"   ✅ NULL warehouse_id count: {null_count}/{len(data['data'])}")
                    elif test_case['warehouse_id'] == 'NOT_NULL':
                        not_null_count = sum(1 for msg in data['data'] if msg.get('warehouse_id') is not None)
                        print(f"   ✅ NOT_NULL warehouse_id count: {not_null_count}/{len(data['data'])}")
                else:
                    print(f"   ℹ️  No data returned")
                    
            else:
                print(f"   ❌ Error: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Request failed: {e}")
        except Exception as e:
            print(f"   ❌ Unexpected error: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 Test completed")

def check_database_connection():
    """Kiểm tra thông tin database connection"""
    print("\n🔍 Database Connection Info:")
    print(f"   DB_CHAT_HOST: {os.getenv('DB_CHAT_HOST', 'NOT_SET')}")
    print(f"   DB_CHAT_PORT: {os.getenv('DB_CHAT_PORT', 'NOT_SET')}")
    print(f"   DB_CHAT_USER: {os.getenv('DB_CHAT_USER', 'NOT_SET')}")
    print(f"   DB_CHAT_NAME: {os.getenv('DB_CHAT_NAME', 'NOT_SET')}")
    print(f"   DB_CHAT_PASSWORD: {'SET' if os.getenv('DB_CHAT_PASSWORD') else 'NOT_SET'}")

if __name__ == "__main__":
    check_database_connection()
    test_unprocessed_messages_api()
