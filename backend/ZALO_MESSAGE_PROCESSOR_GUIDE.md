# Zalo Message Processor Service

Service xử lý tin nhắn từ Zalo định kỳ 10 phút một lần, gửi tới Groq API để bóc tách thông tin căn hộ.

## Tính năng

- ✅ Đọc tin nhắn từ bảng `zalo_messages.received_messages` với điều kiện `status_push_warehouse = 'NOT_YET'`
- ✅ Giới hạn 20 tin nhắn mỗi lần xử lý
- ✅ Gửi tin nhắn tới Groq API (model: llama-3.1-8b-instant) để bóc tách thông tin
- ✅ Cập nhật trạng thái tin nhắn sau khi xử lý
- ✅ Chạy định kỳ 10 phút một lần
- ✅ Sử dụng threading nhẹ nhàng, ít tốn CPU
- ✅ API endpoints để quản lý service

## Cấu hình

### Environment Variables

Thêm các biến môi trường sau vào file `.env`:

```env
# Database Zalo Messages
DB_CHAT_HOST=103.6.234.59
DB_CHAT_PORT=6033
DB_CHAT_USER=easychat
DB_CHAT_PASSWORD=
DB_CHAT_NAME=zalo_messages

# Database Warehouse
DB_WAREHOUSE_HOST=103.6.234.59
DB_WAREHOUSE_PORT=6033
DB_WAREHOUSE_USER=root
DB_WAREHOUSE_PASSWORD=
DB_WAREHOUSE_NAME=warehouse

# Groq API
GROQ_API_KEY=your_groq_api_key_here
```

### Database Schema

Service sử dụng bảng `received_messages` với cấu trúc:

```sql
CREATE TABLE `received_messages` (
  `id` int NOT NULL AUTO_INCREMENT,
  `session_id` int NOT NULL,
  `config_id` int DEFAULT NULL,
  `sender_id` varchar(255) DEFAULT NULL,
  `sender_name` varchar(255) DEFAULT NULL,
  `content` text NOT NULL,
  `thread_id` varchar(255) DEFAULT NULL,
  `thread_type` varchar(50) DEFAULT NULL,
  `received_at` datetime DEFAULT NULL,
  `status_push_kafka` int DEFAULT '0',
  `status_push_warehouse` enum('NOT_YET','PUSHED') DEFAULT 'NOT_YET',
  `reply_quote` text,
  `content_hash` char(40) GENERATED ALWAYS AS (sha(`content`)) STORED,
  PRIMARY KEY (`id`),
  KEY `session_id` (`session_id`),
  KEY `config_id` (`config_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
```

## Cách sử dụng

### 1. Khởi động service

Service sẽ tự động khởi động khi chạy Flask app:

```bash
cd backend
python app.py
```

### 2. Quản lý service qua API

#### Lấy trạng thái service
```bash
GET /api/zalo-processor/status
```

Response:
```json
{
  "success": true,
  "data": {
    "is_running": true,
    "thread_alive": true,
    "interval": 600,
    "started_at": "2024-01-01T10:00:00"
  }
}
```

#### Khởi động service
```bash
POST /api/zalo-processor/start
```

#### Dừng service
```bash
POST /api/zalo-processor/stop
```

### 3. Test service

Chạy test script để kiểm tra service:

```bash
cd backend
python test_zalo_message_processor.py
```

## Cấu trúc code

```
backend/
├── services/
│   ├── __init__.py
│   └── zalo_message_processor.py    # Main service
├── app.py                           # Tích hợp service
├── test_zalo_message_processor.py   # Test script
└── ZALO_MESSAGE_PROCESSOR_GUIDE.md  # Hướng dẫn này
```

## Chi tiết implementation

### ZaloMessageProcessor Class

```python
class ZaloMessageProcessor:
    def __init__(self):
        # Khởi tạo database config và Groq client
        
    def get_unprocessed_messages(self, limit=20):
        # Lấy tin nhắn chưa xử lý từ database
        
    def process_message_with_groq(self, message_content):
        # Gửi tin nhắn tới Groq API
        
    def update_message_status(self, message_id, status):
        # Cập nhật trạng thái tin nhắn
        
    def process_messages_batch(self):
        # Xử lý một batch tin nhắn
        
    def run_scheduler(self):
        # Chạy scheduler định kỳ
        
    def start(self):
        # Khởi động service
        
    def stop(self):
        # Dừng service
```

### Workflow

1. **Scheduler chạy mỗi 10 phút**
2. **Lấy 20 tin nhắn** với `status_push_warehouse = 'NOT_YET'`
3. **Gửi từng tin nhắn** tới Groq API với prompt JSON
4. **Parse JSON response** từ Groq
5. **Map unit_type name** sang ID từ bảng `types_unit`
6. **Insert/Update** vào bảng `warehouse.apartments`
7. **Cập nhật trạng thái** tin nhắn thành `'PUSHED'` (chỉ khi warehouse thành công)
8. **Sleep** cho đến lần chạy tiếp theo

## Logging

Service sử dụng Python logging với level INFO. Logs bao gồm:

- Khởi động/dừng service
- Số lượng tin nhắn tìm thấy
- Kết quả xử lý từng tin nhắn
- Lỗi nếu có

## Xử lý lỗi

- **Database connection error**: Log lỗi và tiếp tục
- **Groq API error**: Log lỗi và bỏ qua tin nhắn đó
- **Service error**: Sleep 60 giây trước khi thử lại

## Chi tiết xử lý dữ liệu

### Groq Prompt
Service sử dụng prompt có cấu trúc để Groq trả về JSON với các trường:
- `unit_code`, `unit_axis`, `unit_floor_number`
- `area_land`, `area_construction`, `area_net`, `area_gross`
- `num_bedrooms`, `num_bathrooms`
- `unit_type` (mapped sang ID từ bảng `types_unit`)
- `direction_door`, `direction_balcony`
- `price`, `price_early`, `price_schedule`, `price_loan`
- `notes`, `status`

### Hardcode Values
- `property_group_id = 1`
- `type_view = null`
- `unit_allocation = 'QUY_CHEO'`

### Unit Type Mapping
```python
{
    'Đơn lập': 1, 'Song lập': 2, 'Tứ lập': 3, 'Tứ lập cạnh góc': 4,
    'Shophouse': 5, 'Studio': 6, '1PN': 7, '1PN+': 8,
    '2PN1WC': 9, '2PN2WC': 10, '3PN': 11, 'Đơn lập cạnh góc': 12
}
```

### Database Operations
- **Insert**: Nếu `unit_code` chưa tồn tại
- **Update**: Nếu `unit_code` đã tồn tại (trừ `property_group`)
- **Error handling**: Rollback nếu có lỗi

## Mở rộng

Service được thiết kế để dễ dàng mở rộng:

1. **Tách thành microservice**: Có thể chạy độc lập
2. **Thêm validation**: Có thể thêm validation dữ liệu trước khi insert
3. **Thêm database khác**: Dễ dàng thêm connection tới database khác
4. **Thay đổi interval**: Có thể config thời gian chạy định kỳ
5. **Thêm monitoring**: Có thể tích hợp với monitoring tools
6. **Custom mapping**: Có thể thay đổi unit_type mapping

## Troubleshooting

### Service không khởi động
- Kiểm tra environment variables
- Kiểm tra database connection
- Kiểm tra Groq API key

### Không có tin nhắn được xử lý
- Kiểm tra bảng `received_messages` có dữ liệu không
- Kiểm tra điều kiện `status_push_warehouse = 'NOT_YET'`

### Groq API lỗi
- Kiểm tra API key
- Kiểm tra quota/rate limit
- Kiểm tra network connection
