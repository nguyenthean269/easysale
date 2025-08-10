# CrawlService Guide

## Tổng quan

`CrawlService` là một service class được tạo ra để tái sử dụng logic chung giữa các hàm `create_crawl`, `update_crawl_content`, và `recrawl_content` trong `user.py`. Service này giúp giảm code duplication và dễ dàng maintain.

## Cấu trúc Service

### CrawlService Class

```python
class CrawlService:
    def __init__(self):
        # Khởi tạo GroqChat instance
        self.groq_chat = GroqChat(...)
```

### Các phương thức chính

#### 1. `call_firecrawl_api(link)`
- Gọi API Firecrawl để crawl nội dung từ URL
- Xử lý lỗi và fallback
- Trả về content đã crawl

#### 2. `chunk_content(content)`
- Chia content thành các chunks sử dụng Groq
- Trả về array các chunks

#### 3. `process_chunks_to_milvus(document_id, chunks)`
- Xử lý chunks và lưu vào database + Milvus
- Trả về thống kê kết quả

#### 4. `get_or_create_document(user_id, link, title=None)`
- Lấy hoặc tạo document cho một crawl
- Tránh duplicate documents

#### 5. `clear_document_chunks(document_id)`
- Xóa tất cả chunks của document từ database và Milvus

#### 6. `create_crawl(user_id, link, crawl_tool='firecrawl')`
- Tạo crawl request và xử lý content hoàn chỉnh

#### 7. `update_crawl_content(crawl_id, new_content, user_id)`
- Cập nhật content của crawl và tái tạo chunks

#### 8. `recrawl_content(crawl_id, user_id)`
- Crawl lại content từ URL và cập nhật chunks

## Lợi ích của việc refactor

### 1. Giảm Code Duplication
- Trước: ~300 dòng code trùng lặp giữa 3 hàm
- Sau: Logic chung được tách ra thành service

### 2. Dễ Maintain
- Thay đổi logic crawl chỉ cần sửa ở một nơi
- Thêm tính năng mới dễ dàng hơn

### 3. Tái sử dụng
- Service có thể được sử dụng ở nhiều nơi khác
- Test dễ dàng hơn

### 4. Separation of Concerns
- Logic business được tách khỏi route handlers
- Route handlers chỉ focus vào HTTP handling

## Cách sử dụng

### Trong route handlers

```python
@user_bp.route('/crawls', methods=['POST'])
def create_crawl():
    try:
        crawl_service = CrawlService()
        result = crawl_service.create_crawl(user_id, link, crawl_tool)
        
        return jsonify({
            'message': 'Crawl completed successfully',
            **result
        })
    except Exception as e:
        return jsonify({'error': f'Crawl failed: {str(e)}'}), 500
```

### Trong các service khác

```python
from utils.crawl_service import CrawlService

crawl_service = CrawlService()
result = crawl_service.create_crawl(user_id, link)
```

## Migration từ code cũ

### Trước (create_crawl)
```python
# ~150 dòng code với logic trùng lặp
groq_chat = GroqChat(...)
prompt = f'''...'''
response = groq_chat.chat(prompt, "Hãy chia chunk").clean()
chunks = json.loads(response)

# Xử lý chunks...
for chunk in chunks:
    # Logic xử lý chunk...
```

### Sau (sử dụng service)
```python
# ~10 dòng code
crawl_service = CrawlService()
result = crawl_service.create_crawl(user_id, link, crawl_tool)
```

## Error Handling

Service xử lý các lỗi chính:
- API Firecrawl không khả dụng → Fallback content
- Lỗi Milvus → Chunk vẫn được lưu trong database
- Lỗi Groq → Exception được raise lên route handler

## Testing

Service có thể được test độc lập:

```python
def test_crawl_service():
    service = CrawlService()
    result = service.create_crawl(user_id, "https://example.com")
    assert result['crawl_id'] is not None
    assert result['document_id'] is not None
```

## Future Improvements

1. **Async Support**: Có thể thêm async/await cho các API calls
2. **Batch Processing**: Xử lý nhiều chunks cùng lúc
3. **Retry Logic**: Tự động retry khi API fail
4. **Caching**: Cache kết quả crawl để tránh crawl lại
5. **Monitoring**: Thêm metrics và logging chi tiết hơn 