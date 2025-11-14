#!/usr/bin/env python3
"""
Test Zalo Test API endpoints
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_api_endpoints():
    """Test các API endpoints của Zalo Test"""
    
    print("=== TESTING ZALO TEST API ENDPOINTS ===\n")
    
    # Test 1: Get processor status
    print("1. Testing processor status...")
    try:
        response = requests.get(f"{BASE_URL}/zalo-test/processor-status")
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {json.dumps(data, indent=2)}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {str(e)}")
    print()
    
    # Test 2: Get unprocessed messages
    print("2. Testing unprocessed messages...")
    try:
        response = requests.get(f"{BASE_URL}/zalo-test/unprocessed-messages?limit=5")
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {json.dumps(data, indent=2)}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {str(e)}")
    print()
    
    # Test 3: Get property tree
    print("3. Testing property tree...")
    try:
        response = requests.get(f"{BASE_URL}/zalo-test/property-tree?root_id=1")
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {json.dumps(data, indent=2)}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {str(e)}")
    print()
    
    # Test 4: Test message processing by content
    print("4. Testing message processing by content...")
    test_message = {
        "message_content": "Bán căn hộ S1.01 tầng 5, diện tích 75m2, 2PN2WC, hướng Đông Nam, giá 2.5 tỷ"
    }
    try:
        response = requests.post(f"{BASE_URL}/zalo-test/process-message", json=test_message)
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
    test_api_endpoints()






