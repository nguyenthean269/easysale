# Zalo Message Processor - Test One Mode Guide

## Tổng quan

Mode `test-one` cho phép bạn test một tin nhắn cụ thể theo ID để kiểm tra quá trình xử lý với Groq API và warehouse database.

## Cách sử dụng

### 1. Sử dụng command line trực tiếp

```bash
# Test một message với ID cụ thể
python services/zalo_message_processor.py --mode test-one --message-id 123

# Ví dụ với message ID 456
python services/zalo_message_processor.py --mode test-one --message-id 456
```

### 2. Sử dụng test script

```bash
# Sử dụng test script đơn giản
python test_zalo_message_processor_one.py 123

# Ví dụ với message ID 456
python test_zalo_message_processor_one.py 456
```

### 3. Sử dụng trong code Python

```python
from services.zalo_message_processor import ZaloMessageProcessor

# Khởi tạo processor
processor = ZaloMessageProcessor()

# Test một message cụ thể
result, error = processor.run_test_one_mode(123)

if error:
    print(f"Test failed: {error}")
else:
    print(f"Test result: {result}")
```

## Kết quả trả về

Mode test-one sẽ trả về một dictionary chứa:

```python
{
    'message_id': 123,                    # ID của message
    'message_content': 'Nội dung message', # Nội dung gốc của message
    'groq_result': 'JSON response...',    # Kết quả từ Groq API
    'parsed_data': {                      # Dữ liệu đã parse từ Groq
        'unit_code': 'S1.01',
        'unit_type': 'Studio',
        'price': 2500000000,
        # ... các trường khác
    },
    'warehouse_success': True,            # Có insert/update warehouse thành công không
    'error': None                        # Lỗi nếu có
}
```

## Các trường hợp lỗi

1. **Message not found**: Message với ID không tồn tại
2. **Groq processing failed**: Lỗi khi gọi Groq API
3. **Parse failed**: Không thể parse JSON từ Groq response
4. **Warehouse failed**: Lỗi khi insert/update vào warehouse database

## Lưu ý

- Mode test-one sẽ **KHÔNG** cập nhật trạng thái message trong database
- Chỉ test quá trình xử lý, không thực sự commit dữ liệu
- Phù hợp để debug và kiểm tra logic xử lý

## Ví dụ output

```
🧪 Running in TEST-ONE mode - processing message ID: 123
🔍 Fetching message with ID: 123
✅ Found message 123: Căn hộ S1.01, Studio, 25m2, giá 2.5 tỷ...
📝 Message content: Căn hộ S1.01, Studio, 25m2, giá 2.5 tỷ...
🤖 Processing with Groq...
✅ Groq result: {"unit_code": "S1.01", "unit_type": "Studio", "area_net": 25, "price": 2500000000}
📊 Parsed apartment data: {'unit_code': 'S1.01', 'unit_type': 'Studio', 'area_net': 25, 'price': 2500000000}
🏠 Testing warehouse insert/update...
✅ Warehouse insert/update successful
✅ TEST-ONE mode completed in 2.34s
✅ Test completed successfully
📊 Result: {'message_id': 123, 'message_content': '...', 'groq_result': '...', 'parsed_data': {...}, 'warehouse_success': True}
```







