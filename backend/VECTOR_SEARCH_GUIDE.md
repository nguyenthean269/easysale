# Vector Search với Milvus - Hướng dẫn chi tiết

## 🎯 Tổng quan

Hệ thống vector search cho phép tìm kiếm documents dựa trên semantic similarity thay vì keyword matching. Khi crawl một website, nội dung sẽ được:

1. **Chunking**: Chia thành các đoạn nhỏ (~300 từ)
2. **Embedding**: Chuyển đổi thành vector 768-dimensional
3. **Lưu trữ**: Vector được lưu trong Milvus, metadata trong MySQL
4. **Search**: Tìm kiếm vector tương tự khi user query

## 🚀 Cài đặt

### 1. Cài đặt Milvus

#### Sử dụng Docker (Khuyến nghị)
```bash
# Tải Milvus docker-compose
wget https://github.com/milvus-io/milvus/releases/download/v2.3.3/milvus-standalone-docker-compose.yml -O docker-compose.yml

# Khởi động Milvus
docker-compose up -d

# Kiểm tra status
docker-compose ps
```

#### Hoặc sử dụng pip (cho development)
```bash
pip install pymilvus
```

### 2. Cài đặt Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 3. Cấu hình Environment
Thêm vào file `.env`:
```env
# Milvus Configuration
MILVUS_HOST=localhost
MILVUS_PORT=19530
MILVUS_COLLECTION_NAME=document_chunks
MILVUS_DIMENSION=768

# Embedding Model Configuration
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

### 4. Migration Database
```bash
# Thêm trường milvus_id vào bảng document_chunks
python migrate_link_column.py
```

## 🔧 Kiến trúc hệ thống

### 1. VectorService (`utils/vector_service.py`)
- **Khởi tạo**: Load embedding model và kết nối Milvus
- **Embedding**: Chuyển đổi text thành vector
- **CRUD**: Insert, search, delete vectors trong Milvus
- **Indexing**: Tạo index cho vector search

### 2. Database Schema
```sql
-- Bảng document_chunks với trường milvus_id
CREATE TABLE document_chunks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    document_id INT NOT NULL,
    chunk_index INT NOT NULL,
    content TEXT NOT NULL,
    milvus_id VARCHAR(100) NULL,  -- ID của vector trong Milvus
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
);
```

### 3. Milvus Collection Schema
```python
fields = [
    FieldSchema(name="id", dtype=DataType.VARCHAR, is_primary=True, max_length=100),
    FieldSchema(name="document_id", dtype=DataType.INT64),
    FieldSchema(name="chunk_index", dtype=DataType.INT64),
    FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=768)
]
```

## 📝 Quy trình xử lý

### 1. Crawl và Vector Processing
```python
# 1. Crawl content từ website
firecrawl_response = call_firecrawl_api(link)

# 2. Chunking bằng Groq LLM
chunks = groq_chat.chat(prompt, "Hãy chia chunk")

# 3. Lưu vào database và tạo vector
for chunk in chunks:
    # Lưu vào MySQL
    document_chunk = DocumentChunk(...)
    db.session.add(document_chunk)
    
    # Tạo embedding và lưu vào Milvus
    milvus_id = vector_service.insert_chunk(
        document_id=document.id,
        chunk_index=chunk_index,
        content=chunk
    )
    
    # Cập nhật milvus_id trong database
    document_chunk.milvus_id = milvus_id
```

### 2. Vector Search
```python
# 1. Tạo embedding cho query
query_embedding = vector_service.create_embedding(query)

# 2. Search trong Milvus
search_results = vector_service.search_similar(
    query=query,
    top_k=5,
    document_ids=[1, 2, 3]  # Optional filter
)

# 3. Lấy metadata từ database
for result in search_results:
    chunk = DocumentChunk.query.filter_by(milvus_id=result['id']).first()
    document = Document.query.get(chunk.document_id)
```

## 🔍 API Endpoints

### 1. Crawl với Vector Processing
**POST** `/user/crawls`
```json
{
    "link": "https://example.com",
    "crawl_tool": "firecrawl"
}
```

**Response:**
```json
{
    "message": "Crawl completed successfully",
    "crawl_id": 1,
    "content_length": 1500,
    "chunks_processed": 5
}
```

### 2. Vector Search
**POST** `/user/search`
```json
{
    "query": "machine learning algorithms",
    "top_k": 5,
    "document_ids": [1, 2, 3]  // Optional
}
```

**Response:**
```json
{
    "message": "Search completed successfully",
    "query": "machine learning algorithms",
    "total_results": 3,
    "results": [
        {
            "chunk_id": 1,
            "document_id": 1,
            "document_title": "AI Wikipedia",
            "chunk_index": 2,
            "content": "Machine learning is a subset...",
            "similarity_score": 0.85,
            "source_path": "https://example.com"
        }
    ]
}
```

## 🧪 Testing

### 1. Test cơ bản
```bash
python test_vector_search.py
```

### 2. Test thủ công
```bash
# 1. Đăng nhập
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "password": "user123"}'

# 2. Crawl website
curl -X POST http://localhost:5000/user/crawls \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"link": "https://en.wikipedia.org/wiki/Artificial_intelligence"}'

# 3. Search vector
curl -X POST http://localhost:5000/user/search \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "neural networks", "top_k": 3}'
```

## ⚙️ Cấu hình nâng cao

### 1. Embedding Model
Có thể thay đổi model trong `.env`:
```env
# Các model khác nhau
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2  # 768d, nhanh
EMBEDDING_MODEL=sentence-transformers/all-mpnet-base-v2  # 768d, chính xác hơn
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L12-v2  # 384d, nhỏ hơn
```

### 2. Milvus Index
```python
# IVF_FLAT index (mặc định)
index_params = {
    "metric_type": "COSINE",
    "index_type": "IVF_FLAT",
    "params": {"nlist": 1024}
}

# HNSW index (nhanh hơn cho search)
index_params = {
    "metric_type": "COSINE",
    "index_type": "HNSW",
    "params": {"M": 16, "efConstruction": 500}
}
```

### 3. Search Parameters
```python
# Tăng độ chính xác
search_params = {
    "metric_type": "COSINE",
    "params": {"nprobe": 20}  # Tăng từ 10 lên 20
}

# Giảm thời gian search
search_params = {
    "metric_type": "COSINE",
    "params": {"nprobe": 5}  # Giảm từ 10 xuống 5
}
```

## 🔧 Troubleshooting

### 1. Milvus Connection Error
```bash
# Kiểm tra Milvus status
docker-compose ps

# Restart Milvus
docker-compose restart

# Kiểm tra logs
docker-compose logs milvus-standalone
```

### 2. Embedding Model Error
```bash
# Xóa cache model
rm -rf ~/.cache/torch/sentence_transformers/

# Reinstall sentence-transformers
pip uninstall sentence-transformers
pip install sentence-transformers
```

### 3. Memory Issues
```python
# Giảm batch size khi insert
vector_service.insert_chunk_batch(chunks, batch_size=10)

# Sử dụng model nhỏ hơn
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

## 📊 Performance Optimization

### 1. Batch Processing
```python
def insert_chunks_batch(chunks_data):
    """Insert nhiều chunks cùng lúc"""
    embeddings = []
    ids = []
    document_ids = []
    chunk_indices = []
    
    for chunk_data in chunks_data:
        embedding = vector_service.create_embedding(chunk_data['content'])
        embeddings.append(embedding)
        ids.append(str(uuid.uuid4()))
        document_ids.append(chunk_data['document_id'])
        chunk_indices.append(chunk_data['chunk_index'])
    
    # Insert batch
    data = [ids, document_ids, chunk_indices, embeddings]
    vector_service.collection.insert(data)
```

### 2. Caching
```python
# Cache embedding model
@lru_cache(maxsize=1)
def get_embedding_model():
    return SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# Cache search results
@lru_cache(maxsize=100)
def cached_search(query, top_k=5):
    return vector_service.search_similar(query, top_k)
```

### 3. Async Processing
```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

async def process_chunks_async(chunks):
    """Xử lý chunks bất đồng bộ"""
    with ThreadPoolExecutor() as executor:
        tasks = []
        for chunk in chunks:
            task = asyncio.create_task(
                asyncio.get_event_loop().run_in_executor(
                    executor, 
                    vector_service.insert_chunk,
                    chunk['document_id'],
                    chunk['chunk_index'],
                    chunk['content']
                )
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        return results
```

## 🎯 Best Practices

### 1. Chunking Strategy
- **Kích thước**: 200-400 từ mỗi chunk
- **Overlap**: 50-100 từ giữa các chunks
- **Semantic boundaries**: Chia theo câu/đoạn văn

### 2. Embedding Quality
- **Preprocessing**: Loại bỏ HTML, normalize text
- **Model selection**: Chọn model phù hợp với ngôn ngữ
- **Fine-tuning**: Fine-tune model cho domain cụ thể

### 3. Search Optimization
- **Query preprocessing**: Normalize query text
- **Filtering**: Sử dụng document_ids để filter
- **Scoring**: Kết hợp similarity score với metadata

### 4. Monitoring
```python
# Log performance metrics
import time

start_time = time.time()
results = vector_service.search_similar(query, top_k)
search_time = time.time() - start_time

logger.info(f"Search completed in {search_time:.2f}s for query: {query}")
```

## 🔮 Roadmap

### Phase 1: Basic Vector Search ✅
- [x] Milvus integration
- [x] Embedding generation
- [x] Basic search API

### Phase 2: Advanced Features
- [ ] Hybrid search (vector + keyword)
- [ ] Semantic clustering
- [ ] Auto-suggestions
- [ ] Search analytics

### Phase 3: Production Ready
- [ ] Load balancing
- [ ] Caching layer
- [ ] Monitoring dashboard
- [ ] A/B testing framework 