# Quick Start - Module Crawl

## 🚀 Cài đặt nhanh

### 1. Cấu hình API key (tùy chọn)
```bash
# Kiểm tra cấu hình hiện tại
python check_firecrawl_config.py

# Thêm API key vào file .env nếu cần
echo "FIRECRAWL_API_KEY=your-api-key-here" >> .env
```

### 2. Chạy migration database
```bash
python migrate_crawl.py
```

### 3. Khởi động server
```bash
python app.py
```

### 4. Test API
```bash
python test_crawl_api.py
```

## 📝 Sử dụng API

### Đăng nhập để lấy token
```bash
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "password": "user123"}'
```

### Tạo crawl request
```bash
curl -X POST http://localhost:5000/user/crawls \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"link": "https://example.com", "crawl_tool": "firecrawl"}'
```

### Lấy danh sách crawls
```bash
curl -X GET http://localhost:5000/user/crawls \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 🔧 Cấu hình

### 1. Thêm API key vào file .env
```env
# Firecrawl API Configuration
FIRECRAWL_API_KEY=your-firecrawl-api-key-here
FIRECRAWL_API_URL=https://api.firecrawl.dev/scrape
```

### 2. Tùy chỉnh API firecrawl
Các cấu hình được lấy từ environment variables:
- `FIRECRAWL_API_KEY`: API key của firecrawl
- `FIRECRAWL_API_URL`: URL endpoint của firecrawl API

### 3. Kiểm tra cấu hình
API sẽ tự động sử dụng API key nếu có trong file `.env`. Nếu không có API key, API vẫn hoạt động nhưng có thể bị giới hạn.

## 📊 Database

Bảng `link_crawls` sẽ được tạo tự động với các trường:
- `id`: ID tự động tăng
- `link`: URL đã crawl
- `content`: Nội dung đã crawl
- `crawl_tool`: Tool sử dụng (firecrawl/watercrawl)
- `user_id`: ID của user tạo crawl
- `started_at`: Thời gian bắt đầu
- `done_at`: Thời gian kết thúc

## ⚠️ Lưu ý

1. Đảm bảo database đã được khởi tạo
2. Cần có kết nối internet để gọi API firecrawl
3. Rate limit: 10 requests/minute cho POST, 30 requests/minute cho GET
4. Chỉ user đã đăng nhập mới có thể sử dụng API 