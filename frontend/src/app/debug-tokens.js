// Debug script để kiểm tra tokens trong localStorage
// Chạy trong browser console

console.log('🔍 Debugging tokens in localStorage...');

// Kiểm tra access token
const accessToken = localStorage.getItem('access_token');
console.log('Access Token:', accessToken ? `${accessToken.substring(0, 30)}...` : 'null');

// Kiểm tra refresh token
const refreshToken = localStorage.getItem('refresh_token');
console.log('Refresh Token:', refreshToken ? `${refreshToken.substring(0, 30)}...` : 'null');

// Kiểm tra user data
const userData = localStorage.getItem('current_user');
console.log('User Data:', userData);

// Decode JWT tokens (nếu có)
if (accessToken) {
  try {
    const accessPayload = JSON.parse(atob(accessToken.split('.')[1]));
    console.log('Access Token Payload:', accessPayload);
    console.log('Access Token Type:', accessPayload.type);
    console.log('Access Token Expires:', new Date(accessPayload.exp * 1000));
  } catch (e) {
    console.log('Error decoding access token:', e);
  }
}

if (refreshToken) {
  try {
    const refreshPayload = JSON.parse(atob(refreshToken.split('.')[1]));
    console.log('Refresh Token Payload:', refreshPayload);
    console.log('Refresh Token Type:', refreshPayload.type);
    console.log('Refresh Token Expires:', new Date(refreshPayload.exp * 1000));
  } catch (e) {
    console.log('Error decoding refresh token:', e);
  }
}

// Test refresh token API call
console.log('\n🧪 Testing refresh token API call...');
if (refreshToken) {
  fetch('http://localhost:5000/auth/refresh', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${refreshToken}`,
      'Content-Type': 'application/json'
    }
  })
  .then(response => {
    console.log('Refresh API Status:', response.status);
    return response.json();
  })
  .then(data => {
    console.log('Refresh API Response:', data);
  })
  .catch(error => {
    console.log('Refresh API Error:', error);
  });
} else {
  console.log('No refresh token available');
} 