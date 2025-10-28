#!/usr/bin/env python3
"""
Test Zalo Test API sau khi sửa lỗi method
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_zalo_test_api():
    """Test Zalo Test API endpoints"""
    
    print("=== TESTING ZALO TEST API ===\n")
    
    # Test 1: Processor Status
    print("1. Testing processor status...")
    try:
        response = requests.get(f"{BASE_URL}/api/zalo-test/processor-status")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {json.dumps(data, indent=2)}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Exception: {str(e)}")
    print()
    
    # Test 2: Unprocessed Messages
    print("2. Testing unprocessed messages...")
    try:
        response = requests.get(f"{BASE_URL}/api/zalo-test/unprocessed-messages?limit=5")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {json.dumps(data, indent=2)}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Exception: {str(e)}")
    print()
    
    # Test 3: Property Tree
    print("3. Testing property tree...")
    try:
        response = requests.get(f"{BASE_URL}/api/zalo-test/property-tree?root_id=1")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {json.dumps(data, indent=2)}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Exception: {str(e)}")
    print()
    
    # Test 4: Process Message (Test với tin nhắn mẫu)
    print("4. Testing process message...")
    test_message = {
        "message_content": "Bán căn hộ S1.01 tầng 5, diện tích 85m2, giá 3.2 tỷ",
        "message_id": 999999  # ID test
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/zalo-test/process-message", 
                              json=test_message,
                              headers={'Content-Type': 'application/json'})
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {json.dumps(data, indent=2)}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Exception: {str(e)}")
    print()
    
    print("=== TEST COMPLETED ===")

def test_warehouse_api():
    """Test Warehouse API endpoints"""
    
    print("=== TESTING WAREHOUSE API ===\n")
    
    # Test 1: Test Connection
    print("1. Testing warehouse connection...")
    try:
        response = requests.get(f"{BASE_URL}/warehouse/api/warehouse/apartments/test")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {json.dumps(data, indent=2)}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Exception: {str(e)}")
    print()
    
    # Test 2: Single Insert
    print("2. Testing single apartment insert...")
    test_apartment = {
        "property_group": 7,
        "unit_type": 1,
        "unit_code": "TEST-001",
        "unit_floor_number": 5,
        "area_gross": 85.5,
        "price": 3200000000,
        "status": "CHUA_BAN"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/warehouse/api/warehouse/apartments/single-insert",
                               json=test_apartment,
                               headers={'Content-Type': 'application/json'})
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {json.dumps(data, indent=2)}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Exception: {str(e)}")
    print()
    
    print("=== WAREHOUSE TEST COMPLETED ===")

if __name__ == "__main__":
    print("🚀 Starting API tests...")
    print("Make sure Flask app is running on http://localhost:5000")
    print()
    
    # Wait a bit for user to see the message
    time.sleep(2)
    
    test_zalo_test_api()
    test_warehouse_api()
    
    print("\n✅ All tests completed!")
    print("If you see 404 errors, make sure to restart the Flask app:")
    print("1. Stop the current app (Ctrl+C)")
    print("2. Run: python app.py")
