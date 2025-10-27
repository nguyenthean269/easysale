#!/usr/bin/env python3
"""
Test debug prompt để xem output
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_prompt_generation():
    """Test tạo prompt"""
    try:
        from services.zalo_message_processor import ZaloMessageProcessor
        
        # Tạo instance
        processor = ZaloMessageProcessor()
        
        # Test message
        test_message = "Bán căn hộ S4.01, tầng 15, diện tích 85m2, 2PN2WC, hướng Nam, giá 3.2 tỷ"
        
        print("=== TEST PROMPT GENERATION ===\n")
        
        # Test lấy property tree
        print("1. Property tree:")
        print("-" * 50)
        property_tree = processor.get_property_tree_for_prompt()
        print(property_tree[:500] + "..." if len(property_tree) > 500 else property_tree)
        print("\n" + "=" * 80 + "\n")
        
        # Test tạo prompt đầy đủ
        print("2. Full prompt:")
        print("-" * 50)
        
        # Lấy property tree
        property_tree = processor.get_property_tree_for_prompt()
        
        # Tạo prompt như trong code
        prompt = f"""Bạn là một AI chuyên phân tích tin nhắn rao bán căn hộ. Hãy phân tích tin nhắn dưới đây và trích xuất thông tin căn hộ dưới dạng JSON.

Tin nhắn: {test_message}

{property_tree}

<huong-dan-boc-tach>
- Nếu người dùng đề cập diện tích mà không nói là loại diện tích gì thì đó chính là diện tích tim tường.
- Nếu người dùng đề cập hướng mà không nói là hướng cửa chính hay hướng ban công thì đó chính là hướng cửa chính.
- Nếu không tìm thấy thông tin nào, trả về null cho trường đó.
- Chỉ trả về JSON, không có text giải thích nào khác.
</huong-dan-boc-tach>

Trả về JSON với format sau:
{{
    "property_group": "ID của tòa (số)",
    "unit_code": "mã căn hộ hoặc null",
    "unit_axis": "trục căn hoặc null", 
    "unit_floor_number": "tầng hoặc null",
    "area_land": "diện tích đất (số) hoặc null",
    "area_construction": "diện tích xây dựng (số) hoặc null",
    "area_net": "diện tích thông thủy (số) hoặc null",
    "area_gross": "diện tích tim tường (số) hoặc null",
    "num_bedrooms": "số phòng ngủ (số) hoặc null",
    "num_bathrooms": "số phòng tắm (số) hoặc null",
    "unit_type": "ID loại căn hộ (số) hoặc null",
    "direction_door": "hướng cửa chính (D/T/N/B/DB/DN/TB/TN) hoặc null",
    "direction_balcony": "hướng ban công (D/T/N/B/DB/DN/TB/TN) hoặc null",
    "price": "giá (số) hoặc null",
    "price_early": "giá thanh toán sớm (số) hoặc null",
    "price_schedule": "giá thanh toán theo tiến độ (số) hoặc null",
    "price_loan": "giá vay ngân hàng (số) hoặc null",
    "notes": "ghi chú hoặc null",
    "status": "trạng thái (CHUA_BAN/DA_LOCK/DA_COC/DA_BAN) hoặc null"
}}"""
        
        print(prompt)
        
    except Exception as e:
        print(f"Lỗi: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_prompt_generation()
