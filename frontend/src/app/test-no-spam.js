// Test script để kiểm tra không còn spam refresh calls
// Chạy trong browser console

console.log('🧪 Testing no spam refresh calls...');

let refreshCallCount = 0;

// Override fetch để đếm số lần gọi refresh
const originalFetch = window.fetch;
window.fetch = function(...args) {
  const url = args[0];
  if (typeof url === 'string' && url.includes('/auth/refresh')) {
    refreshCallCount++;
    console.log(`🔄 Refresh call #${refreshCallCount}: ${url}`);
  }
  return originalFetch.apply(this, args);
};

// Reset counter
refreshCallCount = 0;

// Test 1: Gọi API với token hết hạn
console.log('\n🧪 Test 1: Calling API with expired token...');

fetch('http://localhost:5000/user/profile', {
  method: 'GET',
  headers: {
    'Authorization': 'Bearer expired_token_here',
    'Content-Type': 'application/json'
  }
})
.then(response => {
  console.log('Profile API Status:', response.status);
  if (response.status === 401) {
    console.log('✅ Expected 401 - token expired');
    console.log(`Total refresh calls: ${refreshCallCount}`);
    
    if (refreshCallCount <= 1) {
      console.log('✅ No spam detected - refresh called only once');
    } else {
      console.log('❌ Spam detected - refresh called multiple times');
    }
  }
})
.catch(error => {
  console.log('Profile API Error:', error);
  console.log(`Total refresh calls: ${refreshCallCount}`);
});

// Test 2: Gọi refresh trực tiếp
setTimeout(() => {
  console.log('\n🧪 Test 2: Direct refresh call...');
  refreshCallCount = 0;
  
  const refreshToken = localStorage.getItem('refresh_token');
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
      console.log(`Total refresh calls: ${refreshCallCount}`);
      
      if (refreshCallCount === 1) {
        console.log('✅ Direct refresh worked correctly');
      } else {
        console.log('❌ Unexpected refresh calls');
      }
    })
    .catch(error => {
      console.log('Direct Refresh Error:', error);
    });
  } else {
    console.log('❌ No refresh token available');
  }
}, 2000);

// Restore original fetch
setTimeout(() => {
  window.fetch = originalFetch;
  console.log('✅ Original fetch restored');
}, 5000); 