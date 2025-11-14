# Schema Update Guide

## Tổng quan
Hướng dẫn cập nhật database schema mới cho EasySale backend.

## Các thay đổi chính

### 1. Models đã được cập nhật

#### User Model
- ✅ Cập nhật `role` field với enum values: `admin`, `user`, `manager`
- ✅ Thêm indexes cho performance

#### Category Model  
- ✅ Thêm `user_id` foreign key
- ✅ Thêm `parents` field cho hierarchical categories
- ✅ Cập nhật `name` field length lên 1024 characters

#### Document Model
- ✅ Cập nhật `source_type` với enum: `pdf`, `docx`, `web`, `text`
- ✅ Thêm `created_by`, `status`, `description` fields
- ✅ Cập nhật `source_path` thành TEXT

#### DocumentChunk Model
- ✅ Thêm `source_type` và `source_ref` fields
- ✅ Cập nhật enum cho `source_type`: `document`, `message`, `post`

#### Conversation Model
- ✅ Hoàn toàn cập nhật cấu trúc
- ✅ Thêm `agent_id`, `created_by`, `source`, `chatbot_id` fields
- ✅ Thêm `conv_llm_flow_id`, `sender_id`, `chatbot_zalo_personal_id`

#### Message Model
- ✅ Đơn giản hóa cấu trúc
- ✅ Loại bỏ các fields không cần thiết

### 2. Models mới được thêm

#### AgentZaloPersonal
```python
- id, imei, cookies, phone_number, username
- status, chatbot_id, qr_code, login_status
- created_at, updated_at, avatar
```

#### CrawlLog
```python
- id, schedule_id, url, status, file_size
- error_message, created_at
```

#### LinkCrawlsSchedule
```python
- id, list_listening_url, frequency, frequency_unit
- status (active/inactive)
```

#### ZaloConfig
```python
- id, name, imei, cookies, is_default
- created_at, updated_at
```

#### ZaloSession
```python
- id, imei, cookies, created_at, is_active
- Relationships: contacts, messages, received_messages
```

#### ZaloContact
```python
- id, user_id, name, thread_type, session_id
- created_at
```

#### ZaloListenerConfig
```python
- id, config_id, status, is_enabled
- listen_friends, listen_groups, last_error
- last_activity, created_at, updated_at
```

#### ZaloMessage
```python
- id, session_id, recipient_id, recipient_name
- content, media_url, media_type, status
- sent_at, response_data
```

#### ZaloReceivedMessage
```python
- id, session_id, config_id, sender_id, sender_name
- content, thread_id, thread_type, received_at
- status_push_kafka, reply_quote, content_hash
```

## Cách chạy migration

### 1. Backup database hiện tại
```bash
mysqldump -u username -p database_name > backup.sql
```

### 2. Chạy migration script
```bash
cd backend
python migrate_new_schema.py
```

### 3. Kiểm tra kết quả
- Kiểm tra tất cả tables đã được tạo
- Test các relationships
- Verify data integrity

## Các thay đổi cần lưu ý

### 1. API Endpoints
- Có thể cần cập nhật các API endpoints để handle new fields
- Thêm validation cho new enum values
- Update response schemas

### 2. Frontend Updates
- Update TypeScript interfaces
- Handle new data structures
- Update forms và validation

### 3. Business Logic
- Update category hierarchy logic
- Implement Zalo integration features
- Add crawl scheduling functionality

## Testing

### 1. Model Testing
```bash
python test_new_models.py
```

### 2. API Testing
- Test all CRUD operations
- Verify foreign key constraints
- Check enum validations

### 3. Integration Testing
- Test Zalo integration
- Test crawl functionality
- Test conversation flows

## Rollback Plan

Nếu cần rollback:

1. Restore từ backup
2. Revert code changes
3. Re-run old migration scripts

## Support

Nếu gặp vấn đề:
1. Check database logs
2. Verify foreign key constraints
3. Check enum values compatibility
4. Review migration logs

## Next Steps

1. ✅ Update models.py
2. ✅ Test model creation
3. ✅ Create migration script
4. 🔄 Update API endpoints
5. 🔄 Update frontend interfaces
6. 🔄 Test integration
7. 🔄 Deploy to production













