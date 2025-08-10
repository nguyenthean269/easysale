#!/usr/bin/env python3
"""
Test script cho API content generation với tham số mới
"""

import requests
import json
import time

# Cấu hình
BASE_URL = "http://localhost:5000"
LOGIN_URL = f"{BASE_URL}/auth/login"
CONTENT_GENERATE_URL = f"{BASE_URL}/content/generate"

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
    """Test API generate content với tham số mới"""
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # Test data với tham số mới
    test_data = {
        "topic": "Sản phẩm kem dưỡng da chống lão hóa",
        "loai_bai_viet": "Bài viết quảng cáo sản phẩm",
        "khach_hang_so_thich": "Làm đẹp tự nhiên, chăm sóc da",
        "khach_hang_noi_so": "Da bị lão hóa, nếp nhăn",
        "khach_hang_noi_dau": "Da khô, thiếu độ ẩm, mất đàn hồi",
        "giong_dieu": "Thân thiện, tự tin, chuyên nghiệp",
        "muc_tieu": "Thuyết phục khách hàng mua sản phẩm"
    }
    
    print(f"\n🔄 Testing content generation với tham số mới...")
    print(f"📝 Topic: {test_data['topic']}")
    print(f"📄 Loại bài viết: {test_data['loai_bai_viet']}")
    print(f"💖 Sở thích KH: {test_data['khach_hang_so_thich']}")
    print(f"😰 Nỗi sợ KH: {test_data['khach_hang_noi_so']}")
    print(f"😣 Điểm đau KH: {test_data['khach_hang_noi_dau']}")
    print(f"🎭 Giọng điệu: {test_data['giong_dieu']}")
    print(f"🎯 Mục tiêu: {test_data['muc_tieu']}")
    
    try:
        start_time = time.time()
        response = requests.post(CONTENT_GENERATE_URL, json=test_data, headers=headers)
        end_time = time.time()
        
        print(f"⏱️  Response time: {end_time - start_time:.2f} seconds")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Content generation successful!")
            
            # Hiển thị nội dung được tạo
            if 'content' in data:
                print(f"\n📄 Generated Content:")
                print("=" * 80)
                print(data['content'])
                print("=" * 80)
                
                print(f"\n📊 Response metadata:")
                for key, value in data.items():
                    if key != 'content':
                        if key == 'knowledge_sources' and value:
                            print(f"  {key}:")
                            for source in value:
                                print(f"    - {source['source']} (score: {source['score']:.3f})")
                        else:
                            print(f"  {key}: {value}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {e}")

def test_different_scenarios(access_token):
    """Test các kịch bản khác nhau"""
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    scenarios = [
        {
            "name": "Bài viết về khóa học online",
            "data": {
                "topic": "Khóa học lập trình Python online",
                "loai_bai_viet": "Bài viết giới thiệu khóa học",
                "khach_hang_so_thich": "Học lập trình, công nghệ, phát triển bản thân",
                "khach_hang_noi_so": "Không có kinh nghiệm lập trình, khó học",
                "khach_hang_noi_dau": "Thiếu kỹ năng IT, khó tìm việc",
                "giong_dieu": "Động viên, tích cực, dễ hiểu",
                "muc_tieu": "Khuyến khích đăng ký khóa học"
            }
        },
        {
            "name": "Email marketing nhà hàng",
            "data": {
                "topic": "Nhà hàng buffet hải sản cao cấp",
                "loai_bai_viet": "Email marketing khuyến mãi",
                "khach_hang_so_thich": "Ẩm thực, hải sản, không gian sang trọng",
                "khach_hang_noi_so": "Giá cả cao, chất lượng không đảm bảo",
                "khach_hang_noi_dau": "Khó tìm nhà hàng chất lượng, phù hợp gia đình",
                "giong_dieu": "Sang trọng, hấp dẫn, tin cậy",
                "muc_tieu": "Tạo cảm giác thèm ăn và muốn đặt bàn"
            }
        },
        {
            "name": "Bài đăng Facebook về du lịch",
            "data": {
                "topic": "Tour du lịch Phú Quốc 3 ngày 2 đêm",
                "loai_bai_viet": "Bài đăng mạng xã hội",
                "khach_hang_so_thich": "Du lịch, khám phá, chụp ảnh, nghỉ dưỡng",
                "khach_hang_noi_so": "Tour kém chất lượng, lừa đảo, không an toàn",
                "khach_hang_noi_dau": "Stress công việc, cần thư giãn nhưng không biết đi đâu",
                "giong_dieu": "Vui vẻ, phấn khích, tin cậy",
                "muc_tieu": "Tạo cảm hứng du lịch và đặt tour"
            }
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n🧪 Test scenario {i}: {scenario['name']}")
        print("-" * 50)
        
        try:
            response = requests.post(CONTENT_GENERATE_URL, json=scenario['data'], headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Success!")
                print(f"📄 Content preview:")
                content_preview = data['content'][:200] + "..." if len(data['content']) > 200 else data['content']
                print(content_preview)
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"Response: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request error: {e}")
        
        time.sleep(2)  # Delay giữa các request

def main():
    """Main function"""
    print("🚀 Starting Content Generation API Tests (New Parameters)")
    print("=" * 70)
    
    # Đăng nhập
    access_token = login_and_get_token()
    if not access_token:
        print("❌ Không thể đăng nhập. Exiting...")
        return
    
    # Test 1: Content generation cơ bản
    test_content_generate(access_token)
    
    # Test 2: Các kịch bản khác nhau
    test_different_scenarios(access_token)
    
    print("\n🎉 All tests completed!")

if __name__ == "__main__":
    main() 