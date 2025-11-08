#!/usr/bin/env python3
"""
Simple test để kiểm tra warehouse_id update
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_single_message_real_insert():
    """Test single message với real_insert=True"""
    print("🧪 Testing Single Message with real_insert=True")
    print("=" * 50)
    
    # 1. Get unprocessed message
    response = requests.get(f"{BASE_URL}/api/zalo-test/unprocessed-messages?warehouse_id=NULL&limit=1")
    if response.status_code != 200:
        print(f"❌ Failed to get messages: {response.status_code}")
        return
    
    messages = response.json().get('data', [])
    if not messages:
        print("❌ No unprocessed messages found")
        return
    
    message = messages[0]
    message_id = message['id']
    
    print(f"📝 Testing message ID: {message_id}")
    print(f"   Content: {message['content'][:80]}...")
    print(f"   Current warehouse_id: {message.get('warehouse_id', 'NULL')}")
    
    # 2. Process with real_insert=True
    print(f"\n🔄 Processing with real_insert=True...")
    data = {
        "message_id": message_id,
        "real_insert": True
    }
    
    response = requests.post(f"{BASE_URL}/api/zalo-test/process-message", json=data)
    
    if response.status_code != 200:
        print(f"❌ Processing failed: {response.status_code}")
        print(f"Response: {response.text}")
        return
    
    result = response.json()
    
    if result.get('success'):
        print(f"✅ Processing successful")
        print(f"   warehouse_success: {result['data'].get('warehouse_success', False)}")
        print(f"   apartment_id: {result['data'].get('apartment_id', 'N/A')}")
        print(f"   real_insert: {result['data'].get('real_insert', False)}")
        
        # 3. Check if warehouse_id was updated
        print(f"\n🔍 Checking warehouse_id update...")
        check_response = requests.get(f"{BASE_URL}/api/zalo-test/unprocessed-messages?warehouse_id=ALL&limit=100")
        
        if check_response.status_code == 200:
            check_data = check_response.json()
            updated_message = next((msg for msg in check_data['data'] if msg['id'] == message_id), None)
            
            if updated_message:
                warehouse_id = updated_message.get('warehouse_id')
                print(f"   warehouse_id after processing: {warehouse_id}")
                
                if warehouse_id is not None:
                    print(f"   ✅ SUCCESS: warehouse_id was updated to {warehouse_id}")
                else:
                    print(f"   ❌ ERROR: warehouse_id is still NULL!")
                    print(f"   This confirms the bug you're experiencing.")
            else:
                print(f"   ❌ Message not found in check response")
        else:
            print(f"❌ Failed to check warehouse_id: {check_response.status_code}")
    else:
        print(f"❌ Processing failed: {result.get('error')}")

if __name__ == "__main__":
    try:
        test_single_message_real_insert()
    except Exception as e:
        print(f"❌ Test failed: {e}")





