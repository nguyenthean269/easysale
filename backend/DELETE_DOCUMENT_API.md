# Delete Document API

API để xóa document và tất cả chunks liên quan từ cả database và Milvus vector database.

## Endpoints

### 1. GET /user/documents
Lấy danh sách documents của user hiện tại.

**Headers:**
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Response:**
```json
{
  "message": "Danh sách documents",
  "documents": [
    {
      "id": 1,
      "user_id": 1,
      "category_id": 1,
      "title": "Crawl https://example.com",
      "source_type": "web",
      "source_path": "https://example.com",
      "created_at": "2024-01-01T00:00:00",
      "updated_at": "2024-01-01T00:00:00"
    }
  ]
}
```

### 2. DELETE /user/documents/{document_id}
Xóa document và tất cả chunks liên quan.

**Headers:**
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Parameters:**
- `document_id` (integer): ID của document cần xóa

**Response:**
```json
{
  "message": "Document deleted successfully",
  "document_id": 1,
  "chunks_deleted": 5,
  "milvus_deletion": {
    "successful": 5,
    "failed": 0,
    "total": 5
  }
}
```

## Quyền truy cập

- **User thường**: Chỉ có thể xóa documents của chính mình
- **Admin**: Có thể xem tất cả documents nhưng vẫn chỉ xóa được documents của chính mình
- **Rate limit**: 10 requests per minute cho delete, 30 requests per minute cho get

## Quy trình xóa

1. **Kiểm tra quyền**: Xác minh user có quyền xóa document này không
2. **Xóa từ Milvus**: Xóa tất cả chunks của document khỏi vector database
3. **Xóa từ Database**: Xóa document và tất cả chunks liên quan khỏi database
4. **Rollback**: Nếu có lỗi, rollback toàn bộ transaction

## Error Handling

### 404 - Document not found
```json
{
  "error": "Document not found"
}
```

### 403 - Access denied
```json
{
  "error": "Access denied"
}
```

### 500 - Internal server error
```json
{
  "error": "Delete failed: <error_message>"
}
```

## Testing

Sử dụng file `test_delete_document.py` để test API:

```bash
cd backend
python test_delete_document.py
```

Script sẽ:
1. Đăng nhập với user test
2. Lấy danh sách documents
3. Hiển thị danh sách để chọn
4. Xác nhận trước khi xóa
5. Thực hiện xóa và hiển thị kết quả

## Lưu ý

- **Không thể hoàn tác**: Việc xóa document là permanent, không thể khôi phục
- **Cascade delete**: Khi xóa document, tất cả chunks liên quan sẽ bị xóa tự động
- **Milvus sync**: Đảm bảo dữ liệu trong Milvus được đồng bộ với database
- **Performance**: Xóa document lớn có thể mất thời gian do phải xóa nhiều chunks 