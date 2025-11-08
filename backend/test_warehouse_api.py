#!/usr/bin/env python3
"""
Test Warehouse API endpoints
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_warehouse_api():
    """Test các API endpoints của Warehouse"""
    
    print("=== TESTING WAREHOUSE API ENDPOINTS ===\n")
    
    # Test 1: Test connection
    print("1. Testing warehouse connection...")
    try:
        response = requests.get(f"{BASE_URL}/warehouse/api/warehouse/apartments/test")
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {json.dumps(data, indent=2)}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {str(e)}")
    print()
    
    # Test 2: Single insert
    print("2. Testing single apartment insert...")
    test_apartment = {
        "property_group": 1,
        "unit_type": 10,  # 2PN2WC
        "unit_code": "TEST-001",
        "unit_axis": "A",
        "unit_floor_number": 5,
        "area_land": 100.5,
        "area_construction": 85.0,
        "area_net": 75.0,
        "area_gross": 80.0,
        "num_bedrooms": 2,
        "num_bathrooms": 2,
        "type_view": "CITY_VIEW",
        "direction_door": "DN",
        "direction_balcony": "DB",
        "price": 2500000000.0,
        "price_early": 2400000000.0,
        "price_schedule": 2450000000.0,
        "price_loan": 2300000000.0,
        "notes": "Test apartment from API",
        "status": "CHUA_BAN",
        "unit_allocation": "QUY_CHEO"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/warehouse/api/warehouse/apartments/single-insert", json=test_apartment)
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {json.dumps(data, indent=2)}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {str(e)}")
    print()
    
    # Test 3: Batch insert
    print("3. Testing batch apartment insert...")
    test_apartments = [
        {
            "property_group": 1,
            "unit_type": 9,  # 2PN1WC
            "unit_code": "TEST-002",
            "unit_axis": "B",
            "unit_floor_number": 6,
            "area_land": 95.0,
            "area_construction": 80.0,
            "area_net": 70.0,
            "area_gross": 75.0,
            "num_bedrooms": 2,
            "num_bathrooms": 1,
            "direction_door": "T",
            "direction_balcony": "N",
            "price": 2200000000.0,
            "status": "CHUA_BAN"
        },
        {
            "property_group": 1,
            "unit_type": 7,  # 1PN
            "unit_code": "TEST-003",
            "unit_axis": "C",
            "unit_floor_number": 7,
            "area_land": 60.0,
            "area_construction": 50.0,
            "area_net": 45.0,
            "area_gross": 48.0,
            "num_bedrooms": 1,
            "num_bathrooms": 1,
            "direction_door": "B",
            "direction_balcony": "T",
            "price": 1800000000.0,
            "status": "DA_LOCK"
        }
    ]
    
    try:
        response = requests.post(f"{BASE_URL}/warehouse/api/warehouse/apartments/batch-insert", 
                                json={"apartments": test_apartments})
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {json.dumps(data, indent=2)}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {str(e)}")
    print()
    
    # Test 4: Test với dữ liệu thiếu trường
    print("4. Testing with missing fields (should set to NULL)...")
    incomplete_apartment = {
        "unit_code": "TEST-004",
        "unit_floor_number": 8,
        "area_gross": 65.0,
        "num_bedrooms": 1,
        "price": 1500000000.0
        # Thiếu nhiều trường khác
    }
    
    try:
        response = requests.post(f"{BASE_URL}/warehouse/api/warehouse/apartments/single-insert", json=incomplete_apartment)
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {json.dumps(data, indent=2)}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {str(e)}")
    print()
    
    # Test 5: Test với dữ liệu thừa trường (should ignore)
    print("5. Testing with extra fields (should ignore)...")
    extra_field_apartment = {
        "unit_code": "TEST-005",
        "unit_floor_number": 9,
        "area_gross": 70.0,
        "num_bedrooms": 2,
        "price": 2000000000.0,
        "extra_field_1": "This should be ignored",
        "extra_field_2": 12345,
        "invalid_field": "This should also be ignored"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/warehouse/api/warehouse/apartments/single-insert", json=extra_field_apartment)
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {json.dumps(data, indent=2)}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {str(e)}")
    print()
    
    print("=== TEST COMPLETED ===")

if __name__ == "__main__":
    test_warehouse_api()





