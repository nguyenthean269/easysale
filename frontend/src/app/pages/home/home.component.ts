import { Component } from '@angular/core';

@Component({
  selector: 'app-home',
  standalone: true,
  template: `
    <div class="min-h-screen">
      <!-- Hero Section -->
      <section class="bg-gradient-to-br from-blue-600 to-purple-700 text-white py-20">
        <div class="max-w-6xl mx-auto px-6 text-center">
          <h1 class="text-5xl font-bold mb-6">Welcome to EasySale</h1>
          <p class="text-xl mb-8 opacity-90 max-w-2xl mx-auto">
            Your one-stop solution for easy and efficient sales management
          </p>
          <button class="bg-white text-blue-600 px-8 py-3 rounded-full font-semibold hover:bg-gray-100 transition-colors">
            Get Started
          </button>
        </div>
      </section>
      
      <!-- Features Section -->
      <section class="py-20 bg-gray-50">
        <div class="max-w-6xl mx-auto px-6">
          <h2 class="text-3xl font-bold text-center text-gray-800 mb-12">Why Choose EasySale?</h2>
          <div class="grid md:grid-cols-3 gap-8">
            <div class="bg-white p-8 rounded-lg shadow-sm text-center">
              <div class="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg class="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
              </div>
              <h3 class="text-xl font-semibold text-gray-800 mb-3">Easy Management</h3>
              <p class="text-gray-600">Manage your products, orders, and customers with ease</p>
            </div>
            
            <div class="bg-white p-8 rounded-lg shadow-sm text-center">
              <div class="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg class="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
                </svg>
              </div>
              <h3 class="text-xl font-semibold text-gray-800 mb-3">Real-time Analytics</h3>
              <p class="text-gray-600">Get insights into your sales performance instantly</p>
            </div>
            
            <div class="bg-white p-8 rounded-lg shadow-sm text-center">
              <div class="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg class="w-8 h-8 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"></path>
                </svg>
              </div>
              <h3 class="text-xl font-semibold text-gray-800 mb-3">Secure & Reliable</h3>
              <p class="text-gray-600">Your data is safe with our enterprise-grade security</p>
            </div>
          </div>
        </div>
      </section>
    </div>
  `,
  styles: [`
    /* Custom styles for home page */
    .gradient-bg {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
  `]
})
export class HomeComponent {} 