"""
Test script for updated Warehouse Apartments API with list IDs
"""

import requests
import json
import sys
import os

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

def test_warehouse_apis():
    """Test các API warehouse với list IDs"""
    base_url = "http://localhost:5000/warehouse"
    
    print("🧪 Testing Updated Warehouse Apartments APIs...")
    print("=" * 60)
    
    # Test 1: Get apartments list first to get some IDs
    print("\n1️⃣ Getting apartments list to find IDs...")
    try:
        response = requests.get(f"{base_url}/api/warehouse/apartments/list?limit=5")
        if response.status_code == 200:
            data = response.json()
            apartments = data.get('data', [])
            if apartments:
                apartment_ids = [apt['id'] for apt in apartments[:3]]  # Take first 3 IDs
                print(f"✅ Found apartment IDs: {apartment_ids}")
            else:
                print("⚠️ No apartments found, using test IDs")
                apartment_ids = [1, 2, 3]  # Fallback test IDs
        else:
            print(f"❌ Error getting list: {response.status_code}")
            apartment_ids = [1, 2, 3]  # Fallback test IDs
    except Exception as e:
        print(f"❌ Exception: {e}")
        apartment_ids = [1, 2, 3]  # Fallback test IDs
    
    # Test 2: Get apartments by list of IDs
    print(f"\n2️⃣ Testing POST /api/warehouse/apartments/by-ids")
    try:
        payload = {"ids": apartment_ids}
        response = requests.post(f"{base_url}/api/warehouse/apartments/by-ids", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success: Found {len(data.get('data', []))} apartments")
            print(f"📊 Requested: {data.get('requested_count', 0)}")
            print(f"📊 Found: {data.get('found_count', 0)}")
            print(f"📊 Missing IDs: {data.get('missing_ids', [])}")
            
            # Show apartment details
            for i, apt in enumerate(data.get('data', [])[:2]):
                print(f"   {i+1}. ID: {apt.get('id')} - {apt.get('unit_code', 'N/A')} - {apt.get('property_group_name', 'N/A')}")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Test 3: Test with empty IDs array
    print(f"\n3️⃣ Testing POST /api/warehouse/apartments/by-ids with empty array")
    try:
        payload = {"ids": []}
        response = requests.post(f"{base_url}/api/warehouse/apartments/by-ids", json=payload)
        
        if response.status_code == 400:
            print("✅ Correctly rejected empty array")
        else:
            print(f"⚠️ Unexpected response: {response.status_code}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Test 4: Test with invalid data
    print(f"\n4️⃣ Testing POST /api/warehouse/apartments/by-ids with invalid data")
    try:
        payload = {"ids": "not_an_array"}
        response = requests.post(f"{base_url}/api/warehouse/apartments/by-ids", json=payload)
        
        if response.status_code == 400:
            print("✅ Correctly rejected invalid data")
        else:
            print(f"⚠️ Unexpected response: {response.status_code}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Test 5: Test with non-integer IDs
    print(f"\n5️⃣ Testing POST /api/warehouse/apartments/by-ids with non-integer IDs")
    try:
        payload = {"ids": [1, "invalid", 3]}
        response = requests.post(f"{base_url}/api/warehouse/apartments/by-ids", json=payload)
        
        if response.status_code == 400:
            print("✅ Correctly rejected non-integer IDs")
        else:
            print(f"⚠️ Unexpected response: {response.status_code}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Test 6: Test single apartment by ID (backward compatibility)
    print(f"\n6️⃣ Testing GET /api/warehouse/apartments/{{id}} (backward compatibility)")
    try:
        if apartment_ids:
            test_id = apartment_ids[0]
            response = requests.get(f"{base_url}/api/warehouse/apartments/{test_id}")
            
            if response.status_code == 200:
                data = response.json()
                apt_data = data.get('data', {})
                print(f"✅ Success: Found apartment {apt_data.get('unit_code', 'N/A')}")
                print(f"🏢 Property Group: {apt_data.get('property_group_name', 'N/A')}")
                print(f"🏠 Unit Type: {apt_data.get('unit_type_name', 'N/A')}")
            elif response.status_code == 404:
                print("❌ Apartment not found")
            else:
                print(f"❌ Error: {response.status_code} - {response.text}")
        else:
            print("⚠️ No apartment IDs available for testing")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 Testing completed!")

if __name__ == "__main__":
    test_warehouse_apis()






