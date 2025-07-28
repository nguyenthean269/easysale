#!/usr/bin/env python3
import requests
import json

BASE_URL = "http://localhost:5000"

def test_login_response():
    print("🔐 Testing login response format...")
    
    login_data = {"username": "user", "password": "user123"}
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Login successful")
            print("Response keys:", list(data.keys()))
            
            # Kiểm tra các field cần thiết
            required_fields = ['message', 'access_token', 'refresh_token', 'user']
            for field in required_fields:
                if field in data:
                    print(f"✅ {field}: Present")
                else:
                    print(f"❌ {field}: Missing")
            
            # Kiểm tra user object
            if 'user' in data:
                user = data['user']
                print("User fields:", list(user.keys()))
                
                user_fields = ['id', 'username', 'full_name', 'email', 'role']
                for field in user_fields:
                    if field in user:
                        print(f"✅ user.{field}: Present")
                    else:
                        print(f"❌ user.{field}: Missing")
            
            # Hiển thị tokens
            if 'access_token' in data:
                print(f"Access token: {data['access_token'][:30]}...")
            if 'refresh_token' in data:
                print(f"Refresh token: {data['refresh_token'][:30]}...")
                
        else:
            print(f"❌ Login failed: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Is it running?")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_login_response() 