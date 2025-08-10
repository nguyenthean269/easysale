#!/usr/bin/env python3
"""
Test script cho API content generation
"""

import requests
import json
import time

# Cấu hình
BASE_URL = "http://localhost:5000"
LOGIN_URL = f"{BASE_URL}/auth/login"
CONTENT_GENERATE_URL = f"{BASE_URL}/content/generate"
CONTENT_STREAM_URL = f"{BASE_URL}/content/generate/stream"

def login_and_get_token():
    """Đăng nhập và lấy token"""
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        response = requests.post(LOGIN_URL, json=login_data)
        response.raise_for_status()
        
        data = response.json()
        access_token = data.get('access_token')
        
        if not access_token:
            print("❌ Không nhận được access token")
            return None
            
        print("✅ Đăng nhập thành công")
        return access_token
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Lỗi đăng nhập: {e}")
        return None

def test_content_generate(access_token):
    """Test API generate content thường"""
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # Test data
    test_data = {
        "topic": "Công nghệ AI trong năm 2024",
        "content_type": "article",
        "tone": "professional",
        "length": "medium",
        "language": "vi"
    }
    
    print(f"\n🔄 Testing content generation...")
    print(f"📝 Topic: {test_data['topic']}")
    print(f"📄 Type: {test_data['content_type']}")
    print(f"🎭 Tone: {test_data['tone']}")
    print(f"📏 Length: {test_data['length']}")
    print(f"🌐 Language: {test_data['language']}")
    
    try:
        start_time = time.time()
        response = requests.post(CONTENT_GENERATE_URL, json=test_data, headers=headers)
        end_time = time.time()
        
        print(f"⏱️  Response time: {end_time - start_time:.2f} seconds")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Content generation successful!")
            print(f"📊 Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
            
            # Hiển thị nội dung được tạo
            if 'content' in data:
                print(f"\n📄 Generated Content:")
                print("=" * 50)
                print(data['content'])
                print("=" * 50)
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {e}")

def test_content_stream(access_token):
    """Test API generate content stream"""
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # Test data
    test_data = {
        "topic": "Lợi ích của việc tập thể dục hàng ngày",
        "content_type": "blog",
        "tone": "friendly",
        "length": "short",
        "language": "vi"
    }
    
    print(f"\n🔄 Testing content generation (stream)...")
    print(f"📝 Topic: {test_data['topic']}")
    print(f"📄 Type: {test_data['content_type']}")
    print(f"🎭 Tone: {test_data['tone']}")
    print(f"📏 Length: {test_data['length']}")
    print(f"🌐 Language: {test_data['language']}")
    
    try:
        start_time = time.time()
        response = requests.post(CONTENT_STREAM_URL, json=test_data, headers=headers, stream=True)
        end_time = time.time()
        
        print(f"⏱️  Response time: {end_time - start_time:.2f} seconds")
        
        if response.status_code == 200:
            print("✅ Content stream successful!")
            print("📄 Generated Content (stream):")
            print("=" * 50)
            
            full_content = ""
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        data_str = line_str[6:]  # Remove 'data: ' prefix
                        try:
                            data = json.loads(data_str)
                            if 'chunk' in data:
                                chunk = data['chunk']
                                print(chunk, end='', flush=True)
                                full_content += chunk
                            elif 'done' in data:
                                print("\n✅ Stream completed!")
                                break
                            elif 'error' in data:
                                print(f"\n❌ Stream error: {data['error']}")
                                break
                        except json.JSONDecodeError:
                            continue
            
            print("\n" + "=" * 50)
            print(f"📊 Total content length: {len(full_content)} characters")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {e}")

def test_different_content_types(access_token):
    """Test các loại nội dung khác nhau"""
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    test_cases = [
        {
            "topic": "Quảng cáo sản phẩm điện thoại mới",
            "content_type": "product_description",
            "tone": "casual",
            "length": "short",
            "language": "vi"
        },
        {
            "topic": "Email marketing cho dịch vụ khách hàng",
            "content_type": "email",
            "tone": "professional",
            "length": "short",
            "language": "vi"
        },
        {
            "topic": "Bài đăng Facebook về du lịch",
            "content_type": "social_media",
            "tone": "friendly",
            "length": "short",
            "language": "vi"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🔄 Test case {i}: {test_case['content_type']}")
        print(f"📝 Topic: {test_case['topic']}")
        
        try:
            response = requests.post(CONTENT_GENERATE_URL, json=test_case, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Success!")
                print(f"📄 Content preview: {data['content'][:100]}...")
            else:
                print(f"❌ Error: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request error: {e}")
        
        time.sleep(1)  # Delay giữa các request

def main():
    """Main function"""
    print("🚀 Starting Content Generation API Tests")
    print("=" * 50)
    
    # Đăng nhập
    access_token = login_and_get_token()
    if not access_token:
        print("❌ Không thể đăng nhập. Exiting...")
        return
    
    # Test 1: Content generation thường
    test_content_generate(access_token)
    
    # Test 2: Content generation stream
    test_content_stream(access_token)
    
    # Test 3: Các loại nội dung khác nhau
    test_different_content_types(access_token)
    
    print("\n🎉 All tests completed!")

if __name__ == "__main__":
    main() 