# API 404 Troubleshooting Guide

## Vấn đề: API endpoints trả về 404

### ✅ **Đã kiểm tra:**
- Routes đã được đăng ký đúng trong blueprint
- Blueprint đã được import và register trong app.py
- Tất cả endpoints cần thiết đều có sẵn

### 🔧 **Nguyên nhân có thể:**

#### 1. **App chưa được restart**
Sau khi thêm/sửa blueprints, cần restart Flask app:

```bash
# Dừng app hiện tại (Ctrl+C)
# Sau đó restart
python app.py
```

#### 2. **CORS Issues với OPTIONS requests**
Frontend gửi OPTIONS requests trước GET/POST requests. Cần đảm bảo CORS được cấu hình đúng.

#### 3. **URL mismatch**
Kiểm tra frontend có gọi đúng URL không.

### 🚀 **Giải pháp:**

#### **Bước 1: Restart App**
```bash
# Dừng app hiện tại
# Restart
python app.py
```

#### **Bước 2: Test API trực tiếp**
```bash
# Test với curl
curl -X GET http://localhost:5000/api/zalo-test/processor-status
curl -X GET http://localhost:5000/api/zalo-test/unprocessed-messages?limit=5
curl -X GET http://localhost:5000/api/zalo-test/property-tree?root_id=1
```

#### **Bước 3: Test với Python**
```bash
python test_api_endpoints.py
```

#### **Bước 4: Kiểm tra CORS**
Thêm CORS headers nếu cần:

```python
from flask_cors import CORS
CORS(app, resources={
    r"/api/*": {"origins": "*"},
    r"/warehouse/*": {"origins": "*"}
})
```

### 📋 **Routes đã được đăng ký:**

#### **Zalo Test API:**
- ✅ `/api/zalo-test/processor-status` (GET)
- ✅ `/api/zalo-test/unprocessed-messages` (GET)  
- ✅ `/api/zalo-test/property-tree` (GET)
- ✅ `/api/zalo-test/process-message` (POST)
- ✅ `/api/zalo-test/batch-process` (POST)

#### **Warehouse API:**
- ✅ `/warehouse/api/warehouse/apartments/test` (GET)
- ✅ `/warehouse/api/warehouse/apartments/single-insert` (POST)
- ✅ `/warehouse/api/warehouse/apartments/batch-insert` (POST)

### 🔍 **Debug Commands:**

#### **Kiểm tra routes:**
```bash
python test_routes_simple.py
```

#### **Kiểm tra app import:**
```bash
python -c "from app import app; print('App imported successfully')"
```

#### **Test API endpoints:**
```bash
python test_api_endpoints.py
```

### ⚠️ **Lưu ý:**

1. **OPTIONS requests**: Frontend Angular thường gửi OPTIONS requests trước actual requests
2. **CORS**: Đảm bảo CORS được cấu hình cho tất cả API endpoints
3. **Restart**: Luôn restart app sau khi thay đổi routes/blueprints
4. **URL format**: Đảm bảo frontend gọi đúng URL format

### 🎯 **Kết quả mong đợi:**

Sau khi restart app, các API endpoints sẽ hoạt động:
- ✅ `GET /api/zalo-test/processor-status` → 200 OK
- ✅ `GET /api/zalo-test/unprocessed-messages` → 200 OK  
- ✅ `GET /api/zalo-test/property-tree` → 200 OK

### 📞 **Nếu vẫn 404:**

1. Kiểm tra app có chạy đúng port không (5000)
2. Kiểm tra firewall/network issues
3. Kiểm tra frontend URL configuration
4. Kiểm tra browser developer tools để xem actual requests
