#!/usr/bin/env python3
"""
Demo hoàn chỉnh với property groups và unit types từ database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def demo_complete_system():
    """Demo hệ thống hoàn chỉnh"""
    try:
        from app import app
        from utils.property_service import PropertyService
        from services.zalo_message_processor import ZaloMessageProcessor
        
        with app.app_context():
            print("=== DEMO HỆ THỐNG HOÀN CHỈNH ===\n")
            
            # Test message
            test_message = "Bán căn hộ S4.01, tầng 15, diện tích 85m2, 2PN2WC, hướng Nam, giá 3.2 tỷ"
            
            print(f"Test message: {test_message}")
            print("\n" + "="*80 + "\n")
            
            # Test 1: Property tree với unit types
            print("1. Property tree với unit types từ database:")
            print("-" * 50)
            property_tree = PropertyService.get_property_tree_for_prompt(1)
            print(property_tree)
            print("\n" + "="*80 + "\n")
            
            # Test 2: Prompt hoàn chỉnh
            print("2. Prompt hoàn chỉnh cho Groq:")
            print("-" * 50)
            
            processor = ZaloMessageProcessor()
            prompt = f"""
            Hãy phân tích tin nhắn rao bán căn hộ dưới đây và trích xuất thông tin căn hộ dưới dạng JSON, sử dụng tri thức trong cặp thẻ XML <thong-tin-du-an></thong-tin-du-an>, hướng dẫn bóc tách trong cặp thẻ XML <huong-dan-boc-tach></huong-dan-boc-tach>.
            
            Tin nhắn: {test_message}
            
            Trả về JSON với các trường sau (chỉ trả về JSON, không có text khác):
            {{
                "property_group": "Xác định ID của tòa mà người dùng đang có căn hộ rao bán",
                "unit_code": "mã căn hộ nếu có",
                "unit_axis": "trục căn nếu có", 
                "unit_floor_number": "tầng nếu có",
                "area_land": "diện tích đất nếu có (số)",
                "area_construction": "diện tích xây dựng nếu có (số)",
                "area_net": "diện tích thông thủy nếu có (số)",
                "area_gross": "diện tích tim tường nếu có (số)",
                "num_bedrooms": "số phòng ngủ nếu có (số)",
                "num_bathrooms": "số phòng tắm nếu có (số)",
                "unit_type": "ID của loại căn hộ",
                "direction_door": "hướng cửa chính. enum('D','T','N','B','DB','DN','TB','TN')",
                "direction_balcony": "hướng ban công. enum('D','T','N','B','DB','DN','TB','TN')",
                "price": "giá nếu có (số)",
                "price_early": "giá thanh toán sớm nếu có (số)",
                "price_schedule": "giá thanh toán theo tiến độ nếu có (số)",
                "price_loan": "giá vay ngân hàng nếu có (số)",
                "notes": "ghi chú nếu có",
                "status": "trạng thái nếu có (CHUA_BAN, DA_LOCK, DA_COC, DA_BAN)"
            }}

            {property_tree}

            <huong-dan-boc-tach>
            - Nếu người dùng đề cập diện tích mà không nói là loại diện tích gì thì đó chính là diện tích tim tường.
            - Nếu người dùng đề cập hướng mà không nói là hướng cửa chính hay hướng ban công thì đó chính là hướng cửa chính.
            - Nếu không tìm thấy thông tin nào, trả về null cho trường đó.
            </huong-dan-boc-tach>
            
            
            """
            
            print(prompt)
            
    except Exception as e:
        print(f"Lỗi: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    demo_complete_system()
