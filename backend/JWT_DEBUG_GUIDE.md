# JWT Debug Guide

## Lỗi "Not enough segments"

Lỗi này thường xảy ra khi JWT token không đúng format hoặc thiếu. Dưới đây là các bước debug:

## 🔍 Các nguyên nhân có thể:

### 1. **Token không đúng format**
- Token phải có format: `Bearer <token>`
- Token phải có 3 phần: header.payload.signature

### 2. **Token bị cắt hoặc thiếu**
- Token bị cắt ngắn khi copy/paste
- Thiếu một phần của token

### 3. **Token đã hết hạn**
- JWT token có thời gian hết hạn
- Cần đăng nhập lại để lấy token mới

### 4. **Server không nhận được token**
- Header `Authorization` không được gửi đúng
- Content-Type không đúng

## 🛠️ Cách debug:

### Bước 1: Kiểm tra token
```bash
python debug_jwt.py
```

### Bước 2: Test authentication
```bash
python test_auth.py
```

### Bước 3: Kiểm tra request thủ công
```bash
# 1. Đăng nhập để lấy token
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "password": "user123"}'

# 2. Copy token từ response và test
curl -X POST http://localhost:5000/user/crawls \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"link": "https://example.com", "crawl_tool": "firecrawl"}'
```

## 📋 Checklist kiểm tra:

### ✅ Token format
- [ ] Token bắt đầu với "Bearer "
- [ ] Token có đủ 3 phần (header.payload.signature)
- [ ] Token không bị cắt ngắn

### ✅ Request headers
- [ ] Authorization header được gửi
- [ ] Content-Type: application/json (cho POST)
- [ ] Không có khoảng trắng thừa

### ✅ Server status
- [ ] Server đang chạy
- [ ] Database kết nối được
- [ ] JWT secret key được cấu hình

## 🔧 Cách sửa lỗi:

### 1. **Lấy token mới**
```bash
# Đăng nhập lại
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "password": "user123"}'
```

### 2. **Kiểm tra token format**
```python
# Token phải có format:
# Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InVzZXIiLCJyb2xlIjoidXNlciIsInVzZXJfaWQiOjIsImlhdCI6MTYzNTY3ODQwMCwiZXhwIjoxNjM1NjgyMDAwfQ.signature
```

### 3. **Test với Postman/Insomnia**
- Sử dụng tool GUI để test dễ dàng hơn
- Kiểm tra headers và body request

## 🚨 Lỗi thường gặp:

### 1. **"Not enough segments"**
- Token thiếu phần signature
- Token bị cắt ngắn

### 2. **"Invalid token"**
- Token không đúng format
- Token đã hết hạn

### 3. **"Missing token"**
- Không có Authorization header
- Header rỗng

### 4. **"Expired token"**
- Token đã hết hạn
- Cần đăng nhập lại

## 📞 Hỗ trợ:

Nếu vẫn gặp lỗi, hãy:

1. Chạy `python debug_jwt.py` và chia sẻ output
2. Kiểm tra server logs
3. Đảm bảo database có dữ liệu user
4. Kiểm tra JWT secret key trong .env file 