# Knowledge Integration Guide

## Tổng quan

Tính năng tích hợp tri thức (Knowledge Integration) cho phép API Content Generation sử dụng thông tin từ vector database để làm phong phú nội dung được tạo ra.

## Cách hoạt động

### 1. Luồng xử lý
```
Topic → Vector Search → Knowledge Context → AI Prompt → Generated Content
```

1. **Input**: Người dùng nhập chủ đề (topic)
2. **Vector Search**: Hệ thống tìm kiếm 5 documents liên quan nhất trong vector database
3. **Knowledge Context**: Trích xuất nội dung từ các documents tìm được
4. **AI Prompt**: Kết hợp tri thức với thông tin khách hàng để tạo prompt
5. **Generated Content**: AI tạo nội dung dựa trên prompt đã được làm phong phú

### 2. Vector Search Implementation

```python
def search_knowledge(topic):
    """
    Tìm kiếm tri thức liên quan trong vector database
    """
    try:
        vector_service = get_vector_service()
        
        # Thực hiện vector search với topic
        search_results = vector_service.search_similar(
            query=topic,
            top_k=5,  # Lấy top 5 kết quả liên quan nhất
            document_ids=None
        )
        
        # Lấy nội dung chi tiết từ database
        knowledge_chunks = []
        for result in search_results:
            chunk = DocumentChunk.query.filter_by(milvus_id=result['id']).first()
            if chunk:
                document = Document.query.get(chunk.document_id)
                if document:
                    knowledge_chunks.append({
                        'content': chunk.content,
                        'source': document.title,
                        'similarity_score': result['score']
                    })
        
        return knowledge_chunks
        
    except Exception as e:
        print(f"Warning: Failed to search knowledge: {e}")
        return []
```

### 3. Prompt Enhancement

Prompt được làm phong phú bằng cách thêm section "TRI THỨC THAM KHẢO":

```python
knowledge_section = ""
if knowledge_context and len(knowledge_context) > 0:
    knowledge_section = "\nTRI THỨC THAM KHẢO:\n"
    for i, chunk in enumerate(knowledge_context, 1):
        knowledge_section += f"[Nguồn {i}: {chunk['source']}]\n{chunk['content'][:500]}{'...' if len(chunk['content']) > 500 else ''}\n\n"
    knowledge_section += "Hãy sử dụng tri thức tham khảo trên để làm phong phú nội dung, nhưng đừng copy nguyên văn. Hãy diễn giải và kết hợp một cách tự nhiên.\n"
```

## API Response

Response bây giờ bao gồm thông tin về tri thức được sử dụng:

```json
{
  "success": true,
  "content": "Nội dung được tạo...",
  "topic": "Chủ đề",
  "loai_bai_viet": "Loại bài viết",
  "khach_hang_so_thich": "Sở thích KH",
  "khach_hang_noi_so": "Nỗi sợ KH",
  "khach_hang_noi_dau": "Điểm đau KH",
  "giong_dieu": "Giọng điệu",
  "muc_tieu": "Mục tiêu",
  "knowledge_sources": [
    {
      "source": "Document Title 1",
      "score": 0.85
    },
    {
      "source": "Document Title 2", 
      "score": 0.78
    }
  ]
}
```

## Frontend Integration

### 1. Service Update
```typescript
export interface ContentGenerateResponse {
  // ... existing fields
  knowledge_sources: Array<{source: string, score: number}>;
}
```

### 2. UI Display
- Hiển thị danh sách nguồn tri thức được sử dụng
- Hiển thị điểm similarity score dưới dạng phần trăm
- Styling với màu xanh để phân biệt với metadata khác

## Lợi ích

### 1. Nội dung phong phú hơn
- AI có thêm ngữ cảnh để tạo nội dung chi tiết
- Thông tin chính xác từ documents đã được crawl
- Giảm thiểu hallucination của AI

### 2. Tính nhất quán
- Nội dung được tạo dựa trên tri thức có sẵn trong hệ thống
- Đảm bảo tính chính xác của thông tin

### 3. Transparency
- Người dùng biết được nguồn thông tin được sử dụng
- Điểm similarity score giúp đánh giá độ liên quan

## Configuration

### 1. Vector Search Parameters
```python
top_k = 5  # Số lượng documents liên quan nhất
max_content_length = 500  # Giới hạn độ dài nội dung trong prompt
```

### 2. Error Handling
- Nếu vector search thất bại, hệ thống vẫn hoạt động bình thường
- Log warning nhưng không dừng quá trình tạo nội dung

## Testing

### 1. Test với tri thức
```bash
# Test với topic có trong database
curl -X POST http://localhost:5000/content/generate \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Công nghệ AI trong marketing"
  }'
```

### 2. Test không có tri thức
```bash
# Test với topic không có trong database
curl -X POST http://localhost:5000/content/generate \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Chủ đề hoàn toàn mới không có trong database"
  }'
```

## Monitoring

### 1. Logs
- Search knowledge success/failure
- Number of knowledge chunks found
- Similarity scores

### 2. Metrics
- Knowledge utilization rate
- Average similarity scores
- Impact on content quality

## Best Practices

### 1. Content Preparation
- Crawl documents có chất lượng cao
- Đảm bảo documents được chunk hợp lý
- Cập nhật vector database thường xuyên

### 2. Prompt Engineering
- Hướng dẫn AI sử dụng tri thức một cách tự nhiên
- Tránh copy nguyên văn
- Khuyến khích diễn giải và kết hợp

### 3. Quality Control
- Monitor similarity scores
- Review generated content quality
- Adjust top_k parameter if needed

## Troubleshooting

### 1. Không tìm thấy tri thức
- Kiểm tra vector database có documents không
- Verify vector search service hoạt động
- Check similarity threshold

### 2. Chất lượng tri thức thấp
- Review document crawling quality
- Adjust chunking strategy
- Update embedding model

### 3. Performance Issues
- Monitor vector search response time
- Consider caching for frequent topics
- Optimize database queries 