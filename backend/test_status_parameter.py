#!/usr/bin/env python3
"""
Test script để kiểm tra API unprocessed-messages với parameter status
"""

import requests
import json

def test_status_parameter():
    """Test API với các status khác nhau"""
    
    base_url = "http://localhost:5000/api/zalo-test"
    
    # Test các status khác nhau
    statuses = ['NOT_YET', 'PUSHED', 'ALL']
    
    for status in statuses:
        print(f"\n🧪 Testing status: {status}")
        print("=" * 50)
        
        try:
            response = requests.get(f"{base_url}/unprocessed-messages?limit=5&status={status}", timeout=10)
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Success: {data.get('success')}")
                print(f"Count: {data.get('count')}")
                print(f"Status: {data.get('status')}")
                print(f"Messages: {len(data.get('data', []))}")
                
                # Hiển thị một vài message đầu tiên
                messages = data.get('data', [])
                for i, msg in enumerate(messages[:2]):
                    print(f"  Message {i+1}: ID={msg.get('id')}, Status={msg.get('status_push_warehouse')}")
            else:
                print(f"Error: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Connection Error: Server không chạy hoặc không thể kết nối")
        except requests.exceptions.Timeout:
            print("❌ Timeout: Server không phản hồi")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_status_parameter()
