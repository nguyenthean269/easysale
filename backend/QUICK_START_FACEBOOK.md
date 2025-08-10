# Quick Start - Facebook Messenger Integration

## 🚀 Bắt đầu nhanh

### 1. Cài đặt và Cấu hình

```bash
# 1. Chạy migration để tạo bảng Facebook
cd backend
python migrate_facebook.py

# 2. Thêm cấu hình Facebook vào file .env
echo "FACEBOOK_VERIFY_TOKEN=your-facebook-verify-token" >> .env
echo "FACEBOOK_APP_SECRET=your-facebook-app-secret" >> .env

# 3. Khởi động server
python app.py
```

### 2. Thiết lập Facebook App

1. **Tạo Facebook App**
   - Truy cập [Facebook Developers](https://developers.facebook.com/)
   - Tạo app mới
   - Thêm product "Messenger"

2. **Cấu hình Webhook**
   - Webhook URL: `https://your-domain.com/facebook/webhook`
   - Verify Token: `your-facebook-verify-token` (giống trong .env)
   - Subscribe to events: `messages`, `messaging_postbacks`

3. **Lấy Page Access Token**
   - Tạo page access token
   - Lưu token vào database

### 3. Thêm Facebook Page vào Database

```python
# Sử dụng API hoặc trực tiếp trong database
curl -X POST http://localhost:5000/facebook/pages \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "chatbot_id": 1,
    "page_id": "YOUR_PAGE_ID",
    "page_name": "Your Page Name",
    "page_access_token": "YOUR_PAGE_ACCESS_TOKEN",
    "status": true
  }'
```

### 4. Test Webhook

```bash
# Test webhook verification
curl "http://localhost:5000/facebook/webhook?hub.mode=subscribe&hub.verify_token=your-facebook-verify-token&hub.challenge=test_challenge"
```

### 5. Gửi tin nhắn test

```bash
# Gửi tin nhắn
curl -X POST http://localhost:5000/facebook/send-message \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "page_id": "YOUR_PAGE_ID",
    "recipient_id": "USER_ID",
    "message_text": "Hello from EasySale!"
  }'
```

### 6. Chạy Test Script

```bash
# Test toàn bộ functionality
python test_facebook_service.py
```

## 📋 API Endpoints

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET | `/facebook/webhook` | Webhook verification |
| POST | `/facebook/webhook` | Nhận tin nhắn |
| POST | `/facebook/send-message` | Gửi tin nhắn |
| POST | `/facebook/typing-indicator` | Typing indicator |
| GET | `/facebook/pages` | Lấy danh sách pages |
| POST | `/facebook/pages` | Tạo page mới |
| PUT | `/facebook/pages/{id}` | Cập nhật page |
| DELETE | `/facebook/pages/{id}` | Xóa page |

## 🔧 Cấu hình nhanh

### Environment Variables (.env)

```env
# Facebook Configuration
FACEBOOK_VERIFY_TOKEN=your-facebook-verify-token
FACEBOOK_APP_SECRET=your-facebook-app-secret

# Database (nếu chưa có)
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=easysale_db
```

### Database Tables

```sql
-- Bảng Facebook Pages
CREATE TABLE `agent_facebook_pages` (
  `id` int NOT NULL AUTO_INCREMENT,
  `chatbot_id` int DEFAULT NULL,
  `page_id` varchar(255) DEFAULT NULL,
  `page_name` text,
  `page_access_token` text,
  `status` tinyint(1) DEFAULT '1',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
);

-- Cập nhật bảng Messages
ALTER TABLE `messages` 
ADD COLUMN `facebook_message_id` varchar(255) DEFAULT NULL AFTER `zalo_message_id`;
```

## 🧪 Testing

### Test Webhook với ngrok

```bash
# 1. Cài đặt ngrok
# 2. Chạy ngrok
ngrok http 5000

# 3. Sử dụng URL ngrok làm webhook URL
# 4. Test với Facebook Webhook Tester
```

### Test với curl

```bash
# Test webhook message
curl -X POST http://localhost:5000/facebook/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "object": "page",
    "entry": [{
      "id": "PAGE_ID",
      "time": 1234567890,
      "messaging": [{
        "sender": {"id": "USER_ID"},
        "recipient": {"id": "PAGE_ID"},
        "timestamp": 1234567890,
        "message": {
          "mid": "MESSAGE_ID",
          "text": "Hello!"
        }
      }]
    }]
  }'
```

## 🚨 Troubleshooting

### Lỗi thường gặp

1. **Webhook verification failed**
   - Kiểm tra verify token có đúng không
   - Đảm bảo webhook URL accessible

2. **Message not sent**
   - Kiểm tra page access token
   - Đảm bảo page đã được approved
   - Kiểm tra recipient ID

3. **Database errors**
   - Chạy migration script
   - Kiểm tra kết nối database

### Logs

```bash
# Xem logs
tail -f logs/app.log

# Debug mode
export FLASK_DEBUG=True
python app.py
```

## 📚 Tài liệu tham khảo

- [Facebook Messenger API](https://developers.facebook.com/docs/messenger-platform)
- [Webhook Setup](https://developers.facebook.com/docs/messenger-platform/webhook)
- [Send API](https://developers.facebook.com/docs/messenger-platform/send-messages)

## 🎯 Next Steps

1. **Tích hợp AI Chatbot**
   - Kết nối với GroqService
   - Tạo auto-reply thông minh

2. **Analytics**
   - Theo dõi số lượng tin nhắn
   - Phân tích user behavior

3. **Multi-page Support**
   - Quản lý nhiều Facebook pages
   - Routing tin nhắn theo page

4. **Advanced Features**
   - Rich messages (buttons, quick replies)
   - File attachments
   - Template messages 