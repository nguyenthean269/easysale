import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { DocumentService, ContentGenerateRequest, ContentGenerateResponse } from '../../services/document.service';

@Component({
  selector: 'app-content-generate',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="container mx-auto px-4 py-8">
      <div class="max-w-4xl mx-auto">
        <!-- Header -->
        <div class="mb-8">
          <h1 class="text-3xl font-bold text-gray-800 mb-2">Tạo Nội Dung AI</h1>
          <p class="text-gray-600">Sử dụng AI để tạo nội dung marketing chuyên nghiệp dựa trên thông tin khách hàng</p>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <!-- Form Input -->
          <div class="bg-white rounded-lg shadow-md p-6">
            <h2 class="text-xl font-semibold text-gray-800 mb-6">Thông tin đầu vào</h2>
            
            <form (ngSubmit)="onSubmit()" #contentForm="ngForm">
              <!-- Topic -->
              <div class="mb-6">
                <label for="topic" class="block text-sm font-medium text-gray-700 mb-2">
                  Chủ đề <span class="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  id="topic"
                  name="topic"
                  [(ngModel)]="formData.topic"
                  required
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Ví dụ: Sản phẩm kem dưỡng da chống lão hóa"
                />
              </div>

              <!-- Loại bài viết -->
              <div class="mb-6">
                <label for="loai_bai_viet" class="block text-sm font-medium text-gray-700 mb-2">
                  Loại bài viết
                </label>
                <select
                  id="loai_bai_viet"
                  name="loai_bai_viet"
                  [(ngModel)]="formData.loai_bai_viet"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">Chọn loại bài viết</option>
                  <option value="Bài viết quảng cáo sản phẩm">Bài viết quảng cáo sản phẩm</option>
                  <option value="Bài viết giới thiệu dịch vụ">Bài viết giới thiệu dịch vụ</option>
                  <option value="Email marketing khuyến mãi">Email marketing khuyến mãi</option>
                  <option value="Bài đăng mạng xã hội">Bài đăng mạng xã hội</option>
                  <option value="Bài viết blog chia sẻ kinh nghiệm">Bài viết blog chia sẻ kinh nghiệm</option>
                  <option value="Bài viết giới thiệu khóa học">Bài viết giới thiệu khóa học</option>
                </select>
              </div>

              <!-- Sở thích khách hàng -->
              <div class="mb-6">
                <label for="khach_hang_so_thich" class="block text-sm font-medium text-gray-700 mb-2">
                  Sở thích khách hàng
                </label>
                <textarea
                  id="khach_hang_so_thich"
                  name="khach_hang_so_thich"
                  [(ngModel)]="formData.khach_hang_so_thich"
                  rows="2"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Ví dụ: Làm đẹp tự nhiên, chăm sóc da, sống khỏe mạnh"
                ></textarea>
              </div>

              <!-- Nỗi sợ khách hàng -->
              <div class="mb-6">
                <label for="khach_hang_noi_so" class="block text-sm font-medium text-gray-700 mb-2">
                  Nỗi sợ/Lo lắng của khách hàng
                </label>
                <textarea
                  id="khach_hang_noi_so"
                  name="khach_hang_noi_so"
                  [(ngModel)]="formData.khach_hang_noi_so"
                  rows="2"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Ví dụ: Da bị lão hóa, nếp nhăn, mất tự tin"
                ></textarea>
              </div>

              <!-- Điểm đau khách hàng -->
              <div class="mb-6">
                <label for="khach_hang_noi_dau" class="block text-sm font-medium text-gray-700 mb-2">
                  Điểm đau/Vấn đề của khách hàng
                </label>
                <textarea
                  id="khach_hang_noi_dau"
                  name="khach_hang_noi_dau"
                  [(ngModel)]="formData.khach_hang_noi_dau"
                  rows="2"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Ví dụ: Da khô, thiếu độ ẩm, mất đàn hồi"
                ></textarea>
              </div>

              <!-- Giọng điệu -->
              <div class="mb-6">
                <label for="giong_dieu" class="block text-sm font-medium text-gray-700 mb-2">
                  Giọng điệu
                </label>
                <select
                  id="giong_dieu"
                  name="giong_dieu"
                  [(ngModel)]="formData.giong_dieu"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">Chọn giọng điệu</option>
                  <option value="Thân thiện, tự tin, chuyên nghiệp">Thân thiện, tự tin, chuyên nghiệp</option>
                  <option value="Động viên, tích cực, dễ hiểu">Động viên, tích cực, dễ hiểu</option>
                  <option value="Sang trọng, hấp dẫn, tin cậy">Sang trọng, hấp dẫn, tin cậy</option>
                  <option value="Vui vẻ, phấn khích, tin cậy">Vui vẻ, phấn khích, tin cậy</option>
                  <option value="Chuyên nghiệp, trang trọng">Chuyên nghiệp, trang trọng</option>
                  <option value="Thân thiện, gần gũi">Thân thiện, gần gũi</option>
                </select>
              </div>

              <!-- Mục tiêu -->
              <div class="mb-6">
                <label for="muc_tieu" class="block text-sm font-medium text-gray-700 mb-2">
                  Mục tiêu
                </label>
                <textarea
                  id="muc_tieu"
                  name="muc_tieu"
                  [(ngModel)]="formData.muc_tieu"
                  rows="2"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Ví dụ: Thuyết phục khách hàng mua sản phẩm"
                ></textarea>
              </div>

              <!-- Submit Button -->
              <button
                type="submit"
                [disabled]="!contentForm.form.valid || isLoading"
                class="w-full bg-blue-600 text-white py-3 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                <span *ngIf="!isLoading">🚀 Tạo nội dung</span>
                <span *ngIf="isLoading" class="flex items-center justify-center">
                  <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Đang tạo nội dung...
                </span>
              </button>
            </form>
          </div>

          <!-- Result Panel -->
          <div class="bg-white rounded-lg shadow-md p-6">
            <h2 class="text-xl font-semibold text-gray-800 mb-6">Kết quả</h2>
            
            <!-- Loading State -->
            <div *ngIf="isLoading" class="flex flex-col items-center justify-center py-12">
              <svg class="animate-spin h-12 w-12 text-blue-600 mb-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <p class="text-gray-600">AI đang tạo nội dung cho bạn...</p>
            </div>

            <!-- Error State -->
            <div *ngIf="error && !isLoading" class="bg-red-50 border border-red-200 rounded-md p-4 mb-4">
              <div class="flex">
                <div class="flex-shrink-0">
                  <svg class="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
                  </svg>
                </div>
                <div class="ml-3">
                  <h3 class="text-sm font-medium text-red-800">Có lỗi xảy ra</h3>
                  <p class="text-sm text-red-700 mt-1">{{ error }}</p>
                </div>
              </div>
            </div>

            <!-- Success State -->
            <div *ngIf="result && !isLoading" class="space-y-4">
              <!-- Content -->
              <div class="bg-gray-50 rounded-md p-4">
                <h3 class="text-sm font-medium text-gray-800 mb-3">📝 Nội dung được tạo:</h3>
                <div class="bg-white rounded border p-4 min-h-[300px] max-h-[500px] overflow-y-auto">
                  <pre class="whitespace-pre-wrap text-sm text-gray-700 leading-relaxed">{{ result.content }}</pre>
                </div>
              </div>

              <!-- Metadata -->
              <div class="grid grid-cols-1 gap-3 text-sm">
                <div class="flex justify-between">
                  <span class="text-gray-600">Chủ đề:</span>
                  <span class="text-gray-800 font-medium">{{ result.topic }}</span>
                </div>
                <div class="flex justify-between" *ngIf="result.loai_bai_viet">
                  <span class="text-gray-600">Loại bài viết:</span>
                  <span class="text-gray-800">{{ result.loai_bai_viet }}</span>
                </div>
                <div class="flex justify-between" *ngIf="result.giong_dieu">
                  <span class="text-gray-600">Giọng điệu:</span>
                  <span class="text-gray-800">{{ result.giong_dieu }}</span>
                </div>
                <div *ngIf="result.knowledge_sources && result.knowledge_sources.length > 0" class="pt-2 border-t">
                  <span class="text-gray-600 text-xs font-medium">📚 Tri thức tham khảo:</span>
                  <div class="mt-2 space-y-1">
                    <div *ngFor="let source of result.knowledge_sources" 
                         class="flex justify-between items-center bg-blue-50 px-2 py-1 rounded text-xs">
                      <span class="text-blue-800 truncate">{{ source.source }}</span>
                      <span class="text-blue-600 ml-2 font-mono">{{ (source.score * 100).toFixed(1) }}%</span>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Action Buttons -->
              <div class="flex space-x-3 pt-4 border-t">
                <button
                  (click)="copyToClipboard()"
                  class="flex-1 bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 transition-colors"
                >
                  📋 Copy nội dung
                </button>
                <button
                  (click)="clearResult()"
                  class="flex-1 bg-gray-600 text-white py-2 px-4 rounded-md hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 transition-colors"
                >
                  🗑️ Xóa kết quả
                </button>
              </div>
            </div>

            <!-- Empty State -->
            <div *ngIf="!result && !isLoading && !error" class="flex flex-col items-center justify-center py-12 text-gray-500">
              <svg class="h-16 w-16 mb-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <p class="text-center">Nội dung sẽ hiển thị ở đây sau khi bạn tạo</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    /* Custom scrollbar for content area */
    .overflow-y-auto::-webkit-scrollbar {
      width: 6px;
    }
    
    .overflow-y-auto::-webkit-scrollbar-track {
      background: #f1f1f1;
      border-radius: 3px;
    }
    
    .overflow-y-auto::-webkit-scrollbar-thumb {
      background: #c1c1c1;
      border-radius: 3px;
    }
    
    .overflow-y-auto::-webkit-scrollbar-thumb:hover {
      background: #a8a8a8;
    }
  `]
})
export class ContentGenerateComponent {
  formData: ContentGenerateRequest = {
    topic: '',
    loai_bai_viet: '',
    khach_hang_so_thich: '',
    khach_hang_noi_so: '',
    khach_hang_noi_dau: '',
    giong_dieu: '',
    muc_tieu: ''
  };

  result: ContentGenerateResponse | null = null;
  isLoading = false;
  error: string | null = null;

  constructor(private documentService: DocumentService) {}

  onSubmit() {
    if (!this.formData.topic.trim()) {
      this.error = 'Vui lòng nhập chủ đề';
      return;
    }

    this.isLoading = true;
    this.error = null;
    this.result = null;

    this.documentService.generateContent(this.formData).subscribe({
      next: (response) => {
        this.result = response;
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Error generating content:', error);
        this.error = error.error?.message || error.error?.error || 'Có lỗi xảy ra khi tạo nội dung';
        this.isLoading = false;
      }
    });
  }

  copyToClipboard() {
    if (this.result?.content) {
      navigator.clipboard.writeText(this.result.content).then(() => {
        // You could add a toast notification here
        alert('Đã copy nội dung vào clipboard!');
      }).catch(() => {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = this.result!.content;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        alert('Đã copy nội dung vào clipboard!');
      });
    }
  }

  clearResult() {
    this.result = null;
    this.error = null;
  }
} 