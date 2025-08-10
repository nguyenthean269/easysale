# Crawl Update & Recrawl Guide

## 🎯 Tổng quan

Hệ thống EasySale đã được mở rộng với các tính năng mới cho phép:

1. **Sửa content của bản ghi Crawl** - Cập nhật nội dung đã crawl
2. **Crawl lại** - Tự động crawl lại từ URL gốc
3. **Tự động cập nhật chunks và Milvus** - Xóa chunks cũ và tạo chunks mới

## 🚀 API Endpoints Mới

### 1. Cập nhật Content Crawl

**PUT** `/user/crawls/<crawl_id>`

Cập nhật content của một crawl và tự động tái tạo chunks/Milvus.

#### Headers
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

#### Request Body
```json
{
    "content": "Nội dung mới đã được cập nhật..."
}
```

#### Response
```json
{
    "message": "Crawl content updated successfully",
    "crawl_id": 1,
    "document_id": 5,
    "content_length": 1500,
    "chunks_processed": 5,
    "milvus_inserts": {
        "successful": 5,
        "failed": 0,
        "total": 5
    }
}
```

### 2. Crawl Lại

**POST** `/user/crawls/<crawl_id>/recrawl`

Crawl lại content từ URL gốc và cập nhật chunks/Milvus.

#### Headers
```
Authorization: Bearer <jwt_token>
```

#### Response
```json
{
    "message": "Recrawl completed successfully",
    "crawl_id": 1,
    "document_id": 5,
    "link": "https://example.com",
    "crawl_tool": "firecrawl",
    "started_at": "2024-01-01T10:00:00",
    "done_at": "2024-01-01T10:00:05",
    "content_length": 1800,
    "chunks_processed": 6,
    "milvus_inserts": {
        "successful": 6,
        "failed": 0,
        "total": 6
    }
}
```

## 🔧 Quy trình Xử lý

### 1. Cập nhật Content

Khi gọi API update content:

1. **Cập nhật database**: Cập nhật content trong bảng `link_crawls`
2. **Tìm document tương ứng**: Tìm document có cùng `user_id`, `source_type='web'`, và `source_path`
3. **Xóa chunks cũ**: 
   - Xóa tất cả chunks trong bảng `document_chunks`
   - Xóa vectors tương ứng trong Milvus
4. **Tạo chunks mới**:
   - Sử dụng Groq LLM để chia content thành chunks
   - Lưu chunks mới vào database
   - Tạo embeddings và lưu vào Milvus
5. **Commit thay đổi**: Lưu tất cả thay đổi vào database

### 2. Crawl Lại

Khi gọi API recrawl:

1. **Crawl lại**: Gọi API firecrawl để lấy content mới
2. **Cập nhật crawl record**: Cập nhật content và thời gian trong `link_crawls`
3. **Xóa chunks cũ**: Tương tự như update content
4. **Tạo chunks mới**: Tương tự như update content
5. **Commit thay đổi**: Lưu tất cả thay đổi

## 🎨 Frontend Integration

### 1. Service Methods

```typescript
// Cập nhật content
updateCrawlContent(crawlId: number, content: string): Observable<CrawlResponse>

// Crawl lại
recrawlContent(crawlId: number): Observable<CrawlResponse>
```

### 2. Component Features

- **Edit button**: Mở modal để sửa content
- **Recrawl button**: Tự động crawl lại từ URL
- **Real-time updates**: Tự động refresh danh sách sau khi cập nhật

### 3. UI Components

- **Edit Modal**: Textarea lớn để sửa content
- **Loading states**: Hiển thị trạng thái đang xử lý
- **Success/Error messages**: Thông báo kết quả

## 🧪 Testing

### 1. Test Script

Chạy file test để kiểm tra các API mới:

```bash
cd backend
python test_crawl_update.py
```

### 2. Manual Testing

#### Test Update Content
```bash
# 1. Đăng nhập
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "password": "user123"}'

# 2. Update content
curl -X PUT http://localhost:5000/user/crawls/1 \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content": "New updated content..."}'
```

#### Test Recrawl
```bash
# Recrawl content
curl -X POST http://localhost:5000/user/crawls/1/recrawl \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 🔒 Bảo mật & Quyền

### 1. Authentication
- Tất cả API đều yêu cầu JWT token
- Token được validate qua middleware

### 2. Authorization
- **User thường**: Chỉ có thể sửa/crawl lại crawls của chính mình
- **Admin**: Có thể sửa/crawl lại tất cả crawls

### 3. Rate Limiting
- **Update content**: 10 requests per minute
- **Recrawl**: 10 requests per minute

## ⚠️ Lưu Ý Quan Trọng

### 1. Data Consistency
- Khi update/recrawl, tất cả chunks cũ sẽ bị xóa
- Chunks mới sẽ được tạo từ content mới
- Milvus vectors cũ sẽ bị xóa và tạo lại

### 2. Performance
- Quá trình xử lý có thể mất thời gian với content lớn
- Nên hiển thị loading state cho user
- Có thể xử lý bất đồng bộ trong tương lai

### 3. Error Handling
- Nếu Milvus không khả dụng, chunks vẫn được lưu trong database
- Nếu Groq LLM lỗi, API sẽ trả về error
- Database rollback nếu có lỗi xảy ra

## 🔄 Workflow Điển Hình

### 1. Sửa Content Thủ Công
```
User → Edit Content → Save → Update Database → Delete Old Chunks → Create New Chunks → Update Milvus
```

### 2. Crawl Lại Tự Động
```
User → Recrawl → Call Firecrawl API → Update Database → Delete Old Chunks → Create New Chunks → Update Milvus
```

## 📊 Monitoring

### 1. Logs
- Tất cả operations được log chi tiết
- Milvus insertion results được track
- Error handling với detailed messages

### 2. Metrics
- Content length changes
- Chunks processed count
- Milvus insertion success/failure rates
- Processing time

## 🚀 Future Enhancements

### 1. Async Processing
- Queue-based processing cho content lớn
- Background jobs cho recrawl operations
- Real-time progress updates

### 2. Version Control
- Lưu lịch sử thay đổi content
- Rollback to previous versions
- Diff view between versions

### 3. Batch Operations
- Update multiple crawls at once
- Bulk recrawl operations
- Batch chunk processing 