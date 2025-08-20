# Content Generation API Documentation

## Tổng quan

API Content Generation sử dụng GroqChat để tạo nội dung dựa trên chủ đề được cung cấp. API hỗ trợ nhiều loại nội dung, giọng điệu và độ dài khác nhau.

## Endpoints

### 1. POST /content/generate

Tạo nội dung thông thường.

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "topic": "Chủ đề cần tạo nội dung",
  "loai_bai_viet": "Loại bài viết",           // optional
  "khach_hang_so_thich": "Sở thích khách hàng",    // optional
  "khach_hang_noi_so": "Nỗi sợ của khách hàng",    // optional
  "khach_hang_noi_dau": "Điểm đau của khách hàng",  // optional
  "giong_dieu": "Giọng điệu viết",            // optional
  "muc_tieu": "Mục tiêu của bài viết"         // optional
}
```

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `topic` | string | ✅ | - | Chủ đề cần tạo nội dung |
| `loai_bai_viet` | string | ❌ | "Bài viết thông tin" | Loại bài viết cần tạo |
| `khach_hang_so_thich` | string | ❌ | "Chưa xác định" | Sở thích của khách hàng mục tiêu |
| `khach_hang_noi_so` | string | ❌ | "Chưa xác định" | Nỗi sợ/lo lắng của khách hàng |
| `khach_hang_noi_dau` | string | ❌ | "Chưa xác định" | Điểm đau/vấn đề của khách hàng |
| `giong_dieu` | string | ❌ | "Chuyên nghiệp và thân thiện" | Giọng điệu của bài viết |
| `muc_tieu` | string | ❌ | "Cung cấp giá trị và thu hút khách hàng" | Mục tiêu của bài viết |

**Ví dụ về các tham số:**

**Loại bài viết:**
- Bài viết quảng cáo sản phẩm
- Bài viết giới thiệu dịch vụ
- Email marketing khuyến mãi
- Bài đăng mạng xã hội
- Bài viết blog chia sẻ kinh nghiệm

**Sở thích khách hàng:**
- Làm đẹp tự nhiên, chăm sóc da
- Học lập trình, công nghệ
- Du lịch, khám phá
- Ẩm thực, nấu ăn

**Nỗi sợ khách hàng:**
- Da bị lão hóa, nếp nhăn
- Không có kinh nghiệm lập trình
- Tour kém chất lượng, lừa đảo
- Giá cả cao, chất lượng không đảm bảo

**Điểm đau khách hàng:**
- Da khô, thiếu độ ẩm, mất đàn hồi
- Thiếu kỹ năng IT, khó tìm việc
- Stress công việc, cần thư giãn
- Khó tìm nhà hàng chất lượng

**Giọng điệu:**
- Thân thiện, tự tin, chuyên nghiệp
- Động viên, tích cực, dễ hiểu
- Sang trọng, hấp dẫn, tin cậy
- Vui vẻ, phấn khích, tin cậy

**Mục tiêu:**
- Chia sẻ thông tin
- Bán sản phẩm

**Response:**
```json
{
  "success": true,
  "content": "Nội dung được tạo...",
  "topic": "Chủ đề cần tạo nội dung",
  "loai_bai_viet": "Loại bài viết",
  "khach_hang_so_thich": "Sở thích khách hàng",
  "khach_hang_noi_so": "Nỗi sợ của khách hàng",
  "khach_hang_noi_dau": "Điểm đau của khách hàng",
  "giong_dieu": "Giọng điệu viết",
  "muc_tieu": "Mục tiêu của bài viết"
}
```

### 2. POST /content/generate/stream

Tạo nội dung dưới dạng stream (Server-Sent Events).

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:** (Giống như endpoint thường)

**Response:** Server-Sent Events format
```
data: {"chunk": "Phần nội dung đầu tiên..."}

data: {"chunk": "Phần nội dung tiếp theo..."}

data: {"done": true}
```

## Ví dụ sử dụng

### 1. Tạo bài viết quảng cáo kem dưỡng da

```bash
curl -X POST http://localhost:5000/content/generate \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Sản phẩm kem dưỡng da chống lão hóa",
    "loai_bai_viet": "Bài viết quảng cáo sản phẩm",
    "khach_hang_so_thich": "Làm đẹp tự nhiên, chăm sóc da",
    "khach_hang_noi_so": "Da bị lão hóa, nếp nhăn",
    "khach_hang_noi_dau": "Da khô, thiếu độ ẩm, mất đàn hồi",
    "giong_dieu": "Thân thiện, tự tin, chuyên nghiệp",
    "muc_tieu": "Bán sản phẩm"
  }'
```

### 2. Tạo email marketing nhà hàng

```bash
curl -X POST http://localhost:5000/content/generate \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Nhà hàng buffet hải sản cao cấp",
    "loai_bai_viet": "Email marketing khuyến mãi",
    "khach_hang_so_thich": "Ẩm thực, hải sản, không gian sang trọng",
    "khach_hang_noi_so": "Giá cả cao, chất lượng không đảm bảo",
    "khach_hang_noi_dau": "Khó tìm nhà hàng chất lượng, phù hợp gia đình",
    "giong_dieu": "Sang trọng, hấp dẫn, tin cậy",
    "muc_tieu": "Bán sản phẩm"
  }'
```

### 3. Tạo bài viết giới thiệu khóa học

```bash
curl -X POST http://localhost:5000/content/generate \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Khóa học lập trình Python online",
    "loai_bai_viet": "Bài viết giới thiệu khóa học",
    "khach_hang_so_thich": "Học lập trình, công nghệ, phát triển bản thân",
    "khach_hang_noi_so": "Không có kinh nghiệm lập trình, khó học",
    "khach_hang_noi_dau": "Thiếu kỹ năng IT, khó tìm việc",
    "giong_dieu": "Động viên, tích cực, dễ hiểu",
    "muc_tieu": "Bán sản phẩm"
  }'
```

### 4. Tạo bài đăng mạng xã hội về du lịch

```bash
curl -X POST http://localhost:5000/content/generate \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Tour du lịch Phú Quốc 3 ngày 2 đêm",
    "loai_bai_viet": "Bài đăng mạng xã hội",
    "khach_hang_so_thich": "Du lịch, khám phá, chụp ảnh, nghỉ dưỡng",
    "khach_hang_noi_so": "Tour kém chất lượng, lừa đảo, không an toàn",
    "khach_hang_noi_dau": "Stress công việc, cần thư giãn nhưng không biết đi đâu",
    "giong_dieu": "Vui vẻ, phấn khích, tin cậy",
    "muc_tieu": "Bán sản phẩm"
  }'
```

### 5. Tạo nội dung stream

```javascript
const eventSource = new EventSource('/content/generate/stream', {
  headers: {
    'Authorization': 'Bearer <your_token>',
    'Content-Type': 'application/json'
  }
});

eventSource.onmessage = function(event) {
  const data = JSON.parse(event.data);
  
  if (data.chunk) {
    console.log('Chunk:', data.chunk);
    // Hiển thị chunk
  } else if (data.done) {
    console.log('Stream completed');
    eventSource.close();
  } else if (data.error) {
    console.error('Error:', data.error);
    eventSource.close();
  }
};
```

## Rate Limiting

- `/content/generate`: 10 requests per minute
- `/content/generate/stream`: 5 requests per minute

## Authentication

Tất cả endpoints yêu cầu JWT token hợp lệ với role: `user`, `manager`, hoặc `admin`.

## Error Responses

### 400 Bad Request
```json
{
  "error": "Dữ liệu không được cung cấp"
}
```

### 401 Unauthorized
```json
{
  "error": "Invalid token",
  "message": "Token không hợp lệ hoặc đã hết hạn"
}
```

### 429 Too Many Requests
```json
{
  "error": "Rate limit exceeded",
  "message": "Bạn đã vượt quá giới hạn request"
}
```

### 500 Internal Server Error
```json
{
  "error": "Lỗi khi tạo nội dung",
  "message": "Chi tiết lỗi"
}
```

## Testing

Chạy file test để kiểm tra API với tham số mới:

```bash
cd backend
python test_content_generate_new.py
```

Hoặc test với tham số cũ (deprecated):

```bash
cd backend
python test_content_generate.py
```

## Lưu ý

1. API sử dụng GroqChat với model `llama-3.3-70b-versatile`
2. Nội dung được tạo là văn bản thuần túy, không có markdown
3. Stream endpoint phù hợp cho việc hiển thị nội dung real-time
4. Đảm bảo GROQ_API_KEY đã được cấu hình trong file .env 