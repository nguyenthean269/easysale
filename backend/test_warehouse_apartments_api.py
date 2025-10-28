"""
Test script for new Warehouse Apartments API
"""

import requests
import json
import sys
import os

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

def test_warehouse_apis():
    """Test các API warehouse mới"""
    base_url = "http://localhost:5000/warehouse"
    
    print("🧪 Testing Warehouse Apartments APIs...")
    print("=" * 50)
    
    # Test 1: Get apartments list
    print("\n1️⃣ Testing GET /api/warehouse/apartments/list")
    try:
        response = requests.get(f"{base_url}/api/warehouse/apartments/list?limit=5")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success: Found {len(data.get('data', []))} apartments")
            print(f"📊 Total: {data.get('total', 0)}")
            print(f"📄 Has more: {data.get('has_more', False)}")
            
            # Show first apartment if available
            if data.get('data'):
                first_apt = data['data'][0]
                print(f"🏠 First apartment: {first_apt.get('unit_code', 'N/A')} - {first_apt.get('property_group_name', 'N/A')} - {first_apt.get('unit_type_name', 'N/A')}")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Test 2: Get apartment by ID (if we have data)
    print("\n2️⃣ Testing GET /api/warehouse/apartments/{id}")
    try:
        # First get list to find an ID
        list_response = requests.get(f"{base_url}/api/warehouse/apartments/list?limit=1")
        if list_response.status_code == 200:
            list_data = list_response.json()
            if list_data.get('data'):
                apartment_id = list_data['data'][0]['id']
                print(f"🔍 Testing with apartment ID: {apartment_id}")
                
                response = requests.get(f"{base_url}/api/warehouse/apartments/{apartment_id}")
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
                print("⚠️ No apartments found to test with")
        else:
            print(f"❌ Error getting list: {list_response.status_code}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Test 3: Search apartments
    print("\n3️⃣ Testing GET /api/warehouse/apartments/search")
    try:
        response = requests.get(f"{base_url}/api/warehouse/apartments/search?q=A&limit=3")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success: Found {len(data.get('data', []))} apartments matching 'A'")
            print(f"📊 Total matches: {data.get('total', 0)}")
            print(f"🔍 Search query: {data.get('search_query', 'N/A')}")
            
            # Show search results
            for i, apt in enumerate(data.get('data', [])[:2]):
                print(f"   {i+1}. {apt.get('unit_code', 'N/A')} - {apt.get('property_group_name', 'N/A')}")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Test 4: Filter by property_group_id
    print("\n4️⃣ Testing GET /api/warehouse/apartments/list with property_group_id filter")
    try:
        response = requests.get(f"{base_url}/api/warehouse/apartments/list?property_group_id=1&limit=3")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success: Found {len(data.get('data', []))} apartments in property_group 1")
            print(f"📊 Total in group: {data.get('total', 0)}")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Test 5: Filter by unit_type_id
    print("\n5️⃣ Testing GET /api/warehouse/apartments/list with unit_type_id filter")
    try:
        response = requests.get(f"{base_url}/api/warehouse/apartments/list?unit_type_id=1&limit=3")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success: Found {len(data.get('data', []))} apartments of unit_type 1")
            print(f"📊 Total of this type: {data.get('total', 0)}")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Testing completed!")

if __name__ == "__main__":
    test_warehouse_apis()
