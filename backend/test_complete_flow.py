#!/usr/bin/env python3
"""
Test script để kiểm tra flow hoàn chỉnh:
1. Gọi /api/zalo-test/unprocessed-messages để lấy messages
2. Gọi /warehouse/api/warehouse/apartments/by-ids để load apartment info
3. Gọi /api/zalo-test/process-message để xử lý message
4. Gọi lại /warehouse/api/warehouse/apartments/by-ids để update apartment info
"""

import requests
import json
import time

def test_complete_flow():
    """Test flow hoàn chỉnh"""
    
    base_url = "http://localhost:5000"
    
    print("🧪 Testing Complete Flow")
    print("=" * 60)
    
    # Bước 1: Lấy danh sách messages
    print("\n📋 Step 1: Get unprocessed messages")
    try:
        response = requests.get(f"{base_url}/api/zalo-test/unprocessed-messages?limit=5&warehouse_id=ALL")
        
        if response.status_code == 200:
            data = response.json()
            messages = data.get('data', [])
            print(f"   ✅ Found {len(messages)} messages")
            
            if messages:
                # Hiển thị thông tin messages
                for msg in messages:
                    print(f"   📝 Message {msg['id']}: warehouse_id={msg.get('warehouse_id', 'NULL')}")
                
                # Bước 2: Load apartment info cho messages có warehouse_id
                print("\n🏠 Step 2: Load apartment info for messages with warehouse_id")
                
                messages_with_warehouse_id = [msg for msg in messages if msg.get('warehouse_id')]
                
                if messages_with_warehouse_id:
                    warehouse_ids = [msg['warehouse_id'] for msg in messages_with_warehouse_id]
                    print(f"   📊 Loading apartments for warehouse_ids: {warehouse_ids}")
                    
                    # Gọi API warehouse
                    warehouse_response = requests.post(
                        f"{base_url}/warehouse/api/warehouse/apartments/by-ids",
                        json={"apartment_ids": warehouse_ids}
                    )
                    
                    if warehouse_response.status_code == 200:
                        warehouse_data = warehouse_response.json()
                        apartments = warehouse_data.get('data', [])
                        print(f"   ✅ Loaded {len(apartments)} apartments")
                        
                        for apt in apartments:
                            print(f"   🏢 Apartment {apt['id']}: {apt.get('unit_code', 'N/A')} - {apt.get('unit_type_name', 'N/A')}")
                    else:
                        print(f"   ❌ Failed to load apartments: {warehouse_response.text}")
                else:
                    print("   ℹ️  No messages with warehouse_id found")
                
                # Bước 3: Test process một message chưa có warehouse_id
                print("\n⚙️ Step 3: Process a message without warehouse_id")
                
                messages_without_warehouse_id = [msg for msg in messages if not msg.get('warehouse_id')]
                
                if messages_without_warehouse_id:
                    test_message = messages_without_warehouse_id[0]
                    print(f"   🧪 Testing message {test_message['id']}: {test_message['content'][:50]}...")
                    
                    # Gọi API process message
                    process_response = requests.post(
                        f"{base_url}/api/zalo-test/process-message",
                        json={"message_id": test_message['id']}
                    )
                    
                    if process_response.status_code == 200:
                        process_data = process_response.json()
                        print(f"   ✅ Processing result: {process_data.get('success', False)}")
                        
                        if process_data.get('success') and process_data.get('data'):
                            apartment_id = process_data['data'].get('apartment_id')
                            if apartment_id:
                                print(f"   🎉 New apartment created with ID: {apartment_id}")
                                
                                # Bước 4: Load apartment info mới
                                print(f"\n🔄 Step 4: Load new apartment info for ID {apartment_id}")
                                
                                new_apartment_response = requests.post(
                                    f"{base_url}/warehouse/api/warehouse/apartments/by-ids",
                                    json={"apartment_ids": [apartment_id]}
                                )
                                
                                if new_apartment_response.status_code == 200:
                                    new_apartment_data = new_apartment_response.json()
                                    new_apartments = new_apartment_data.get('data', [])
                                    
                                    if new_apartments:
                                        new_apt = new_apartments[0]
                                        print(f"   ✅ New apartment loaded:")
                                        print(f"      🏢 ID: {new_apt['id']}")
                                        print(f"      🏠 Unit Code: {new_apt.get('unit_code', 'N/A')}")
                                        print(f"      📐 Type: {new_apt.get('unit_type_name', 'N/A')}")
                                        print(f"      📏 Area: {new_apt.get('area_gross', 'N/A')}m²")
                                        print(f"      💰 Price: {new_apt.get('price', 'N/A')}")
                                    else:
                                        print(f"   ❌ No apartment found for ID {apartment_id}")
                                else:
                                    print(f"   ❌ Failed to load new apartment: {new_apartment_response.text}")
                            else:
                                print(f"   ⚠️  No apartment_id in response")
                        else:
                            print(f"   ❌ Processing failed: {process_data.get('error', 'Unknown error')}")
                    else:
                        print(f"   ❌ Process request failed: {process_response.text}")
                else:
                    print("   ℹ️  No messages without warehouse_id found")
            else:
                print("   ℹ️  No messages found")
        else:
            print(f"   ❌ Failed to get messages: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Request failed: {e}")
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 Complete flow test finished")

if __name__ == "__main__":
    test_complete_flow()