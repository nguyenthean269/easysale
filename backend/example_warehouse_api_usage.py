"""
Ví dụ sử dụng API Warehouse Apartments với list IDs
"""

import requests
import json

def example_usage():
    """Ví dụ cách sử dụng API mới"""
    
    base_url = "http://localhost:5000/warehouse"
    
    print("📚 Ví dụ sử dụng Warehouse Apartments API với list IDs")
    print("=" * 60)
    
    # Ví dụ 1: Lấy nhiều apartments cùng lúc
    print("\n1️⃣ Lấy nhiều apartments cùng lúc:")
    print("POST /api/warehouse/apartments/by-ids")
    print("Body: {\"ids\": [1, 2, 3, 4, 5]}")
    
    payload = {"ids": [1, 2, 3, 4, 5]}
    try:
        response = requests.post(f"{base_url}/api/warehouse/apartments/by-ids", json=payload)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Thành công: Tìm thấy {data.get('found_count', 0)}/{data.get('requested_count', 0)} apartments")
            print(f"📊 Missing IDs: {data.get('missing_ids', [])}")
        else:
            print(f"❌ Lỗi: {response.status_code}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Ví dụ 2: Response format
    print("\n2️⃣ Format response:")
    example_response = {
        "success": True,
        "data": [
            {
                "id": 1,
                "property_group": 1,
                "property_group_name": "Vinhomes Smart City",
                "unit_type": 1,
                "unit_type_name": "Đơn lập",
                "unit_code": "A101",
                "unit_axis": "A",
                "unit_floor_number": 1,
                "area_gross": 85.5,
                "price": 3200000000,
                "status": "CHUA_BAN"
            }
        ],
        "requested_count": 1,
        "found_count": 1,
        "missing_ids": []
    }
    print(json.dumps(example_response, indent=2, ensure_ascii=False))
    
    # Ví dụ 3: So sánh với API cũ
    print("\n3️⃣ So sánh với API cũ:")
    print("API cũ (single ID):")
    print("GET /api/warehouse/apartments/1")
    print("→ Trả về 1 apartment")
    
    print("\nAPI mới (list IDs):")
    print("POST /api/warehouse/apartments/by-ids")
    print("Body: {\"ids\": [1, 2, 3]}")
    print("→ Trả về nhiều apartments cùng lúc")
    
    # Ví dụ 4: Use cases thực tế
    print("\n4️⃣ Use cases thực tế:")
    use_cases = [
        "Lấy thông tin nhiều căn hộ đã được user bookmark",
        "Hiển thị danh sách căn hộ trong giỏ hàng",
        "Lấy thông tin căn hộ trong một tòa nhà cụ thể",
        "So sánh nhiều căn hộ cùng lúc",
        "Export dữ liệu nhiều căn hộ"
    ]
    
    for i, use_case in enumerate(use_cases, 1):
        print(f"   {i}. {use_case}")
    
    # Ví dụ 5: Performance benefits
    print("\n5️⃣ Lợi ích về performance:")
    benefits = [
        "Giảm số lượng HTTP requests",
        "Giảm latency khi cần nhiều apartments",
        "Batch processing hiệu quả hơn",
        "Giảm tải cho database server"
    ]
    
    for i, benefit in enumerate(benefits, 1):
        print(f"   {i}. {benefit}")
    
    print("\n" + "=" * 60)
    print("🎯 API đã sẵn sàng sử dụng!")

if __name__ == "__main__":
    example_usage()





