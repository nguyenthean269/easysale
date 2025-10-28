#!/usr/bin/env python3
"""
Test script để kiểm tra flow hoàn chỉnh với real insert:
1. Gọi /api/zalo-test/unprocessed-messages để lấy messages
2. Gọi /warehouse/api/warehouse/apartments/by-ids để load apartment info
3. Gọi /api/zalo-test/process-message với real_insert=true để xử lý message và cập nhật warehouse_id
4. Gọi lại /warehouse/api/warehouse/apartments/by-ids để update apartment info
"""

import requests
import json
import time

def test_real_insert_flow():
    """Test flow với real insert"""
    
    base_url = "http://localhost:5000"
    
    print("🧪 Testing Real Insert Flow")
    print("=" * 60)
    
    # Bước 1: Lấy danh sách messages chưa có warehouse_id
    print("\n📋 Step 1: Get messages without warehouse_id")
    try:
        response = requests.get(f"{base_url}/api/zalo-test/unprocessed-messages?limit=5&warehouse_id=NULL")
        
        if response.status_code == 200:
            data = response.json()
            messages = data.get('data', [])
            print(f"   ✅ Found {len(messages)} messages without warehouse_id")
            
            if messages:
                # Chọn message đầu tiên để test
                test_message = messages[0]
                print(f"   🧪 Testing message {test_message['id']}: {test_message['content'][:50]}...")
                
                # Bước 2: Test process message với real_insert=true
                print(f"\n⚙️ Step 2: Process message with real_insert=true")
                
                process_response = requests.post(
                    f"{base_url}/api/zalo-test/process-message",
                    json={
                        "message_id": test_message['id'],
                        "real_insert": True
                    }
                )
                
                if process_response.status_code == 200:
                    process_data = process_response.json()
                    print(f"   ✅ Processing result: {process_data.get('success', False)}")
                    
                    if process_data.get('success') and process_data.get('data'):
                        apartment_id = process_data['data'].get('apartment_id')
                        real_insert = process_data['data'].get('real_insert', False)
                        
                        print(f"   🎉 Processing successful!")
                        print(f"      📊 Apartment ID: {apartment_id}")
                        print(f"      🔄 Real Insert: {real_insert}")
                        
                        if apartment_id:
                            # Bước 3: Kiểm tra warehouse_id đã được cập nhật chưa
                            print(f"\n🔍 Step 3: Check if warehouse_id was updated")
                            
                            # Lấy lại message để kiểm tra warehouse_id
                            check_response = requests.get(f"{base_url}/api/zalo-test/unprocessed-messages?limit=1&warehouse_id={apartment_id}")
                            
                            if check_response.status_code == 200:
                                check_data = check_response.json()
                                updated_messages = check_data.get('data', [])
                                
                                if updated_messages:
                                    updated_message = updated_messages[0]
                                    print(f"   ✅ Found updated message:")
                                    print(f"      📝 Message ID: {updated_message['id']}")
                                    print(f"      🏠 Warehouse ID: {updated_message.get('warehouse_id')}")
                                    
                                    if updated_message.get('warehouse_id') == apartment_id:
                                        print(f"   🎉 SUCCESS: warehouse_id was correctly updated!")
                                        
                                        # Bước 4: Load apartment info mới
                                        print(f"\n🏠 Step 4: Load new apartment info")
                                        
                                        apartment_response = requests.post(
                                            f"{base_url}/warehouse/api/warehouse/apartments/by-ids",
                                            json={"apartment_ids": [apartment_id]}
                                        )
                                        
                                        if apartment_response.status_code == 200:
                                            apartment_data = apartment_response.json()
                                            apartments = apartment_data.get('data', [])
                                            
                                            if apartments:
                                                apt = apartments[0]
                                                print(f"   ✅ New apartment loaded:")
                                                print(f"      🏢 ID: {apt['id']}")
                                                print(f"      🏠 Unit Code: {apt.get('unit_code', 'N/A')}")
                                                print(f"      📐 Type: {apt.get('unit_type_name', 'N/A')}")
                                                print(f"      📏 Area: {apt.get('area_gross', 'N/A')}m²")
                                                print(f"      💰 Price: {apt.get('price', 'N/A')}")
                                                
                                                print(f"\n🎉 COMPLETE SUCCESS!")
                                                print(f"   ✅ Message processed successfully")
                                                print(f"   ✅ warehouse_id updated in database")
                                                print(f"   ✅ Apartment info loaded correctly")
                                            else:
                                                print(f"   ❌ No apartment found for ID {apartment_id}")
                                        else:
                                            print(f"   ❌ Failed to load apartment: {apartment_response.text}")
                                    else:
                                        print(f"   ❌ warehouse_id not updated correctly")
                                else:
                                    print(f"   ❌ Updated message not found")
                            else:
                                print(f"   ❌ Failed to check updated message: {check_response.text}")
                        else:
                            print(f"   ⚠️  No apartment_id in response")
                    else:
                        print(f"   ❌ Processing failed: {process_data.get('error', 'Unknown error')}")
                else:
                    print(f"   ❌ Process request failed: {process_response.text}")
            else:
                print("   ℹ️  No messages without warehouse_id found")
        else:
            print(f"   ❌ Failed to get messages: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Request failed: {e}")
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 Real insert flow test finished")

if __name__ == "__main__":
    test_real_insert_flow()
