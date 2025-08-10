# Facebook Messenger Integration Guide

## Tổng quan

Hệ thống EasySale đã được tích hợp với Facebook Messenger API để hỗ trợ chatbot tự động. Tích hợp này bao gồm:

- **Webhook API**: Nhận tin nhắn từ Facebook Messenger
- **Send Message API**: Gửi tin nhắn qua Facebook Messenger
- **Database Integration**: Lưu trữ tin nhắn và thông tin trang Facebook
- **Security**: Xác thực webhook và chữ ký

## Cấu trúc Database

### Bảng `agent_facebook_pages`

```sql
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
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb3
```

### Cập nhật bảng `messages`

Bảng `messages` đã được cập nhật với cột `facebook_message_id`:

```sql
ALTER TABLE `messages` 
ADD COLUMN `facebook_message_id` varchar(255) DEFAULT NULL AFTER `zalo_message_id`
```

## Cài đặt và Cấu hình

### 1. Cài đặt Dependencies

Đảm bảo các thư viện cần thiết đã được cài đặt:

```bash
pip install requests flask-cors
```

### 2. Cấu hình Environment Variables

Thêm các biến môi trường vào file `.env`:

```env
# Facebook Configuration
FACEBOOK_VERIFY_TOKEN=your-facebook-verify-token
FACEBOOK_APP_SECRET=your-facebook-app-secret
```

### 3. Chạy Migration

Chạy script migration để tạo bảng và cập nhật database:

```bash
cd backend
python migrate_facebook.py
```

## API Endpoints

### 1. Webhook Verification

**Endpoint:** `GET /facebook/webhook`

**Mô tả:** Xác thực webhook với Facebook

**Parameters:**
- `hub.mode`: Chế độ xác thực (thường là "subscribe")
- `hub.verify_token`: Token xác thực
- `hub.challenge`: Challenge string từ Facebook

**Response:**
- `200`: Xác thực thành công, trả về challenge string
- `403`: Xác thực thất bại

### 2. Webhook Message Receiver

**Endpoint:** `POST /facebook/webhook`

**Mô tả:** Nhận tin nhắn từ Facebook Messenger

**Headers:**
- `X-Hub-Signature-256`: Chữ ký webhook (nếu có app secret)

**Request Body:** JSON từ Facebook Messenger API

**Response:**
```json
{
  "success": true,
  "message": "Successfully processed 1 messages",
  "processed_messages": 1
}
```

### 3. Send Message

**Endpoint:** `POST /facebook/send-message`

**Mô tả:** Gửi tin nhắn qua Facebook Messenger

**Headers:**
- `Authorization`: Bearer token

**Request Body:**
```json
{
  "page_id": "123456789012345",
  "recipient_id": "987654321098765",
  "message_text": "Hello from EasySale!",
  "conversation_id": 123
}
```

**Response:**
```json
{
  "success": true,
  "message": "Message sent successfully",
  "facebook_message_id": "mid.1234567890abcdef"
}
```

### 4. Typing Indicator

**Endpoint:** `POST /facebook/typing-indicator`

**Mô tả:** Gửi chỉ báo đang nhập

**Request Body:**
```json
{
  "page_id": "123456789012345",
  "recipient_id": "987654321098765",
  "typing": true
}
```

### 5. Facebook Pages Management

#### Get All Pages
**Endpoint:** `GET /facebook/pages`

#### Get Specific Page
**Endpoint:** `GET /facebook/pages/{page_id}`

#### Create Page
**Endpoint:** `POST /facebook/pages`

**Request Body:**
```json
{
  "chatbot_id": 1,
  "page_id": "123456789012345",
  "page_name": "My Facebook Page",
  "page_access_token": "your-page-access-token",
  "status": true
}
```

#### Update Page
**Endpoint:** `PUT /facebook/pages/{page_id}`

#### Delete Page
**Endpoint:** `DELETE /facebook/pages/{page_id}`

### 6. Conversation Messages

**Endpoint:** `GET /facebook/conversations/{conversation_id}/messages`

**Mô tả:** Lấy tin nhắn của một cuộc hội thoại

## Facebook Service

### Các phương thức chính

#### 1. `verify_webhook(mode, token, challenge, verify_token)`
Xác thực webhook với Facebook

#### 2. `verify_signature(signature, body, app_secret)`
Xác thực chữ ký webhook

#### 3. `get_page_access_token(page_id)`
Lấy page access token từ database

#### 4. `get_or_create_conversation(sender_id, page_id)`
Tạo hoặc lấy cuộc hội thoại hiện có

#### 5. `save_message_to_db(conversation_id, sender_id, content, facebook_message_id, message_type)`
Lưu tin nhắn vào database

#### 6. `process_webhook_message(data)`
Xử lý dữ liệu webhook từ Facebook

#### 7. `send_message(page_id, recipient_id, message_text, conversation_id)`
Gửi tin nhắn qua Facebook Messenger API

#### 8. `send_typing_indicator(page_id, recipient_id, typing)`
Gửi chỉ báo đang nhập

## Cách sử dụng

### 1. Thiết lập Facebook App

1. Tạo Facebook App tại [Facebook Developers](https://developers.facebook.com/)
2. Thêm Messenger product
3. Tạo Page Access Token
4. Cấu hình webhook URL: `https://your-domain.com/facebook/webhook`

### 2. Thêm Facebook Page vào Database

```python
from models import FacebookPage
from flask import Flask

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'your-database-uri'
db.init_app(app)

with app.app_context():
    page = FacebookPage(
        chatbot_id=1,
        page_id="your-page-id",
        page_name="Your Page Name",
        page_access_token="your-page-access-token",
        status=True
    )
    db.session.add(page)
    db.session.commit()
```

### 3. Gửi tin nhắn

```python
from utils.facebook_service import FacebookService

fb_service = FacebookService()
result = fb_service.send_message(
    page_id="your-page-id",
    recipient_id="user-id",
    message_text="Hello from EasySale!"
)

if result['success']:
    print(f"Message sent: {result['facebook_message_id']}")
else:
    print(f"Error: {result['message']}")
```

### 4. Xử lý tin nhắn đến

Tin nhắn đến sẽ được tự động xử lý thông qua webhook và lưu vào database. Bạn có thể truy vấn tin nhắn:

```python
from models import Message, Conversation

# Lấy cuộc hội thoại
conversation = Conversation.query.filter_by(
    thread_id="fb_your-page-id_user-id",
    thread_type="facebook"
).first()

# Lấy tin nhắn
messages = Message.query.filter_by(
    conversation_id=conversation.id
).order_by(Message.created_at.asc()).all()
```

## Testing

### Chạy Test Script

```bash
cd backend
python test_facebook_service.py
```

### Test Migration

```bash
# Chạy migration
python migrate_facebook.py

# Rollback (nếu cần)
python migrate_facebook.py --rollback
```

## Bảo mật

### 1. Webhook Verification
- Sử dụng verify token để xác thực webhook
- Cấu hình app secret để xác thực chữ ký

### 2. Access Token Security
- Lưu trữ page access token an toàn trong database
- Không expose token trong logs hoặc error messages

### 3. Rate Limiting
- API endpoints đã được tích hợp với rate limiting
- Cấu hình giới hạn request phù hợp

## Troubleshooting

### 1. Webhook không nhận được tin nhắn
- Kiểm tra webhook URL có đúng không
- Đảm bảo page access token hợp lệ
- Kiểm tra logs để xem lỗi

### 2. Không gửi được tin nhắn
- Kiểm tra page access token
- Đảm bảo page đã được approved
- Kiểm tra recipient ID có đúng không

### 3. Database errors
- Chạy migration script
- Kiểm tra kết nối database
- Xem logs để debug

## Logs và Monitoring

### Log Levels
- `INFO`: Thông tin hoạt động bình thường
- `ERROR`: Lỗi cần xử lý
- `WARNING`: Cảnh báo

### Monitoring
- Theo dõi số lượng tin nhắn được xử lý
- Kiểm tra tỷ lệ lỗi
- Monitor database performance

## Ví dụ sử dụng hoàn chỉnh

### 1. Auto-reply Bot

```python
from utils.facebook_service import FacebookService
from models import Message, Conversation

class FacebookAutoReplyBot:
    def __init__(self):
        self.fb_service = FacebookService()
    
    def handle_incoming_message(self, webhook_data):
        # Xử lý webhook
        result = self.fb_service.process_webhook_message(webhook_data)
        
        if result['success'] and result['processed_messages'] > 0:
            # Tìm tin nhắn mới nhất
            for entry in webhook_data['entry']:
                for messaging in entry['messaging']:
                    sender_id = messaging['sender']['id']
                    page_id = messaging['recipient']['id']
                    
                    # Gửi auto-reply
                    self.send_auto_reply(sender_id, page_id)
    
    def send_auto_reply(self, sender_id, page_id):
        # Gửi typing indicator
        self.fb_service.send_typing_indicator(page_id, sender_id, True)
        
        # Gửi tin nhắn
        reply_text = "Cảm ơn bạn đã liên hệ! Chúng tôi sẽ phản hồi sớm nhất."
        result = self.fb_service.send_message(page_id, sender_id, reply_text)
        
        # Tắt typing indicator
        self.fb_service.send_typing_indicator(page_id, sender_id, False)
        
        return result
```

### 2. Integration với Chatbot AI

```python
from utils.facebook_service import FacebookService
from utils.groq_service import GroqService

class FacebookAIBot:
    def __init__(self):
        self.fb_service = FacebookService()
        self.ai_service = GroqService()
    
    def handle_message(self, webhook_data):
        # Xử lý webhook
        result = self.fb_service.process_webhook_message(webhook_data)
        
        if result['success']:
            # Lấy tin nhắn cuối cùng
            for entry in webhook_data['entry']:
                for messaging in entry['messaging']:
                    if 'message' in messaging:
                        sender_id = messaging['sender']['id']
                        page_id = messaging['recipient']['id']
                        message_text = messaging['message']['text']
                        
                        # Tạo AI response
                        ai_response = self.ai_service.generate_response(message_text)
                        
                        # Gửi response
                        self.fb_service.send_message(page_id, sender_id, ai_response)
```

## Kết luận

Tích hợp Facebook Messenger đã được hoàn thành với đầy đủ tính năng:

- ✅ Webhook nhận tin nhắn
- ✅ API gửi tin nhắn
- ✅ Lưu trữ database
- ✅ Bảo mật và xác thực
- ✅ Testing và documentation
- ✅ Error handling
- ✅ Logging và monitoring

Hệ thống sẵn sàng để triển khai và sử dụng trong production. 