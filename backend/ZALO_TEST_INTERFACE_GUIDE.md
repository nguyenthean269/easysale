# Zalo Message Processor Test Interface

## Tổng quan

Giao diện web để test xử lý tin nhắn Zalo thay cho việc sử dụng command line với `test_zalo_message_processor_one.py`.

## Tính năng

### 1. **Processor Status**
- Hiển thị trạng thái của Zalo Message Processor
- Kiểm tra xem service có đang chạy không
- Xem interval schedule (phút)
- Kiểm tra schedule có được enable không

### 2. **Test by Message ID**
- Nhập ID của tin nhắn từ database
- Test xử lý tin nhắn cụ thể
- Hiển thị kết quả parsing và processing

### 3. **Test by Message Content**
- Nhập nội dung tin nhắn trực tiếp
- Test xử lý mà không cần có tin nhắn trong database
- Phù hợp để test prompt và Groq API

### 4. **Batch Processing**
- Xử lý nhiều tin nhắn cùng lúc
- Có thể điều chỉnh limit (số lượng tin nhắn)
- Hiển thị kết quả tổng hợp

### 5. **Unprocessed Messages**
- Hiển thị danh sách tin nhắn chưa xử lý
- Có thể test từng tin nhắn trực tiếp từ danh sách
- Refresh để cập nhật danh sách

### 6. **Property Tree**
- Hiển thị cây phân khu/tòa từ database
- Có thể thay đổi root_id để xem các nhánh khác
- Sử dụng trong prompt cho Groq

## Cách sử dụng

### Truy cập giao diện
1. Khởi động backend: `python app.py`
2. Khởi động frontend: `ng serve`
3. Truy cập: `http://localhost:4200/dashboard/zalo-test`

### Test tin nhắn
1. **Test by ID**: Nhập ID tin nhắn → Click "Test Process"
2. **Test by Content**: Nhập nội dung → Click "Test Process"
3. **Batch Test**: Điều chỉnh limit → Click "Batch Process"

### Ví dụ tin nhắn test
```
Bán căn hộ S1.01 tầng 5, diện tích 75m2, 2PN2WC, hướng Đông Nam, giá 2.5 tỷ
```

## API Endpoints

### Backend APIs (`/zalo-test/*`)

- `GET /processor-status` - Lấy trạng thái processor
- `GET /unprocessed-messages?limit=20` - Lấy tin nhắn chưa xử lý
- `GET /property-tree?root_id=1` - Lấy property tree
- `POST /process-message` - Test xử lý tin nhắn
- `POST /batch-process` - Xử lý batch tin nhắn

### Request/Response Examples

#### Test Process Message
```json
POST /zalo-test/process-message
{
  "message_content": "Bán căn hộ S1.01 tầng 5, diện tích 75m2, 2PN2WC, hướng Đông Nam, giá 2.5 tỷ"
}
```

#### Response
```json
{
  "success": true,
  "data": {
    "groq_response": "...",
    "parsed_data": {
      "property_group": "7",
      "unit_code": null,
      "unit_floor_number": 5,
      "area_gross": 75.0,
      "num_bedrooms": 2,
      "num_bathrooms": 2,
      "unit_type": "10",
      "direction_door": "DN",
      "price": 2500000000.0
    }
  },
  "message": "Successfully processed message content"
}
```

## Cấu hình

### Environment Variables
```env
# Zalo Message Processor Configuration
ZALO_MESSAGE_PROCESSOR_SCHEDULE=10  # Phút (0 = disable)
GROQ_API_KEY=your-groq-api-key-here

# Database Chat Configuration
DB_CHAT_HOST=103.6.234.59
DB_CHAT_PORT=6033
DB_CHAT_USER=easychat
DB_CHAT_PASSWORD=
DB_CHAT_NAME=zalo_messages
```

### Schedule Configuration
- `ZALO_MESSAGE_PROCESSOR_SCHEDULE=0` → Không chạy schedule
- `ZALO_MESSAGE_PROCESSOR_SCHEDULE=5` → Chạy mỗi 5 phút
- `ZALO_MESSAGE_PROCESSOR_SCHEDULE=10` → Chạy mỗi 10 phút (default)

## Troubleshooting

### Lỗi thường gặp

1. **"No module named 'pymysql'"**
   ```bash
   pip install pymysql
   ```

2. **"Working outside of application context"**
   - Đã được fix bằng cách sử dụng raw SQL connections

3. **"JSON decode error"**
   - Groq API trả về text thay vì JSON
   - Đã được fix bằng enhanced JSON parsing

4. **Frontend không load được**
   - Kiểm tra backend có chạy không
   - Kiểm tra CORS configuration
   - Kiểm tra environment variables

### Debug Commands

```bash
# Test API endpoints
python test_zalo_test_api.py

# Test processor trực tiếp
python test_zalo_message_processor_one.py --message-id 123

# Kiểm tra logs
tail -f logs/app.log
```

## So sánh với Command Line

| Tính năng | Command Line | Web Interface |
|-----------|--------------|---------------|
| Test 1 tin nhắn | ✅ | ✅ |
| Test nhiều tin nhắn | ✅ | ✅ |
| Xem kết quả | Console output | JSON + UI |
| Debug dễ dàng | ❌ | ✅ |
| Không cần code | ❌ | ✅ |
| Batch processing | ✅ | ✅ |
| Real-time status | ❌ | ✅ |
| Property tree | ❌ | ✅ |

## Kết luận

Giao diện web cung cấp cách test Zalo Message Processor trực quan và dễ sử dụng hơn so với command line, phù hợp cho:
- **Developers**: Debug và test nhanh
- **QA**: Test các trường hợp khác nhau
- **Product**: Demo và kiểm tra tính năng
- **Support**: Troubleshoot các vấn đề của khách hàng
