# Crawl API Documentation

## Tổng quan

Module crawl cho phép người dùng crawl nội dung từ các website thông qua API firecrawl và lưu trữ kết quả vào database.

## API Endpoints

### 1. Tạo Crawl Request

**POST** `/user/crawls`

Tạo một crawl request mới và gọi API firecrawl để lấy nội dung.

#### Headers
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

#### Request Body
```json
{
    "link": "https://example.com",
    "crawl_tool": "firecrawl"
}
```

#### Parameters
- `link` (required): URL cần crawl
- `crawl_tool` (optional): Tool sử dụng để crawl. Mặc định là "firecrawl". Các giá trị hợp lệ: "firecrawl", "watercrawl"

#### Response
```json
{
    "message": "Crawl completed successfully",
    "crawl_id": 1,
    "link": "https://example.com",
    "crawl_tool": "firecrawl",
    "started_at": "2024-01-01T10:00:00",
    "done_at": "2024-01-01T10:00:05",
    "content_length": 1500
}
```

### 2. Lấy Danh Sách Crawls

**GET** `/user/crawls`

Lấy danh sách tất cả crawls của user hiện tại (hoặc tất cả nếu là admin).

#### Headers
```
Authorization: Bearer <jwt_token>
```

#### Response
```json
{
    "message": "Danh sách crawls",
    "crawls": [
        {
            "id": 1,
            "link": "https://example.com",
            "content": "Nội dung đã crawl...",
            "crawl_tool": "firecrawl",
            "user_id": 1,
            "started_at": "2024-01-01T10:00:00",
            "done_at": "2024-01-01T10:00:05"
        }
    ]
}
```

### 3. Lấy Chi Tiết Crawl

**GET** `/user/crawls/<crawl_id>`

Lấy chi tiết của một crawl cụ thể.

#### Headers
```
Authorization: Bearer <jwt_token>
```

#### Response
```json
{
    "message": "Chi tiết crawl",
    "crawl": {
        "id": 1,
        "link": "https://example.com",
        "content": "Nội dung đã crawl...",
        "crawl_tool": "firecrawl",
        "user_id": 1,
        "started_at": "2024-01-01T10:00:00",
        "done_at": "2024-01-01T10:00:05"
    }
}
```

## Database Schema

### Bảng `link_crawls`

```sql
CREATE TABLE link_crawls (
    id INT AUTO_INCREMENT PRIMARY KEY,
    link INT NOT NULL,
    content LONGTEXT NOT NULL,
    crawl_tool ENUM('firecrawl','watercrawl') NOT NULL,
    user_id INT NOT NULL,
    started_at DATETIME NOT NULL,
    done_at DATETIME NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

## Quyền Truy Cập

- **User thường**: Chỉ có thể xem và tạo crawls của chính mình
- **Admin**: Có thể xem tất cả crawls của tất cả users

## Rate Limiting

- **POST /user/crawls**: 10 requests per minute
- **GET /user/crawls**: 30 requests per minute

## Cấu Hình Firecrawl API

### Environment Variables

Thêm các biến môi trường vào file `.env`:

```env
# Firecrawl API Configuration
FIRECRAWL_API_KEY=your-firecrawl-api-key-here
FIRECRAWL_API_URL=https://api.firecrawl.dev/scrape
```

### API Configuration

- **URL**: Có thể tùy chỉnh qua `FIRECRAWL_API_URL` (mặc định: `https://api.firecrawl.dev/scrape`)
- **Method**: POST
- **Content-Type**: application/json
- **Authorization**: Bearer token (nếu có API key)

### Payload mẫu:
```json
{
    "url": "https://example.com",
    "pageOptions": {
        "onlyMainContent": true
    }
}
```

### Headers mẫu:
```json
{
    "Content-Type": "application/json",
    "Authorization": "Bearer YOUR_API_KEY"
}
```

## Lỗi Thường Gặp

### 1. Link không hợp lệ
```json
{
    "error": "Link is required"
}
```

### 2. Crawl tool không hợp lệ
```json
{
    "error": "crawl_tool must be either \"firecrawl\" or \"watercrawl\""
}
```

### 3. API call thất bại
```json
{
    "error": "Crawl failed: API call failed: Connection timeout"
}
```

### 4. Không có quyền truy cập
```json
{
    "error": "Access denied"
}
```

## Testing

Chạy file test để kiểm tra API:

```bash
python test_crawl_api.py
```

## Ví Dụ Sử Dụng

### 1. Tạo crawl với curl
```bash
curl -X POST http://localhost:5000/user/crawls \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "link": "https://example.com",
    "crawl_tool": "firecrawl"
  }'
```

### 2. Lấy danh sách crawls
```bash
curl -X GET http://localhost:5000/user/crawls \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### 3. Lấy chi tiết crawl
```bash
curl -X GET http://localhost:5000/user/crawls/1 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Lưu Ý

1. Đảm bảo server đang chạy trước khi test API
2. Cần đăng nhập để lấy JWT token
3. API firecrawl có thể cần API key tùy theo cấu hình
4. Nội dung crawl được lưu dưới dạng text trong database
5. Thời gian crawl được ghi lại chính xác từ lúc bắt đầu đến lúc kết thúc 