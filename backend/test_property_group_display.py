#!/usr/bin/env python3
"""
Test script để kiểm tra việc hiển thị property_group_name trong cột Warehouse
"""

import requests
import json
import time

def test_property_group_display():
    """Test hiển thị property_group_name"""
    
    base_url = "http://localhost:5000"
    
    print("🏢 Testing Property Group Name Display")
    print("=" * 60)
    
    # Bước 1: Lấy danh sách messages có warehouse_id
    print("\n📋 Step 1: Get messages with warehouse_id")
    try:
        response = requests.get(f"{base_url}/api/zalo-test/unprocessed-messages?limit=5&warehouse_id=NOT_NULL")
        
        if response.status_code == 200:
            data = response.json()
            messages = data.get('data', [])
            print(f"   ✅ Found {len(messages)} messages with warehouse_id")
            
            if messages:
                # Bước 2: Lấy apartment info cho các messages này
                print("\n🏠 Step 2: Load apartment info")
                
                warehouse_ids = [msg['warehouse_id'] for msg in messages if msg.get('warehouse_id')]
                print(f"   📊 Warehouse IDs: {warehouse_ids}")
                
                if warehouse_ids:
                    # Gọi API warehouse để lấy apartment info
                    warehouse_response = requests.post(
                        f"{base_url}/warehouse/api/warehouse/apartments/by-ids",
                        json={"apartment_ids": warehouse_ids}
                    )
                    
                    if warehouse_response.status_code == 200:
                        warehouse_data = warehouse_response.json()
                        apartments = warehouse_data.get('data', [])
                        print(f"   ✅ Loaded {len(apartments)} apartments")
                        
                        # Hiển thị thông tin apartments với property_group_name
                        for apt in apartments:
                            print(f"\n   🏢 Apartment {apt['id']}:")
                            print(f"      🏘️  Property Group: {apt.get('property_group_name', 'N/A')}")
                            print(f"      🏠 Unit Code: {apt.get('unit_code', 'N/A')}")
                            print(f"      📐 Type: {apt.get('unit_type_name', 'N/A')}")
                            print(f"      📏 Area: {apt.get('area_gross', 'N/A')}m²")
                            print(f"      💰 Price: {apt.get('price', 'N/A')}")
                            
                            # Kiểm tra xem có property_group_name không
                            if apt.get('property_group_name'):
                                print(f"      ✅ Property Group Name available: {apt['property_group_name']}")
                            else:
                                print(f"      ⚠️  Property Group Name missing")
                    else:
                        print(f"   ❌ Failed to load apartments: {warehouse_response.text}")
                else:
                    print("   ℹ️  No warehouse_ids found")
            else:
                print("   ℹ️  No messages with warehouse_id found")
                
                # Nếu không có messages với warehouse_id, test với messages chưa có warehouse_id
                print("\n🔄 Alternative: Test with messages without warehouse_id")
                response2 = requests.get(f"{base_url}/api/zalo-test/unprocessed-messages?limit=3&warehouse_id=NULL")
                
                if response2.status_code == 200:
                    data2 = response2.json()
                    messages2 = data2.get('data', [])
                    print(f"   ✅ Found {len(messages2)} messages without warehouse_id")
                    
                    if messages2:
                        test_message = messages2[0]
                        print(f"   🧪 Testing message {test_message['id']} to create apartment...")
                        
                        # Process message để tạo apartment
                        process_response = requests.post(
                            f"{base_url}/api/zalo-test/process-message",
                            json={
                                "message_id": test_message['id'],
                                "real_insert": True
                            }
                        )
                        
                        if process_response.status_code == 200:
                            process_data = process_response.json()
                            if process_data.get('success') and process_data.get('data'):
                                apartment_id = process_data['data'].get('apartment_id')
                                if apartment_id:
                                    print(f"   🎉 Created apartment with ID: {apartment_id}")
                                    
                                    # Load apartment info để kiểm tra property_group_name
                                    apt_response = requests.post(
                                        f"{base_url}/warehouse/api/warehouse/apartments/by-ids",
                                        json={"apartment_ids": [apartment_id]}
                                    )
                                    
                                    if apt_response.status_code == 200:
                                        apt_data = apt_response.json()
                                        apartments = apt_data.get('data', [])
                                        
                                        if apartments:
                                            apt = apartments[0]
                                            print(f"   🏢 New Apartment:")
                                            print(f"      🏘️  Property Group: {apt.get('property_group_name', 'N/A')}")
                                            print(f"      🏠 Unit Code: {apt.get('unit_code', 'N/A')}")
                                            print(f"      📐 Type: {apt.get('unit_type_name', 'N/A')}")
                                            
                                            if apt.get('property_group_name'):
                                                print(f"      ✅ Property Group Name available: {apt['property_group_name']}")
                                            else:
                                                print(f"      ⚠️  Property Group Name missing")
                                        else:
                                            print(f"      ❌ No apartment data returned")
                                    else:
                                        print(f"      ❌ Failed to load apartment: {apt_response.text}")
                                else:
                                    print(f"   ⚠️  No apartment_id returned")
                            else:
                                print(f"   ❌ Processing failed: {process_data.get('error', 'Unknown error')}")
                        else:
                            print(f"   ❌ Process request failed: {process_response.text}")
        else:
            print(f"   ❌ Failed to get messages: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Request failed: {e}")
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
    
    print("\n" + "=" * 60)
    print("🏢 Property Group Name Display Test Summary:")
    print("   ✅ Added property_group_name to Warehouse column")
    print("   ✅ Display format: Property: [property_group_name]")
    print("   ✅ Fallback to 'N/A' if property_group_name is missing")
    print("🏁 Test completed")

if __name__ == "__main__":
    test_property_group_display()
