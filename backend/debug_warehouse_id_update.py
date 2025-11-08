#!/usr/bin/env python3
"""
Debug script để kiểm tra vấn đề warehouse_id không được cập nhật
"""

import requests
import json
import time

# API base URL
BASE_URL = "http://localhost:5000"

def test_warehouse_id_update():
    """Test warehouse_id update issue"""
    print("🔍 Debugging Warehouse ID Update Issue")
    print("=" * 50)
    
    # 1. Get unprocessed messages
    print("\n1. Getting unprocessed messages...")
    response = requests.get(f"{BASE_URL}/api/zalo-test/unprocessed-messages?warehouse_id=NULL&limit=3")
    
    if response.status_code != 200:
        print(f"❌ Failed to get unprocessed messages: {response.status_code}")
        return
    
    data = response.json()
    messages = data.get('data', [])
    
    if len(messages) < 1:
        print("❌ Need at least 1 message to test")
        return
    
    test_message = messages[0]
    message_id = test_message['id']
    
    print(f"✅ Found test message: ID={message_id}")
    print(f"   Content: {test_message['content'][:100]}...")
    print(f"   Current warehouse_id: {test_message.get('warehouse_id', 'NULL')}")
    
    # 2. Test with real_insert=False (test mode)
    print(f"\n2. Testing with real_insert=False (test mode)...")
    test_data = {
        "message_id": message_id,
        "real_insert": False
    }
    
    response = requests.post(f"{BASE_URL}/api/zalo-test/process-message", json=test_data)
    
    if response.status_code != 200:
        print(f"❌ Test mode processing failed: {response.status_code}")
        return
    
    result = response.json()
    
    if result.get('success'):
        print(f"✅ Test mode processing successful")
        print(f"   warehouse_success: {result['data'].get('warehouse_success', False)}")
        print(f"   apartment_id: {result['data'].get('apartment_id', 'N/A')}")
        print(f"   real_insert: {result['data'].get('real_insert', False)}")
        
        # Check if warehouse_id was updated (should NOT be updated in test mode)
        print(f"\n3. Checking warehouse_id after test mode...")
        check_response = requests.get(f"{BASE_URL}/api/zalo-test/unprocessed-messages?warehouse_id=ALL&limit=100")
        if check_response.status_code == 200:
            check_data = check_response.json()
            updated_message = next((msg for msg in check_data['data'] if msg['id'] == message_id), None)
            if updated_message:
                print(f"   warehouse_id after test mode: {updated_message.get('warehouse_id', 'NULL')}")
                if updated_message.get('warehouse_id') is None:
                    print(f"   ✅ Correct: warehouse_id is still NULL (test mode)")
                else:
                    print(f"   ❌ Error: warehouse_id was updated in test mode!")
    else:
        print(f"❌ Test mode processing failed: {result.get('error')}")
        return
    
    # 4. Test with real_insert=True (real insert mode)
    print(f"\n4. Testing with real_insert=True (real insert mode)...")
    real_data = {
        "message_id": message_id,
        "real_insert": True
    }
    
    response = requests.post(f"{BASE_URL}/api/zalo-test/process-message", json=real_data)
    
    if response.status_code != 200:
        print(f"❌ Real insert processing failed: {response.status_code}")
        return
    
    result = response.json()
    
    if result.get('success'):
        print(f"✅ Real insert processing successful")
        print(f"   warehouse_success: {result['data'].get('warehouse_success', False)}")
        print(f"   apartment_id: {result['data'].get('apartment_id', 'N/A')}")
        print(f"   real_insert: {result['data'].get('real_insert', False)}")
        print(f"   replaced: {result['data'].get('replaced', False)}")
        
        # Check if warehouse_id was updated (should be updated in real insert mode)
        print(f"\n5. Checking warehouse_id after real insert mode...")
        check_response = requests.get(f"{BASE_URL}/api/zalo-test/unprocessed-messages?warehouse_id=ALL&limit=100")
        if check_response.status_code == 200:
            check_data = check_response.json()
            updated_message = next((msg for msg in check_data['data'] if msg['id'] == message_id), None)
            if updated_message:
                print(f"   warehouse_id after real insert: {updated_message.get('warehouse_id', 'NULL')}")
                if updated_message.get('warehouse_id') is not None:
                    print(f"   ✅ Correct: warehouse_id was updated to {updated_message['warehouse_id']}")
                else:
                    print(f"   ❌ ERROR: warehouse_id is still NULL after real insert!")
                    print(f"   This is the bug you're experiencing!")
            else:
                print(f"   ❌ Message not found in check response")
    else:
        print(f"❌ Real insert processing failed: {result.get('error')}")

def test_batch_warehouse_id_update():
    """Test batch warehouse_id update issue"""
    print("\n🔍 Testing Batch Warehouse ID Update")
    print("=" * 50)
    
    # 1. Get unprocessed messages
    print("\n1. Getting unprocessed messages...")
    response = requests.get(f"{BASE_URL}/api/zalo-test/unprocessed-messages?warehouse_id=NULL&limit=3")
    
    if response.status_code != 200:
        print(f"❌ Failed to get unprocessed messages: {response.status_code}")
        return
    
    data = response.json()
    messages = data.get('data', [])
    
    if len(messages) < 2:
        print("❌ Need at least 2 messages to test batch")
        return
    
    message_ids = [msg['id'] for msg in messages[:2]]
    
    print(f"✅ Found test messages: IDs={message_ids}")
    
    # 2. Test batch with real_insert=True
    print(f"\n2. Testing batch with real_insert=True...")
    batch_data = {
        "message_ids": message_ids,
        "real_insert": True
    }
    
    response = requests.post(f"{BASE_URL}/api/zalo-test/process-message", json=batch_data)
    
    if response.status_code != 200:
        print(f"❌ Batch processing failed: {response.status_code}")
        return
    
    result = response.json()
    
    if result.get('success'):
        print(f"✅ Batch processing successful")
        batch_info = result['data']['batch_info']
        print(f"   Processed: {batch_info['processed_count']} messages")
        print(f"   Successful: {batch_info['successful_count']} apartments")
        print(f"   Real insert: {batch_info['real_insert']}")
        
        # Check individual results
        print(f"\n3. Individual results:")
        for i, result_item in enumerate(result['data']['results']):
            print(f"   Message {result_item['message_id']}:")
            print(f"     - warehouse_success: {result_item['warehouse_success']}")
            print(f"     - apartment_id: {result_item.get('apartment_id', 'N/A')}")
        
        # Check if warehouse_ids were actually updated
        print(f"\n4. Checking warehouse_id updates in database...")
        check_response = requests.get(f"{BASE_URL}/api/zalo-test/unprocessed-messages?warehouse_id=ALL&limit=100")
        if check_response.status_code == 200:
            check_data = check_response.json()
            for msg_id in message_ids:
                updated_message = next((msg for msg in check_data['data'] if msg['id'] == msg_id), None)
                if updated_message:
                    warehouse_id = updated_message.get('warehouse_id')
                    print(f"   Message {msg_id}: warehouse_id = {warehouse_id}")
                    if warehouse_id is None:
                        print(f"   ❌ ERROR: warehouse_id is NULL for message {msg_id}!")
                    else:
                        print(f"   ✅ Correct: warehouse_id = {warehouse_id}")
                else:
                    print(f"   ❌ Message {msg_id} not found in check response")
    else:
        print(f"❌ Batch processing failed: {result.get('error')}")

if __name__ == "__main__":
    try:
        test_warehouse_id_update()
        test_batch_warehouse_id_update()
        print(f"\n✅ Debug tests completed!")
    except Exception as e:
        print(f"❌ Debug test failed with error: {e}")





