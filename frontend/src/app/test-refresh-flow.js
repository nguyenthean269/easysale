// Test script để kiểm tra toàn bộ refresh flow
// Chạy trong browser console

console.log('🧪 Testing complete refresh flow...');

// 1. Kiểm tra tokens hiện tại
const accessToken = localStorage.getItem('access_token');
const refreshToken = localStorage.getItem('refresh_token');

console.log('Current tokens:');
console.log('Access token:', accessToken ? 'Present' : 'Missing');
console.log('Refresh token:', refreshToken ? 'Present' : 'Missing');

// 2. Test gọi API với access token hết hạn
console.log('\n🧪 Testing API call with expired token...');

// Tạo một request với token cũ (giả sử hết hạn)
fetch('http://localhost:5000/user/profile', {
  method: 'GET',
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
  }
})
.then(response => {
  console.log('Profile API Status:', response.status);
  if (response.status === 401) {
    console.log('✅ Expected 401 - token expired');
    console.log('Interceptor should automatically refresh token...');
  } else if (response.status === 200) {
    console.log('✅ Token still valid');
    return response.json();
  }
})
.then(data => {
  if (data) {
    console.log('Profile data:', data);
  }
})
.catch(error => {
  console.log('Profile API Error:', error);
});

// 3. Test refresh token trực tiếp
console.log('\n🧪 Testing direct refresh token call...');

if (refreshToken) {
  fetch('http://localhost:5000/auth/refresh', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${refreshToken}`,
      'Content-Type': 'application/json'
    }
  })
  .then(response => {
    console.log('Direct Refresh Status:', response.status);
    return response.json();
  })
  .then(data => {
    console.log('Direct Refresh Response:', data);
    if (data.access_token) {
      console.log('✅ New access token received');
      // Lưu token mới
      localStorage.setItem('access_token', data.access_token);
      console.log('✅ New token saved to localStorage');
    }
  })
  .catch(error => {
    console.log('Direct Refresh Error:', error);
  });
} else {
  console.log('❌ No refresh token available');
}

// 4. Test API call với token mới
setTimeout(() => {
  console.log('\n🧪 Testing API call with new token...');
  const newAccessToken = localStorage.getItem('access_token');
  
  fetch('http://localhost:5000/user/profile', {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${newAccessToken}`,
      'Content-Type': 'application/json'
    }
  })
  .then(response => {
    console.log('New Profile API Status:', response.status);
    return response.json();
  })
  .then(data => {
    console.log('New Profile Response:', data);
  })
  .catch(error => {
    console.log('New Profile Error:', error);
  });
}, 1000); 