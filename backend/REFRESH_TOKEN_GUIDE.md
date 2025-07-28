# Refresh Token Guide

## Tổng quan

Hệ thống hiện tại đã được cập nhật để hỗ trợ **Refresh Token** - một cơ chế bảo mật quan trọng cho JWT authentication.

## 🔄 Cách hoạt động

### 1. **Token Types**
- **Access Token**: Token ngắn hạn (1 giờ) để truy cập API
- **Refresh Token**: Token dài hạn (7 ngày) để lấy access token mới

### 2. **Flow Authentication**
```
1. User đăng nhập → Nhận access_token + refresh_token
2. Sử dụng access_token để gọi API
3. Khi access_token hết hạn (401) → Tự động dùng refresh_token
4. Nhận access_token mới → Tiếp tục sử dụng
5. Khi refresh_token hết hạn → Yêu cầu đăng nhập lại
```

## 🛠️ Backend Implementation

### Cấu hình JWT
```python
# config.py
JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hour
JWT_REFRESH_TOKEN_EXPIRES = 604800  # 7 days
```

### API Endpoints

#### 1. Login
```http
POST /auth/login
Content-Type: application/json

{
  "username": "user",
  "password": "user123"
}
```

**Response:**
```json
{
  "message": "Đăng nhập thành công",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "username": "user",
    "role": "user"
  }
}
```

#### 2. Refresh Token
```http
POST /auth/refresh
Authorization: Bearer <refresh_token>
```

**Response:**
```json
{
  "message": "Token đã được refresh thành công",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### 3. Logout
```http
POST /auth/logout
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "message": "Đăng xuất thành công"
}
```

## 🎨 Frontend Implementation

### AuthService Updates

#### 1. Interface Updates
```typescript
export interface LoginResponse {
  access_token: string;
  refresh_token: string;  // Thêm refresh token
  token_type: string;
  user: User;
}

export interface RefreshResponse {
  access_token: string;
  message: string;
}
```

#### 2. New Methods
```typescript
// Refresh token
refreshToken(): Observable<RefreshResponse>

// Get refresh token
getRefreshToken(): string | null

// Updated logout
logout(): Observable<any>
```

### AuthInterceptor Updates

Interceptor tự động xử lý refresh token:

```typescript
// Khi gặp lỗi 401
if (error.status === 401) {
  const refreshToken = authService.getRefreshToken();
  
  if (refreshToken) {
    return authService.refreshToken().pipe(
      switchMap(response => {
        // Tạo lại request với token mới
        const newRequest = request.clone({
          setHeaders: {
            Authorization: `Bearer ${response.access_token}`
          }
        });
        return next(newRequest);
      }),
      catchError(refreshError => {
        // Refresh token cũng hết hạn
        authService.clearAuth();
        router.navigate(['/login']);
        return throwError(() => refreshError);
      })
    );
  }
}
```

## 🧪 Testing

### Test Script
```bash
python test_refresh_token.py
```

### Manual Testing
```bash
# 1. Login
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "password": "user123"}'

# 2. Refresh token
curl -X POST http://localhost:5000/auth/refresh \
  -H "Authorization: Bearer <refresh_token>"

# 3. Logout
curl -X POST http://localhost:5000/auth/logout \
  -H "Authorization: Bearer <access_token>"
```

## 🔒 Security Features

### 1. **Token Expiration**
- Access Token: 1 giờ
- Refresh Token: 7 ngày

### 2. **Automatic Refresh**
- Frontend tự động refresh khi access token hết hạn
- User không cần đăng nhập lại

### 3. **Secure Storage**
- Tokens được lưu trong localStorage
- Refresh token được xóa khi logout

### 4. **Error Handling**
- Invalid refresh token → Logout
- Expired refresh token → Redirect to login

## 📋 Environment Variables

Thêm vào file `.env`:
```env
JWT_ACCESS_TOKEN_EXPIRES=3600
JWT_REFRESH_TOKEN_EXPIRES=604800
```

## 🚀 Benefits

### 1. **Better UX**
- User không bị logout thường xuyên
- Seamless experience

### 2. **Enhanced Security**
- Access token ngắn hạn giảm rủi ro
- Refresh token dài hạn cho convenience

### 3. **Automatic Management**
- Frontend tự động xử lý token refresh
- Developer không cần lo lắng về token expiration

## 🔧 Troubleshooting

### Common Issues

#### 1. **Refresh Token Not Working**
- Kiểm tra refresh token có trong localStorage
- Kiểm tra backend endpoint `/auth/refresh`

#### 2. **Infinite Refresh Loop**
- Kiểm tra logic trong AuthInterceptor
- Đảm bảo không gọi refresh cho refresh endpoint

#### 3. **Token Storage Issues**
- Kiểm tra localStorage trong browser
- Đảm bảo clearAuth() xóa đúng tokens

### Debug Commands
```bash
# Test refresh token
python test_refresh_token.py

# Check JWT configuration
python debug_jwt_token.py
```

## 📚 References

- [Flask-JWT-Extended Documentation](https://flask-jwt-extended.readthedocs.io/)
- [Angular HTTP Interceptors](https://angular.io/api/common/http/HttpInterceptor)
- [JWT Best Practices](https://auth0.com/blog/a-look-at-the-latest-draft-for-jwt-bcp/) 