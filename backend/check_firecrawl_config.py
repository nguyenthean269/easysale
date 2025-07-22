#!/usr/bin/env python3
"""
Script kiểm tra cấu hình Firecrawl API
"""

import os
from dotenv import load_dotenv

def check_firecrawl_config():
    """Kiểm tra cấu hình firecrawl API"""
    print("🔍 Kiểm tra cấu hình Firecrawl API")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Kiểm tra API key
    api_key = os.getenv('FIRECRAWL_API_KEY', '')
    api_url = os.getenv('FIRECRAWL_API_URL', 'https://api.firecrawl.dev/scrape')
    
    print(f"📋 FIRECRAWL_API_URL: {api_url}")
    
    if api_key:
        print(f"✅ FIRECRAWL_API_KEY: {'*' * (len(api_key) - 4) + api_key[-4:] if len(api_key) > 4 else '*' * len(api_key)}")
        print("   API key đã được cấu hình")
    else:
        print("❌ FIRECRAWL_API_KEY: Không được cấu hình")
        print("   ⚠️  API sẽ hoạt động không có authentication")
        print("   💡 Thêm FIRECRAWL_API_KEY vào file .env để sử dụng API key")
    
    print("\n📝 Cách thêm API key:")
    print("1. Mở file .env")
    print("2. Thêm dòng: FIRECRAWL_API_KEY=your-api-key-here")
    print("3. Lưu file và khởi động lại server")
    
    return bool(api_key)

def test_api_connection():
    """Test kết nối đến firecrawl API"""
    print("\n🌐 Test kết nối API...")
    
    try:
        import requests
        from flask import Flask
        from config import get_config
        
        # Tạo app context để test
        app = Flask(__name__)
        app.config.from_object(get_config())
        
        with app.app_context():
            from routes.user import call_firecrawl_api
            
            # Test với một URL đơn giản
            test_url = "https://httpbin.org/html"
            print(f"   Testing với URL: {test_url}")
            
            result = call_firecrawl_api(test_url)
            
            if result.get('status') == 'success':
                print("   ✅ API call thành công")
                print(f"   📄 Content length: {len(result.get('content', ''))} characters")
            else:
                print("   ❌ API call thất bại")
                
    except Exception as e:
        print(f"   ❌ Lỗi khi test API: {str(e)}")
        print("   💡 Kiểm tra lại API key và kết nối internet")

if __name__ == "__main__":
    has_api_key = check_firecrawl_config()
    
    if has_api_key:
        print("\n🚀 API key đã được cấu hình, có thể test kết nối...")
        response = input("Bạn có muốn test kết nối API không? (y/n): ")
        if response.lower() in ['y', 'yes']:
            test_api_connection()
    else:
        print("\n⚠️  Vui lòng cấu hình API key trước khi test")
    
    print("\n✅ Kiểm tra hoàn tất!") 