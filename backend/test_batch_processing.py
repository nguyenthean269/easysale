#!/usr/bin/env python3
"""
Test script for batch processing functionality
"""

import requests
import json
import time

# API base URL
BASE_URL = "http://localhost:5000"

def test_batch_processing():
    """Test batch processing with multiple message IDs"""
    print("🧪 Testing Batch Processing Functionality")
    print("=" * 50)
    
    # 1. Get unprocessed messages
    print("\n1. Getting unprocessed messages...")
    response = requests.get(f"{BASE_URL}/api/zalo-test/unprocessed-messages?warehouse_id=NULL&limit=5")
    
    if response.status_code != 200:
        print(f"❌ Failed to get unprocessed messages: {response.status_code}")
        return
    
    data = response.json()
    messages = data.get('data', [])
    
    if len(messages) < 2:
        print("❌ Need at least 2 messages to test batch processing")
        return
    
    print(f"✅ Found {len(messages)} unprocessed messages")
    
    # 2. Select first 3 messages for batch processing
    selected_messages = messages[:3]
    message_ids = [msg['id'] for msg in selected_messages]
    
    print(f"\n2. Selected messages for batch processing: {message_ids}")
    for msg in selected_messages:
        print(f"   - ID: {msg['id']}, Content: {msg['content'][:50]}...")
    
    # 3. Test batch processing (test mode)
    print(f"\n3. Testing batch processing (test mode)...")
    batch_data = {
        "message_ids": message_ids,
        "real_insert": False
    }
    
    start_time = time.time()
    response = requests.post(f"{BASE_URL}/api/zalo-test/process-message", json=batch_data)
    elapsed_time = time.time() - start_time
    
    if response.status_code != 200:
        print(f"❌ Batch processing failed: {response.status_code}")
        print(f"Response: {response.text}")
        return
    
    result = response.json()
    
    if result.get('success'):
        print(f"✅ Batch processing completed in {elapsed_time:.2f}s")
        
        batch_info = result['data']['batch_info']
        print(f"📊 Batch Info:")
        print(f"   - Message IDs: {batch_info['message_ids']}")
        print(f"   - Processed Count: {batch_info['processed_count']}")
        print(f"   - Apartment Count: {batch_info['apartment_count']}")
        print(f"   - Successful Count: {batch_info['successful_count']}")
        print(f"   - Real Insert: {batch_info['real_insert']}")
        print(f"   - Processing Time: {batch_info['processing_time']:.2f}s")
        
        # Show individual results
        print(f"\n📋 Individual Results:")
        for i, result_item in enumerate(result['data']['results']):
            print(f"   {i+1}. Message ID: {result_item['message_id']}")
            print(f"      - Warehouse Success: {result_item['warehouse_success']}")
            print(f"      - Apartment ID: {result_item.get('apartment_id', 'N/A')}")
            print(f"      - Replaced: {result_item.get('replaced', False)}")
            if result_item.get('previous_warehouse_id'):
                print(f"      - Previous Warehouse ID: {result_item['previous_warehouse_id']}")
        
        # Show apartments data
        print(f"\n🏠 Apartments Data:")
        for i, apartment in enumerate(result['data']['apartments']):
            print(f"   {i+1}. Property Group: {apartment.get('property_group_name', 'N/A')}")
            print(f"      - Unit Type: {apartment.get('unit_type_name', 'N/A')}")
            print(f"      - Unit Code: {apartment.get('unit_code', 'N/A')}")
            print(f"      - Price: {apartment.get('price', 'N/A')}")
            print(f"      - Area: {apartment.get('area_gross', 'N/A')}")
        
    else:
        print(f"❌ Batch processing failed: {result.get('error')}")
    
    # 4. Test real insert mode
    print(f"\n4. Testing batch processing (real insert mode)...")
    batch_data_real = {
        "message_ids": message_ids,
        "real_insert": True
    }
    
    start_time = time.time()
    response = requests.post(f"{BASE_URL}/api/zalo-test/process-message", json=batch_data_real)
    elapsed_time = time.time() - start_time
    
    if response.status_code != 200:
        print(f"❌ Real insert batch processing failed: {response.status_code}")
        return
    
    result = response.json()
    
    if result.get('success'):
        print(f"✅ Real insert batch processing completed in {elapsed_time:.2f}s")
        
        batch_info = result['data']['batch_info']
        print(f"📊 Real Insert Results:")
        print(f"   - Successful Count: {batch_info['successful_count']}")
        print(f"   - Warehouse IDs Updated: {len(result['data']['warehouse_ids'])}")
        
        # Check if warehouse_ids were updated
        print(f"\n🔍 Checking warehouse_id updates...")
        for msg_id in message_ids:
            check_response = requests.get(f"{BASE_URL}/api/zalo-test/unprocessed-messages?warehouse_id=NOT_NULL&limit=100")
            if check_response.status_code == 200:
                check_data = check_response.json()
                updated_messages = [msg for msg in check_data['data'] if msg['id'] in message_ids]
                print(f"   - Messages with warehouse_id: {len(updated_messages)}")
                for msg in updated_messages:
                    print(f"     * Message {msg['id']}: warehouse_id = {msg['warehouse_id']}")
                break
    else:
        print(f"❌ Real insert batch processing failed: {result.get('error')}")

def test_single_vs_batch_performance():
    """Compare performance between single and batch processing"""
    print("\n🚀 Performance Comparison: Single vs Batch")
    print("=" * 50)
    
    # Get messages
    response = requests.get(f"{BASE_URL}/api/zalo-test/unprocessed-messages?warehouse_id=NULL&limit=3")
    if response.status_code != 200:
        print("❌ Failed to get messages for performance test")
        return
    
    messages = response.json().get('data', [])
    if len(messages) < 3:
        print("❌ Need at least 3 messages for performance test")
        return
    
    message_ids = [msg['id'] for msg in messages]
    
    # Test single processing
    print("\n1. Testing single processing...")
    single_times = []
    
    for msg_id in message_ids:
        start_time = time.time()
        response = requests.post(f"{BASE_URL}/api/zalo-test/process-message", json={
            "message_id": msg_id,
            "real_insert": False
        })
        elapsed_time = time.time() - start_time
        
        if response.status_code == 200:
            single_times.append(elapsed_time)
            print(f"   - Message {msg_id}: {elapsed_time:.2f}s")
        else:
            print(f"   - Message {msg_id}: Failed")
    
    single_total = sum(single_times)
    single_avg = single_total / len(single_times) if single_times else 0
    
    # Test batch processing
    print(f"\n2. Testing batch processing...")
    start_time = time.time()
    response = requests.post(f"{BASE_URL}/api/zalo-test/process-message", json={
        "message_ids": message_ids,
        "real_insert": False
    })
    batch_time = time.time() - start_time
    
    if response.status_code == 200:
        print(f"   - Batch processing: {batch_time:.2f}s")
        
        # Calculate savings
        time_saved = single_total - batch_time
        efficiency_gain = (time_saved / single_total) * 100 if single_total > 0 else 0
        
        print(f"\n📊 Performance Results:")
        print(f"   - Single processing total: {single_total:.2f}s")
        print(f"   - Single processing average: {single_avg:.2f}s per message")
        print(f"   - Batch processing: {batch_time:.2f}s")
        print(f"   - Time saved: {time_saved:.2f}s")
        print(f"   - Efficiency gain: {efficiency_gain:.1f}%")
        
        if batch_time < single_total:
            print(f"✅ Batch processing is {single_total/batch_time:.1f}x faster!")
        else:
            print(f"⚠️ Batch processing is slower than single processing")
    else:
        print(f"❌ Batch processing failed: {response.status_code}")

if __name__ == "__main__":
    try:
        test_batch_processing()
        test_single_vs_batch_performance()
        print(f"\n✅ All tests completed!")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")





