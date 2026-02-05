import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-about',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="about-page">
      <div class="about-container">
        <!-- Hero Section -->
        <section class="hero-section">
          <h1 class="hero-title">Về Exhome</h1>
          <p class="hero-subtitle">Tìm kiếm bất động sản thông minh, nhanh chóng và hiệu quả</p>
        </section>

        <!-- Mission Section -->
        <section class="content-section">
          <div class="section-header">
            <div class="section-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
            </div>
            <h2 class="section-title">Sứ mệnh</h2>
          </div>
          <div class="section-content">
            <p>
              Exhome.net được xây dựng với sứ mệnh giúp người dùng tìm kiếm bất động sản một cách dễ dàng, nhanh chóng và hiệu quả. 
              Chúng tôi sử dụng công nghệ máy tìm kiếm tiên tiến để thu thập, xử lý và tổ chức thông tin từ nhiều nguồn khác nhau, 
              giúp bạn tiết kiệm thời gian và công sức trong quá trình tìm kiếm bất động sản phù hợp.
            </p>
          </div>
        </section>

        <!-- Technology Section -->
        <section class="content-section">
          <div class="section-header">
            <div class="section-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/>
              </svg>
            </div>
            <h2 class="section-title">Công nghệ</h2>
          </div>
          <div class="section-content">
            <p>
              Chúng tôi sử dụng công nghệ máy tìm kiếm tiên tiến để quét và thu thập thông tin từ các nguồn uy tín trên mạng, 
              bao gồm các nhóm, diễn đàn, và trang tin rao về bất động sản. Hệ thống tự động xử lý và loại bỏ những nội dung 
              trùng lặp, lỗi thời, hoặc không liên quan. Thông tin được phân loại và gắn nhãn theo các tiêu chí như loại đất, 
              địa điểm, giá cả, diện tích, pháp lý, và thời gian đăng.
            </p>
          </div>
        </section>

        <!-- Features Section -->
        <section class="content-section">
          <div class="section-header">
            <div class="section-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4"/>
              </svg>
            </div>
            <h2 class="section-title">Tính năng</h2>
          </div>
          <div class="features-grid">
            <div class="feature-card">
              <div class="feature-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
                </svg>
              </div>
              <h3 class="feature-title">Tìm kiếm thông minh</h3>
              <p class="feature-description">
                Tìm kiếm nhanh chóng với nhiều tiêu chí lọc như loại bất động sản, khu vực, giá cả, diện tích
              </p>
            </div>

            <div class="feature-card">
              <div class="feature-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
                </svg>
              </div>
              <h3 class="feature-title">Cập nhật liên tục</h3>
              <p class="feature-description">
                Thông tin được cập nhật liên tục từ nhiều nguồn, đảm bảo bạn luôn có dữ liệu mới nhất
              </p>
            </div>

            <div class="feature-card">
              <div class="feature-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/>
                </svg>
              </div>
              <h3 class="feature-title">Thông tin đáng tin cậy</h3>
              <p class="feature-description">
                Loại bỏ tự động các thông tin trùng lặp, lỗi thời, giúp bạn tìm được thông tin chính xác
              </p>
            </div>

            <div class="feature-card">
              <div class="feature-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
              </div>
              <h3 class="feature-title">Tiết kiệm thời gian</h3>
              <p class="feature-description">
                Không cần lướt qua hàng trăm bài đăng, tìm kiếm nhanh chóng với kết quả được sắp xếp hợp lý
              </p>
            </div>
          </div>
        </section>

        <!-- Note Section -->
        <section class="note-section">
          <div class="note-content">
            <p>
              <strong>Lưu ý:</strong> Exhome.net là máy tìm kiếm, không thực tiếp bán/cho thuê. 
              Quý khách có nhu cầu vui lòng liên hệ trực tiếp với người bán/cho thuê thông qua thông tin liên hệ trong từng bài đăng.
            </p>
          </div>
        </section>
      </div>
    </div>
  `,
  styles: [`
    .about-page {
      padding: 3rem 0;
    }

    .about-container {
      max-width: 1280px;
      margin: 0 auto;
      padding: 0 2rem;
    }

    /* Hero Section */
    .hero-section {
      text-align: center;
      margin-bottom: 4rem;
      padding-bottom: 3rem;
      border-bottom: 1px solid #e5e7eb;
    }

    .hero-title {
      font-size: 3rem;
      font-weight: 700;
      color: #111827;
      margin: 0 0 1rem 0;
      letter-spacing: -0.03em;
    }

    .hero-subtitle {
      font-size: 1.25rem;
      color: #6b7280;
      margin: 0;
      line-height: 1.6;
    }

    /* Content Section */
    .content-section {
      margin-bottom: 4rem;
    }

    .section-header {
      display: flex;
      align-items: center;
      gap: 1rem;
      margin-bottom: 1.5rem;
    }

    .section-icon {
      width: 48px;
      height: 48px;
      background: rgba(19, 126, 44, 0.1);
      border-radius: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
    }

    .section-icon svg {
      width: 24px;
      height: 24px;
      color: rgb(19, 126, 44);
      stroke-width: 1.5;
    }

    .section-title {
      font-size: 2rem;
      font-weight: 600;
      color: #111827;
      margin: 0;
      letter-spacing: -0.02em;
    }

    .section-content {
      padding-left: 4rem;
    }

    .section-content p {
      color: #4b5563;
      font-size: 1.0625rem;
      line-height: 1.8;
      margin: 0;
    }

    /* Features Grid */
    .features-grid {
      display: grid;
      grid-template-columns: repeat(1, 1fr);
      gap: 1.5rem;
      padding-left: 4rem;
    }

    @media (min-width: 768px) {
      .features-grid {
        grid-template-columns: repeat(2, 1fr);
      }
    }

    @media (min-width: 1024px) {
      .features-grid {
        grid-template-columns: repeat(4, 1fr);
      }
    }

    .feature-card {
      background: #ffffff;
      border: 1px solid #e5e7eb;
      border-radius: 12px;
      padding: 1.5rem;
      transition: all 0.3s ease;
    }

    .feature-card:hover {
      border-color: rgb(19, 126, 44);
      box-shadow: 0 4px 12px rgba(19, 126, 44, 0.1);
      transform: translateY(-2px);
    }

    .feature-icon {
      width: 48px;
      height: 48px;
      background: rgba(19, 126, 44, 0.1);
      border-radius: 10px;
      display: flex;
      align-items: center;
      justify-content: center;
      margin-bottom: 1rem;
    }

    .feature-icon svg {
      width: 24px;
      height: 24px;
      color: rgb(19, 126, 44);
      stroke-width: 1.5;
    }

    .feature-title {
      font-size: 1.125rem;
      font-weight: 600;
      color: #111827;
      margin: 0 0 0.75rem 0;
    }

    .feature-description {
      color: #6b7280;
      font-size: 0.9375rem;
      line-height: 1.6;
      margin: 0;
    }

    /* Note Section */
    .note-section {
      margin-top: 4rem;
      padding-top: 3rem;
      border-top: 1px solid #e5e7eb;
    }

    .note-content {
      background: rgba(19, 126, 44, 0.05);
      border-left: 3px solid rgb(19, 126, 44);
      border-radius: 8px;
      padding: 1.5rem 2rem;
    }

    .note-content p {
      margin: 0;
      color: #4b5563;
      font-size: 1rem;
      line-height: 1.7;
    }

    .note-content strong {
      color: rgb(19, 126, 44);
      font-weight: 600;
    }

    /* Responsive */
    @media (max-width: 768px) {
      .about-page {
        padding: 2rem 0;
      }

      .about-container {
        padding: 0 1rem;
      }

      .hero-section {
        margin-bottom: 3rem;
        padding-bottom: 2rem;
      }

      .hero-title {
        font-size: 2rem;
      }

      .hero-subtitle {
        font-size: 1.125rem;
      }

      .content-section {
        margin-bottom: 3rem;
      }

      .section-header {
        flex-direction: column;
        align-items: flex-start;
        gap: 0.75rem;
      }

      .section-content {
        padding-left: 0;
      }

      .features-grid {
        padding-left: 0;
      }

      .section-title {
        font-size: 1.5rem;
      }
    }
  `]
})
export class AboutComponent {
}


