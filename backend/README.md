# EasySale Flask Backend

## Yêu cầu
- Python 3.8+
- MySQL
- Redis (tùy chọn, cho production)

## Cấu trúc thư mục
```
easysale/
├── app.py                 # Main application file
├── models.py              # Database models
├── config.py              # Configuration management
├── database.sql           # Database schema
├── init_db.py            # Database initialization script
├── create_env.py         # Environment setup script
├── env.example           # Environment variables template
├── requirements.txt       # Python dependencies
├── README.md             # Documentation
├── test_api.py           # Basic API tests
├── test_rate_limit.py    # Rate limiting tests
├── test_permissions.py   # Permission system tests
├── test_config.py        # Configuration tests
├── test_retry_after.py   # Rate limit retry after tests
├── test_crawl_update.py  # Crawl update & recrawl tests
├── routes/               # API routes
│   ├── __init__.py
│   ├── auth.py           # Authentication routes
│   ├── admin.py          # Admin routes
│   └── user.py           # User routes
└── utils/                # Utility functions
    ├── __init__.py
    ├── rate_limit.py     # Rate limiting utilities
    ├── permissions.py    # Permission management utilities
    ├── groq_service.py   # Groq LLM integration
    └── vector_service.py # Milvus vector operations
```

## Cài đặt
```bash
# Tạo virtual environment
python -m venv venv

# Kích hoạt virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Cài đặt dependencies
pip install -r requirements.txt
```

## Dependencies
- **Flask**: Web framework
- **Flask-SQLAlchemy**: ORM cho database
- **Flask-JWT-Extended**: JWT authentication
- **Flask-Limiter**: Rate limiting
- **Flask-Migrate**: Database migrations
- **Flask-CORS**: Cross-origin resource sharing
- **Werkzeug**: Password hashing
- **requests**: HTTP client (cho testing)
- **python-dotenv**: Environment variables management

## Cấu hình Environment

### 1. Tạo file .env
```bash
# Tự động tạo file .env từ template
python create_env.py
```

### 2. Cấu hình Database
Chỉnh sửa file `.env` với thông tin MySQL của bạn:
```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=easysale_db
```

### 3. Cấu hình JWT
```env
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
```

### 4. Tạo Database
```sql
CREATE DATABASE easysale_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

## Khởi tạo DB
Có 2 cách để khởi tạo database:

### Cách 1: Sử dụng script tự động
```bash
python init_db.py
```

### Cách 2: Sử dụng Flask-Migrate
```bash
flask db init
flask db migrate
flask db upgrade
```

## Chạy server
```bash
python app.py
```

## Testing

### Test API cơ bản
```bash
python test_api.py
```

### Test Rate Limiting chi tiết
```bash
python test_rate_limit.py
```

### Test Permission System
```bash
python test_permissions.py
```

### Test Configuration
```bash
python test_config.py
```

### Test Rate Limit Retry After
```bash
python test_retry_after.py
```

### Test thủ công với curl
```bash
# Test đăng ký
curl -X POST http://localhost:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "test123",
    "email": "test@example.com",
    "full_name": "Test User"
  }'

# Test đăng nhập
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'

# Test rate limit status
curl -X GET http://localhost:5000/auth/rate-limit-status
```

## API Endpoints

### Authentication
- `POST /auth/register` - Đăng ký tài khoản mới
  ```json
  {
    "username": "newuser",
    "password": "password123",
    "email": "user@example.com",
    "full_name": "Nguyễn Văn A",
    "phone": "0123456789"
  }
  ```

- `POST /auth/login` - Đăng nhập
  ```json
  {
    "username": "admin",
    "password": "admin123"
  }
  ```

- `GET /auth/profile` - Lấy thông tin profile (cần JWT token)
- `GET /auth/permissions` - Lấy danh sách permissions của user (cần JWT token)
- `GET /auth/rate-limit-status` - Kiểm tra trạng thái rate limit

### Response Headers
Khi gọi API, bạn sẽ nhận được các headers sau:
- `X-RateLimit-Limit`: Giới hạn request
- `X-RateLimit-Remaining`: Số request còn lại
- `X-RateLimit-Reset`: Thời gian reset

### Rate Limit Error Response
Khi vượt quá giới hạn, API sẽ trả về:
```json
{
  "error": "Rate limit exceeded",
  "message": "Bạn đã vượt quá giới hạn request. Vui lòng thử lại sau 45 giây.",
  "retry_after": 45,
  "limit": "5 per minute",
  "limit_info": {
    "limit": "5 per minute",
    "remaining": 0,
    "reset_time": 1640995200
  }
}
```

**Các trường trong response:**
- `error`: Loại lỗi
- `message`: Thông báo chi tiết với thời gian cụ thể
- `retry_after`: Số giây cần chờ trước khi thử lại
- `limit`: Giới hạn đã bị vượt quá
- `limit_info`: Thông tin chi tiết về rate limit

### Admin Routes
- `GET /admin/dashboard` - Dashboard admin (cần role admin)
- `GET /admin/users` - Danh sách tất cả users (cần role admin/manager)
- `GET /admin/users/<id>` - Thông tin user theo ID (cần role admin/manager)
- `PUT /admin/users/<id>` - Cập nhật thông tin user (cần role admin)
- `DELETE /admin/users/<id>` - Xóa user (cần role admin)

### User Routes
- `GET /user/profile` - Profile user (cần authentication)
- `PUT /user/profile` - Cập nhật profile của chính mình (cần authentication)
- `GET /user/users/<id>` - Thông tin profile (ownership check)

## Tài khoản mẫu
- **Admin**: username: `admin`, password: `admin123`
- **User**: username: `user`, password: `user123`

## Rate Limiting

### Giới hạn theo API
| API Endpoint | Giới hạn | Mô tả |
|--------------|----------|-------|
| `POST /auth/register` | 5/phút, 20/giờ | Đăng ký tài khoản |
| `POST /auth/login` | 10/phút, 50/giờ | Đăng nhập |
| `GET /auth/profile` | 30/phút | Lấy thông tin profile |
| `GET /admin/dashboard` | 60/phút | Dashboard admin |
| `GET /user/profile` | 30/phút | Profile user |
| `GET /auth/rate-limit-status` | 10/phút | Kiểm tra rate limit |

### Giới hạn mặc định
- **200 requests/ngày** cho tất cả API
- **50 requests/giờ** cho tất cả API

### Cách hoạt động
- Rate limiting được tính theo **IP address**
- Giới hạn được reset sau mỗi khoảng thời gian
- Có thể mở rộng để sử dụng user ID cho authenticated requests
- Storage sử dụng memory (có thể thay đổi thành Redis cho production)

## Tính năng mới
✅ **Chức năng đăng ký** với validation:
- Kiểm tra email hợp lệ
- Kiểm tra mật khẩu mạnh (tối thiểu 6 ký tự)
- Kiểm tra username và email không trùng lặp
- Hash mật khẩu an toàn

✅ **Cập nhật database schema** với các trường:
- email, full_name, phone
- is_active, created_at, updated_at
- Validation và error handling

✅ **Rate Limiting** để bảo vệ API:
- **Register**: 5 requests/phút, 20 requests/giờ
- **Login**: 10 requests/phút, 50 requests/giờ
- **Profile**: 30 requests/phút
- **Admin Dashboard**: 60 requests/phút
- **Default**: 200 requests/ngày, 50 requests/giờ
- Error handling cho rate limit exceeded
- Endpoint kiểm tra rate limit status
- Custom utility functions cho rate limiting nâng cao

✅ **Permission System** để kiểm soát quyền truy cập:
- **Role-based access control**: admin, manager, user
- **Permission-based access**: user:read, user:write, user:delete
- **Ownership-based access**: Kiểm tra quyền sở hữu resource
- **Decorator system**: @require_roles(), @require_permissions(), @require_ownership()
- **Granular permissions**: Kiểm soát chi tiết từng API endpoint

## Permission System

### Roles và Permissions
| Role | Permissions | Mô tả |
|------|-------------|-------|
| **admin** | user:read, user:write, user:delete, admin:read, admin:write, admin:delete, system:read, system:write, system:delete | Quyền tối cao |
| **manager** | user:read, user:write, admin:read, system:read | Quyền quản lý |
| **user** | user:read, user:write | Quyền cơ bản |

### Sử dụng Decorators

#### 1. Role-based Access Control
```python
from utils.permissions import require_roles

@require_roles('admin')
def admin_only_function():
    # Chỉ admin mới truy cập được
    pass

@require_roles('admin', 'manager')
def admin_manager_function():
    # Admin hoặc manager mới truy cập được
    pass
```

#### 2. Permission-based Access Control
```python
from utils.permissions import require_permissions

@require_permissions('user:read')
def read_user_data():
    # Cần permission user:read
    pass

@require_permissions('user:write', 'user:delete')
def modify_user_data():
    # Cần cả user:write và user:delete
    pass
```

#### 3. Ownership-based Access Control
```python
from utils.permissions import require_ownership

@require_ownership('user')
def user_profile(user_id):
    # Chỉ chủ sở hữu hoặc admin mới truy cập được
    pass
```

### Utility Functions
```python
from utils.permissions import is_admin, is_owner, has_permission

# Kiểm tra trong code
if is_admin():
    # Logic cho admin
    pass

if is_owner(user_id):
    # Logic cho chủ sở hữu
    pass

if has_permission('user:delete'):
    # Logic cho user có quyền xóa
    pass
```

### Error Responses
```json
{
  "error": "Forbidden",
  "message": "Bạn cần có quyền admin để truy cập API này"
}
```

## Tùy chỉnh Rate Limiting

### Thay đổi giới hạn cho API cụ thể
Chỉnh sửa decorator trong file route tương ứng:
```python
# Ví dụ: thay đổi rate limit cho register
@auth_bp.route('/register', methods=['POST'])
@limiter.limit("10 per minute")  # Thay đổi từ 5 thành 10
@limiter.limit("50 per hour")    # Thay đổi từ 20 thành 50
def register():
    # ... code ...
```

### Sử dụng Redis storage (cho production)
```python
# Trong app.py
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    storage_uri="redis://localhost:6379"  # Thay đổi storage
)
```

### Custom key function
```python
# Tạo key dựa trên user ID thay vì IP
def get_user_key():
    try:
        identity = get_jwt_identity()
        return f"user:{identity.get('user_id')}"
    except:
        return f"ip:{request.remote_addr}"

# Sử dụng trong route
@limiter.limit("30 per minute", key_func=get_user_key)
def some_route():
    # ... code ...
```

### Sử dụng utility functions
```python
from utils.rate_limit import user_rate_limit, ip_rate_limit

# Rate limit dựa trên user ID
@user_rate_limit("30 per minute")
def authenticated_route():
    # ... code ...

# Rate limit dựa trên IP
@ip_rate_limit("10 per minute")
def public_route():
    # ... code ...
```

## Troubleshooting

### Lỗi thường gặp

#### 1. Rate limit không hoạt động
- Kiểm tra Flask-Limiter đã được cài đặt: `pip install Flask-Limiter`
- Kiểm tra import limiter trong route files
- Restart server sau khi thay đổi cấu hình

#### 2. Rate limit quá nghiêm ngặt
- Giảm giới hạn trong decorator
- Tăng thời gian window (ví dụ: "per hour" thay vì "per minute")

#### 3. Rate limit không reset
- Kiểm tra storage backend (memory/Redis)
- Đảm bảo server không restart giữa chừng

#### 4. Test rate limiting
```bash
# Test nhanh với nhiều request
for i in {1..10}; do
  curl -X POST http://localhost:5000/auth/register \
    -H "Content-Type: application/json" \
    -d '{"username":"test'$i'","password":"test123","email":"test'$i'@example.com","full_name":"Test"}'
  echo "Request $i completed"
done
```

### Monitoring Rate Limits
- Sử dụng endpoint `/auth/rate-limit-status` để kiểm tra
- Theo dõi headers `X-RateLimit-*` trong response
- Log rate limit violations để phân tích

### Best Practices
1. **Phân biệt rate limit theo loại API**:
   - Public APIs: Giới hạn thấp hơn
   - Authenticated APIs: Giới hạn cao hơn
   - Admin APIs: Giới hạn cao nhất

2. **Sử dụng Redis cho production**:
   - Memory storage sẽ mất khi restart server
   - Redis cho phép scale across multiple servers

3. **Custom error messages**:
   - Thông báo rõ ràng cho user
   - Hướng dẫn thời gian retry

4. **Monitoring và alerting**:
   - Theo dõi rate limit violations
   - Alert khi có dấu hiệu tấn công

## Deployment

### Development
```bash
# Chạy với debug mode
python app.py
```

### Production
```bash
# Sử dụng Gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Hoặc sử dụng uWSGI
pip install uwsgi
uwsgi --http 0.0.0.0:5000 --module app:app --processes 4
```

### Environment Variables
Tất cả cấu hình được quản lý qua file `.env`:

```env
# Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=easysale_db

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True

# Rate Limiting
RATE_LIMIT_STORAGE_URI=memory://

# Server Configuration
HOST=0.0.0.0
PORT=5000
```

### Tạo file .env
```bash
python create_env.py
```

### Docker (tùy chọn)
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

## Tính năng Crawl & Vector Search

### Crawl Management
Hệ thống hỗ trợ crawl nội dung từ website và tự động xử lý vector search:

#### API Endpoints
- **POST** `/user/crawls` - Tạo crawl mới
- **GET** `/user/crawls` - Lấy danh sách crawls
- **GET** `/user/crawls/<id>` - Lấy chi tiết crawl
- **PUT** `/user/crawls/<id>` - Cập nhật content crawl
- **POST** `/user/crawls/<id>/recrawl` - Crawl lại từ URL

#### Vector Processing
- Tự động chia content thành chunks (~300 từ)
- Tạo embeddings sử dụng sentence-transformers
- Lưu vectors trong Milvus cho semantic search
- Hỗ trợ search tương tự với **POST** `/user/search`

### Document Management
- **GET** `/user/documents` - Lấy danh sách documents
- **GET** `/user/documents/<id>` - Lấy chi tiết document
- **DELETE** `/user/documents/<id>` - Xóa document
- **POST** `/user/documents/<id>/retry-milvus` - Retry Milvus inserts

### Cấu hình Milvus
```env
MILVUS_HOST=localhost
MILVUS_PORT=19530
MILVUS_COLLECTION_NAME=document_chunks
MILVUS_DIMENSION=768
EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
```

### Testing Crawl Features
```bash
# Test crawl update và recrawl
python test_crawl_update.py

# Test vector search
python test_vector_search.py
```

Xem thêm chi tiết trong:
- [CRAWL_API.md](CRAWL_API.md) - API documentation
- [VECTOR_SEARCH_GUIDE.md](VECTOR_SEARCH_GUIDE.md) - Vector search guide
- [CRAWL_UPDATE_GUIDE.md](CRAWL_UPDATE_GUIDE.md) - Crawl update features

## Contributing
1. Fork repository
2. Tạo feature branch: `git checkout -b feature/new-feature`
3. Commit changes: `git commit -am 'Add new feature'`
4. Push branch: `git push origin feature/new-feature`
5. Tạo Pull Request

## License
MIT License - xem file LICENSE để biết thêm chi tiết. 