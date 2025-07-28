# Document & Crawl Management Guide

## Tổng quan

Tính năng Document & Crawl Management đã được tích hợp vào trang dashboard/users của frontend, cung cấp giao diện để quản lý documents và thực hiện crawl dữ liệu từ các website.

## Các tính năng chính

### 1. Documents Tab
- **Xem danh sách documents**: Hiển thị tất cả documents đã được tạo
- **Xem chi tiết document**: Click "View" để xem thông tin chi tiết và các chunks
- **Xóa document**: Xóa document và tất cả chunks liên quan
- **Retry Milvus**: Thử lại việc insert chunks vào Milvus nếu bị lỗi

### 2. Crawl Tab
- **Tạo crawl mới**: Nhập URL và chọn crawl tool (firecrawl/watercrawl)
- **Xem danh sách crawls**: Hiển thị tất cả crawls đã thực hiện
- **Xem chi tiết crawl**: Xem nội dung đã crawl được

### 3. Search Tab
- **Vector search**: Tìm kiếm documents bằng vector similarity
- **Tùy chỉnh kết quả**: Chọn số lượng kết quả (top_k)
- **Lọc theo document**: Chỉ tìm kiếm trong các document cụ thể

## Cách sử dụng

### Tạo crawl mới
1. Chuyển đến tab "Crawl"
2. Nhập URL cần crawl (phải bắt đầu bằng http:// hoặc https://)
3. Chọn crawl tool (mặc định là firecrawl)
4. Click "Start Crawl"
5. Đợi quá trình crawl hoàn thành

### Tìm kiếm documents
1. Chuyển đến tab "Search"
2. Nhập từ khóa tìm kiếm
3. Tùy chỉnh số lượng kết quả (1-20)
4. Tùy chọn: Nhập document IDs để lọc (phân cách bằng dấu phẩy)
5. Click "Search"

### Quản lý documents
1. Chuyển đến tab "Documents"
2. Xem danh sách documents
3. Click "View" để xem chi tiết
4. Click "Retry Milvus" nếu chunks chưa được insert vào Milvus
5. Click "Delete" để xóa document

## API Endpoints được sử dụng

### Crawl APIs
- `POST /user/crawls` - Tạo crawl mới
- `GET /user/crawls` - Lấy danh sách crawls
- `GET /user/crawls/{id}` - Lấy chi tiết crawl

### Document APIs
- `GET /user/documents` - Lấy danh sách documents
- `GET /user/documents/{id}` - Lấy chi tiết document
- `DELETE /user/documents/{id}` - Xóa document
- `POST /user/documents/{id}/retry-milvus` - Retry Milvus inserts

### Search API
- `POST /user/search` - Vector search

## Lưu ý

1. **Authentication**: Tất cả API calls đều yêu cầu JWT token
2. **Rate Limiting**: Các API có giới hạn số lượng request
3. **Permissions**: User chỉ có thể truy cập documents/crawls của chính mình (trừ admin)
4. **Milvus Integration**: Documents được chia thành chunks và lưu vào Milvus để vector search

## Troubleshooting

### Crawl không thành công
- Kiểm tra URL có hợp lệ không
- Kiểm tra kết nối internet
- Kiểm tra API key của firecrawl (nếu có)

### Search không có kết quả
- Kiểm tra documents đã được crawl và lưu vào Milvus chưa
- Thử retry Milvus inserts cho document
- Kiểm tra từ khóa tìm kiếm

### Lỗi authentication
- Kiểm tra JWT token có hợp lệ không
- Đăng nhập lại nếu cần thiết 