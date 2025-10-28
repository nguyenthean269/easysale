#!/usr/bin/env python3
"""
Test API endpoints để kiểm tra 404 issues
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_api_endpoints():
    """Test các API endpoints"""
    
    print("=== TESTING API ENDPOINTS ===\n")
    
    # Test 1: Zalo Test API endpoints
    print("1. Testing Zalo Test API endpoints...")
    zalo_test_endpoints = [
        "/api/zalo-test/processor-status",
        "/api/zalo-test/unprocessed-messages?limit=5",
        "/api/zalo-test/property-tree?root_id=1"
    ]
    
    for endpoint in zalo_test_endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            print(f"   {endpoint}: {response.status_code}")
            if response.status_code != 200:
                print(f"      Error: {response.text}")
        except Exception as e:
            print(f"   {endpoint}: Error - {str(e)}")
    print()
    
    # Test 2: Warehouse API endpoints
    print("2. Testing Warehouse API endpoints...")
    warehouse_endpoints = [
        "/warehouse/api/warehouse/apartments/test",
        "/warehouse/api/warehouse/apartments/single-insert"
    ]
    
    for endpoint in warehouse_endpoints:
        try:
            if "test" in endpoint:
                response = requests.get(f"{BASE_URL}{endpoint}")
            else:
                response = requests.post(f"{BASE_URL}{endpoint}", json={})
            print(f"   {endpoint}: {response.status_code}")
            if response.status_code not in [200, 400]:  # 400 is expected for empty data
                print(f"      Error: {response.text}")
        except Exception as e:
            print(f"   {endpoint}: Error - {str(e)}")
    print()
    
    # Test 3: Zalo Processor API endpoints
    print("3. Testing Zalo Processor API endpoints...")
    processor_endpoints = [
        "/api/zalo-processor/status",
        "/api/zalo-processor/start",
        "/api/zalo-processor/stop"
    ]
    
    for endpoint in processor_endpoints:
        try:
            if "status" in endpoint:
                response = requests.get(f"{BASE_URL}{endpoint}")
            else:
                response = requests.post(f"{BASE_URL}{endpoint}")
            print(f"   {endpoint}: {response.status_code}")
            if response.status_code != 200:
                print(f"      Error: {response.text}")
        except Exception as e:
            print(f"   {endpoint}: Error - {str(e)}")
    print()
    
    print("=== TEST COMPLETED ===")

if __name__ == "__main__":
    test_api_endpoints()
