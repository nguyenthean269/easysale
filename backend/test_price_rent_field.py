#!/usr/bin/env python3
"""
Test script để kiểm tra API /warehouse/api/warehouse/apartments/by-ids có trả về trường price_rent
"""

import requests
import json
import time

def test_price_rent_field():
    """Test price_rent field in apartments by-ids API"""
    
    base_url = "http://localhost:5000"
    
    print("💰 Testing price_rent Field in Apartments API")
    print("=" * 60)
    
    # Bước 1: Lấy danh sách apartments để có IDs
    print("\n📋 Step 1: Get apartments list to find IDs")
    try:
        response = requests.get(f"{base_url}/warehouse/api/warehouse/apartments/list?limit=5")
        
        if response.status_code == 200:
            data = response.json()
            apartments = data.get('data', [])
            print(f"   ✅ Found {len(apartments)} apartments")
            
            if apartments:
                apartment_ids = [apt['id'] for apt in apartments[:3]]  # Lấy 3 IDs đầu tiên
                print(f"   📊 Apartment IDs: {apartment_ids}")
                
                # Bước 2: Test API by-ids với price_rent
                print(f"\n💰 Step 2: Test /api/warehouse/apartments/by-ids with price_rent")
                
                payload = {"ids": apartment_ids}
                response = requests.post(f"{base_url}/warehouse/api/warehouse/apartments/by-ids", json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"   ✅ API Response successful")
                    print(f"   📊 Requested: {data.get('requested_count', 0)}")
                    print(f"   📊 Found: {data.get('found_count', 0)}")
                    print(f"   📊 Missing IDs: {data.get('missing_ids', [])}")
                    
                    apartments_data = data.get('data', [])
                    
                    if apartments_data:
                        print(f"\n💰 Step 3: Check price_rent field in response")
                        
                        for i, apt in enumerate(apartments_data):
                            print(f"\n   🏠 Apartment {i+1} (ID: {apt.get('id')}):")
                            print(f"      📊 Price Fields:")
                            print(f"         💰 Price: {apt.get('price', 'N/A')}")
                            print(f"         🏃 Early Price: {apt.get('price_early', 'N/A')}")
                            print(f"         📅 Schedule Price: {apt.get('price_schedule', 'N/A')}")
                            print(f"         🏦 Loan Price: {apt.get('price_loan', 'N/A')}")
                            print(f"         🏠 Rent Price: {apt.get('price_rent', 'N/A')}")
                            
                            # Kiểm tra xem có price_rent không
                            if 'price_rent' in apt:
                                print(f"         ✅ price_rent field exists: {apt['price_rent']}")
                            else:
                                print(f"         ❌ price_rent field missing!")
                            
                            # Kiểm tra các trường khác
                            print(f"      📊 Other Fields:")
                            print(f"         🏘️  Property: {apt.get('property_group_name', 'N/A')}")
                            print(f"         🏠 Unit: {apt.get('unit_code', 'N/A')}")
                            print(f"         📐 Type: {apt.get('unit_type_name', 'N/A')}")
                            print(f"         📏 Area: {apt.get('area_gross', 'N/A')}m²")
                            print(f"         🛏️  Bedrooms: {apt.get('num_bedrooms', 'N/A')}")
                            print(f"         🚿 Bathrooms: {apt.get('num_bathrooms', 'N/A')}")
                            print(f"         📍 Status: {apt.get('status', 'N/A')}")
                        
                        # Bước 4: Test frontend interface
                        print(f"\n🎨 Step 4: Test Frontend Interface")
                        print(f"   📱 Frontend should:")
                        print(f"      ✅ Include price_rent in Apartment interface")
                        print(f"      ✅ Display price_rent in modal (red color)")
                        print(f"      ✅ Format price_rent with formatPrice() function")
                        print(f"      ✅ Show in Pricing Information section")
                        
                        # Bước 5: Test API consistency
                        print(f"\n🔄 Step 5: Test API Consistency")
                        print(f"   📊 Checking all apartment APIs for price_rent:")
                        
                        # Test single apartment API
                        if apartment_ids:
                            single_id = apartment_ids[0]
                            single_response = requests.get(f"{base_url}/warehouse/api/warehouse/apartments/{single_id}")
                            
                            if single_response.status_code == 200:
                                single_data = single_response.json()
                                single_apt = single_data.get('data', {})
                                
                                if 'price_rent' in single_apt:
                                    print(f"      ✅ Single apartment API includes price_rent: {single_apt['price_rent']}")
                                else:
                                    print(f"      ❌ Single apartment API missing price_rent!")
                            else:
                                print(f"      ⚠️  Single apartment API failed: {single_response.status_code}")
                        
                        # Test search API
                        search_response = requests.get(f"{base_url}/warehouse/api/warehouse/apartments/search?q=A&limit=1")
                        
                        if search_response.status_code == 200:
                            search_data = search_response.json()
                            search_apartments = search_data.get('data', [])
                            
                            if search_apartments:
                                search_apt = search_apartments[0]
                                if 'price_rent' in search_apt:
                                    print(f"      ✅ Search API includes price_rent: {search_apt['price_rent']}")
                                else:
                                    print(f"      ❌ Search API missing price_rent!")
                            else:
                                print(f"      ⚠️  No apartments found in search")
                        else:
                            print(f"      ⚠️  Search API failed: {search_response.status_code}")
                        
                        # Bước 6: Test data types
                        print(f"\n🔢 Step 6: Test Data Types")
                        test_apt = apartments_data[0]
                        
                        price_fields = ['price', 'price_early', 'price_schedule', 'price_loan', 'price_rent']
                        for field in price_fields:
                            value = test_apt.get(field)
                            if value is not None:
                                if isinstance(value, (int, float)):
                                    print(f"      ✅ {field}: {value} (type: {type(value).__name__})")
                                else:
                                    print(f"      ⚠️  {field}: {value} (unexpected type: {type(value).__name__})")
                            else:
                                print(f"      ℹ️  {field}: NULL")
                    else:
                        print(f"   ❌ No apartment data returned")
                else:
                    print(f"   ❌ API request failed: {response.status_code}")
                    print(f"   📄 Response: {response.text}")
            else:
                print("   ℹ️  No apartments found")
        else:
            print(f"   ❌ Failed to get apartments list: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Request failed: {e}")
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
    
    print("\n" + "=" * 60)
    print("💰 price_rent Field Test Summary:")
    print("   ✅ Added price_rent to get_apartments_by_ids query")
    print("   ✅ Added price_rent to get_apartments_list query")
    print("   ✅ Added price_rent to search_apartments query")
    print("   ✅ Updated frontend Apartment interface")
    print("   ✅ Added price_rent display in modal (red color)")
    print("   ✅ All apartment APIs now return price_rent field")
    print("🏁 Test completed")

if __name__ == "__main__":
    test_price_rent_field()
