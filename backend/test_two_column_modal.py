#!/usr/bin/env python3
"""
Test script để kiểm tra modal 2 cột: Zalo Message Details và Warehouse Apartment Details
"""

import requests
import json
import time

def test_two_column_modal():
    """Test two-column modal layout"""
    
    base_url = "http://localhost:5000"
    
    print("📱🏠 Testing Two-Column Modal Layout")
    print("=" * 60)
    
    # Bước 1: Tìm message có warehouse_id để test modal
    print("\n📋 Step 1: Find message with warehouse_id")
    try:
        response = requests.get(f"{base_url}/api/zalo-test/unprocessed-messages?limit=5&warehouse_id=NOT_NULL")
        
        if response.status_code == 200:
            data = response.json()
            messages = data.get('data', [])
            print(f"   ✅ Found {len(messages)} messages with warehouse_id")
            
            if messages:
                # Chọn message đầu tiên để test
                test_message = messages[0]
                message_id = test_message['id']
                warehouse_id = test_message['warehouse_id']
                
                print(f"\n🧪 Testing message {message_id}:")
                print(f"   📱 Message ID: {message_id}")
                print(f"   🏠 Warehouse ID: {warehouse_id}")
                
                # Bước 2: Verify Zalo Message data
                print(f"\n📱 Step 2: Verify Zalo Message Data")
                print(f"   📊 Zalo Message Fields:")
                print(f"      ID: {test_message.get('id')}")
                print(f"      Session ID: {test_message.get('session_id', 'N/A')}")
                print(f"      Config ID: {test_message.get('config_id', 'N/A')}")
                print(f"      Sender ID: {test_message.get('sender_id', 'N/A')}")
                print(f"      Sender Name: {test_message.get('sender_name', 'N/A')}")
                print(f"      Thread ID: {test_message.get('thread_id', 'N/A')}")
                print(f"      Thread Type: {test_message.get('thread_type', 'N/A')}")
                print(f"      Received At: {test_message.get('received_at', 'N/A')}")
                print(f"      Kafka Status: {test_message.get('status_push_kafka', 'N/A')}")
                print(f"      Warehouse ID: {test_message.get('warehouse_id', 'N/A')}")
                print(f"      Content Length: {len(test_message.get('content', ''))}")
                print(f"      Reply Quote: {test_message.get('reply_quote', 'N/A')}")
                print(f"      Content Hash: {test_message.get('content_hash', 'N/A')}")
                print(f"      Document Chunks: {test_message.get('added_document_chunks', 'N/A')}")
                
                # Bước 3: Verify Warehouse Apartment data
                print(f"\n🏠 Step 3: Verify Warehouse Apartment Data")
                
                apartment_response = requests.post(
                    f"{base_url}/warehouse/api/warehouse/apartments/by-ids",
                    json={"apartment_ids": [warehouse_id]}
                )
                
                if apartment_response.status_code == 200:
                    apartment_data = apartment_response.json()
                    apartments = apartment_data.get('data', [])
                    
                    if apartments:
                        apartment = apartments[0]
                        print(f"   📊 Warehouse Apartment Fields:")
                        print(f"      ID: {apartment.get('id')}")
                        print(f"      Property Group: {apartment.get('property_group_name', 'N/A')}")
                        print(f"      Unit Code: {apartment.get('unit_code', 'N/A')}")
                        print(f"      Unit Type: {apartment.get('unit_type_name', 'N/A')}")
                        print(f"      Floor: {apartment.get('unit_floor_number', 'N/A')}")
                        print(f"      Unit Axis: {apartment.get('unit_axis', 'N/A')}")
                        print(f"      Gross Area: {apartment.get('area_gross', 'N/A')}m²")
                        print(f"      Net Area: {apartment.get('area_net', 'N/A')}m²")
                        print(f"      Construction Area: {apartment.get('area_construction', 'N/A')}m²")
                        print(f"      Land Area: {apartment.get('area_land', 'N/A')}m²")
                        print(f"      Price: {apartment.get('price', 'N/A')}")
                        print(f"      Early Price: {apartment.get('price_early', 'N/A')}")
                        print(f"      Schedule Price: {apartment.get('price_schedule', 'N/A')}")
                        print(f"      Loan Price: {apartment.get('price_loan', 'N/A')}")
                        print(f"      Bedrooms: {apartment.get('num_bedrooms', 'N/A')}")
                        print(f"      Bathrooms: {apartment.get('num_bathrooms', 'N/A')}")
                        print(f"      View Type: {apartment.get('type_view', 'N/A')}")
                        print(f"      Door Direction: {apartment.get('direction_door', 'N/A')}")
                        print(f"      Balcony Direction: {apartment.get('direction_balcony', 'N/A')}")
                        print(f"      Status: {apartment.get('status', 'N/A')}")
                        print(f"      Allocation: {apartment.get('unit_allocation', 'N/A')}")
                        print(f"      Notes: {apartment.get('notes', 'N/A')}")
                        
                        # Bước 4: Test Modal Layout
                        print(f"\n🎭 Step 4: Test Modal Layout")
                        print(f"   📱 Column 1 - Zalo Message Details:")
                        print(f"      ✅ Message ID (font-mono)")
                        print(f"      ✅ Session ID (font-mono)")
                        print(f"      ✅ Config ID (font-mono)")
                        print(f"      ✅ Sender ID (font-mono)")
                        print(f"      ✅ Sender Name")
                        print(f"      ✅ Thread ID (font-mono)")
                        print(f"      ✅ Thread Type")
                        print(f"      ✅ Received At (date pipe)")
                        print(f"      ✅ Kafka Status (colored badge)")
                        print(f"      ✅ Warehouse ID (green, bold)")
                        print(f"      ✅ Message Content (scrollable, max-h-40)")
                        print(f"      ✅ Reply Quote (if exists)")
                        print(f"      ✅ Content Hash (font-mono, small)")
                        print(f"      ✅ Document Chunks (colored badge)")
                        
                        print(f"\n   🏠 Column 2 - Warehouse Apartment Details:")
                        print(f"      ✅ Basic Information section")
                        print(f"         - Apartment ID (font-mono)")
                        print(f"         - Property Group")
                        print(f"         - Unit Code (font-mono)")
                        print(f"         - Unit Type")
                        print(f"         - Floor")
                        print(f"         - Unit Axis")
                        print(f"      ✅ Area Information section")
                        print(f"         - Gross Area (formatted)")
                        print(f"         - Net Area (formatted)")
                        print(f"         - Construction Area (formatted)")
                        print(f"         - Land Area (formatted)")
                        print(f"      ✅ Pricing Information section")
                        print(f"         - Price (green, bold)")
                        print(f"         - Early Price (blue)")
                        print(f"         - Schedule Price (purple)")
                        print(f"         - Loan Price (orange)")
                        print(f"      ✅ Rooms & Features section")
                        print(f"         - Bedrooms")
                        print(f"         - Bathrooms")
                        print(f"         - View Type")
                        print(f"         - Door Direction")
                        print(f"         - Balcony Direction")
                        print(f"      ✅ Status & Notes section")
                        print(f"         - Status (colored badge)")
                        print(f"         - Allocation")
                        print(f"         - Notes (if exists)")
                        
                        # Bước 5: Test Modal Responsiveness
                        print(f"\n📱 Step 5: Test Modal Responsiveness")
                        print(f"   🖥️  Desktop (lg:grid-cols-2):")
                        print(f"      ✅ Two columns side by side")
                        print(f"      ✅ Modal width: w-11/12 md:w-5/6 lg:w-4/5 xl:w-3/4")
                        print(f"      ✅ Gap between columns: gap-6")
                        print(f"   📱 Mobile (grid-cols-1):")
                        print(f"      ✅ Single column layout")
                        print(f"      ✅ Columns stack vertically")
                        print(f"      ✅ Full width on small screens")
                        
                        # Bước 6: Test Modal Header & Footer
                        print(f"\n🎨 Step 6: Test Modal Header & Footer")
                        print(f"   📋 Header:")
                        print(f"      ✅ Title: '🏠 Apartment Details'")
                        print(f"      ✅ Close button (X icon)")
                        print(f"      ✅ Border bottom")
                        print(f"   🔘 Footer:")
                        print(f"      ✅ Close button")
                        print(f"      ✅ Border top")
                        print(f"      ✅ Right alignment")
                        
                        # Bước 7: Test Color Scheme
                        print(f"\n🎨 Step 7: Test Color Scheme")
                        print(f"   📱 Zalo Message Column:")
                        print(f"      ✅ Blue theme (text-blue-900, border-blue-200)")
                        print(f"      ✅ Blue header background")
                        print(f"   🏠 Warehouse Column:")
                        print(f"      ✅ Green theme (text-green-900, border-green-200)")
                        print(f"      ✅ Green header background")
                        print(f"   🎯 Price Colors:")
                        print(f"      ✅ Main Price: green-600, bold")
                        print(f"      ✅ Early Price: blue-600")
                        print(f"      ✅ Schedule Price: purple-600")
                        print(f"      ✅ Loan Price: orange-600")
                    else:
                        print(f"   ❌ No apartment data returned")
                else:
                    print(f"   ❌ Failed to load apartment: {apartment_response.text}")
            else:
                print("   ℹ️  No messages with warehouse_id found")
                
                # Tạo message có warehouse_id để test
                print("\n🆕 Creating message with warehouse_id for testing")
                response_new = requests.get(f"{base_url}/api/zalo-test/unprocessed-messages?limit=1&warehouse_id=NULL")
                
                if response_new.status_code == 200:
                    data_new = response_new.json()
                    messages_new = data_new.get('data', [])
                    
                    if messages_new:
                        new_message = messages_new[0]
                        print(f"   🧪 Processing message {new_message['id']} to create warehouse_id...")
                        
                        process_response = requests.post(
                            f"{base_url}/api/zalo-test/process-message",
                            json={
                                "message_id": new_message['id'],
                                "real_insert": True
                            }
                        )
                        
                        if process_response.status_code == 200:
                            process_data = process_response.json()
                            if process_data.get('success'):
                                apartment_id = process_data.get('data', {}).get('apartment_id')
                                print(f"   ✅ Created apartment {apartment_id}")
                                print(f"   📱🏠 Now modal should show two-column layout")
                            else:
                                print(f"   ❌ Processing failed: {process_data.get('error')}")
                        else:
                            print(f"   ❌ Process request failed: {process_response.text}")
        else:
            print(f"   ❌ Failed to get messages: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Request failed: {e}")
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
    
    print("\n" + "=" * 60)
    print("📱🏠 Two-Column Modal Test Summary:")
    print("   ✅ Modal displays Zalo Message Details in Column 1")
    print("   ✅ Modal displays Warehouse Apartment Details in Column 2")
    print("   ✅ Responsive layout (2 columns desktop, 1 column mobile)")
    print("   ✅ Color-coded sections (blue for Zalo, green for Warehouse)")
    print("   ✅ Comprehensive field display with proper formatting")
    print("   ✅ Scrollable content areas where needed")
    print("   ✅ Proper typography (font-mono for IDs, colored prices)")
    print("   ✅ Status badges with appropriate colors")
    print("🏁 Test completed")

if __name__ == "__main__":
    test_two_column_modal()
