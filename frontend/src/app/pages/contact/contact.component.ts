import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-contact',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="contact-page">
      <div class="contact-container">
        <!-- Hero Section -->
        <section class="hero-section">
          <h1 class="hero-title">Liên hệ với chúng tôi</h1>
          <p class="hero-subtitle">Chúng tôi luôn sẵn sàng hỗ trợ và lắng nghe ý kiến của bạn</p>
        </section>

        <div class="contact-grid">
          <!-- Contact Info -->
          <section class="contact-info-section">
            <div class="info-card">
              <div class="info-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
                </svg>
              </div>
              <h3 class="info-title">Email</h3>
              <a href="mailto:exhome.net&#64;gmail.com" class="info-link">exhome.net&#64;gmail.com</a>
            </div>

            <div class="info-card">
              <div class="info-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"/>
                </svg>
              </div>
              <h3 class="info-title">Điện thoại</h3>
              <a href="tel:0582994406" class="info-link">058.299.44.06</a>
            </div>

            <div class="info-card">
              <div class="info-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/>
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/>
                </svg>
              </div>
              <h3 class="info-title">Địa chỉ</h3>
              <p class="info-text">Website thử nghiệm đang trong quá trình hoàn thiện</p>
            </div>

            <div class="social-card">
              <h3 class="social-title">Kết nối với chúng tôi</h3>
              <div class="social-links">
                <a href="https://facebook.com/exhome.net" target="_blank" rel="noopener noreferrer" class="social-link" aria-label="Facebook">
                  <svg viewBox="0 0 512 512" fill="currentColor">
                    <path d="M504 256C504 119 393 8 256 8S8 119 8 256c0 123.78 90.69 226.38 209.25 245V327.69h-63V256h63v-54.64c0-62.15 37-96.48 93.67-96.48 27.14 0 55.52 4.84 55.52 4.84v61h-31.28c-30.8 0-40.41 19.12-40.41 38.73V256h68.78l-11 71.69h-57.78V501C413.31 482.38 504 379.78 504 256z"></path>
                  </svg>
                </a>
                <a href="/" target="_blank" rel="noopener noreferrer" class="social-link" aria-label="YouTube">
                  <svg viewBox="0 0 576 512" fill="currentColor">
                    <path d="M549.655 124.083c-6.281-23.65-24.787-42.276-48.284-48.597C458.781 64 288 64 288 64S117.22 64 74.629 75.486c-23.497 6.322-42.003 24.947-48.284 48.597-11.412 42.867-11.412 132.305-11.412 132.305s0 89.438 11.412 132.305c6.281 23.65 24.787 41.5 48.284 47.821C117.22 448 288 448 288 448s170.78 0 213.371-11.486c23.497-6.321 42.003-24.171 48.284-47.821 11.412-42.867 11.412-132.305 11.412-132.305s0-89.438-11.412-132.305zm-317.51 213.508V175.185l142.739 81.205-142.739 81.201z"></path>
                  </svg>
                </a>
              </div>
            </div>
          </section>

          <!-- Contact Form -->
          <section class="contact-form-section">
            <div class="form-card">
              <h2 class="form-title">Gửi tin nhắn cho chúng tôi</h2>
              <form class="contact-form" (ngSubmit)="onSubmit()">
                <div class="form-group">
                  <label for="name" class="form-label">Họ và tên</label>
                  <input 
                    type="text" 
                    id="name" 
                    name="name" 
                    class="form-input" 
                    placeholder="Nhập họ và tên của bạn"
                    [(ngModel)]="formData.name"
                    required>
                </div>

                <div class="form-group">
                  <label for="email" class="form-label">Email</label>
                  <input 
                    type="email" 
                    id="email" 
                    name="email" 
                    class="form-input" 
                    placeholder="your.email@example.com"
                    [(ngModel)]="formData.email"
                    required>
                </div>

                <div class="form-group">
                  <label for="phone" class="form-label">Số điện thoại</label>
                  <input 
                    type="tel" 
                    id="phone" 
                    name="phone" 
                    class="form-input" 
                    placeholder="Nhập số điện thoại"
                    [(ngModel)]="formData.phone">
                </div>

                <div class="form-group">
                  <label for="subject" class="form-label">Chủ đề</label>
                  <input 
                    type="text" 
                    id="subject" 
                    name="subject" 
                    class="form-input" 
                    placeholder="Chủ đề tin nhắn"
                    [(ngModel)]="formData.subject"
                    required>
                </div>

                <div class="form-group">
                  <label for="message" class="form-label">Nội dung</label>
                  <textarea 
                    id="message" 
                    name="message" 
                    class="form-textarea" 
                    rows="6"
                    placeholder="Nhập nội dung tin nhắn của bạn..."
                    [(ngModel)]="formData.message"
                    required></textarea>
                </div>

                <button type="submit" class="submit-button">
                  <span>Gửi tin nhắn</span>
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"/>
                  </svg>
                </button>
              </form>
            </div>
          </section>
        </div>

        <!-- Note Section -->
        <section class="note-section">
          <div class="note-content">
            <p>
              <strong>Lưu ý:</strong> Exhome.net là máy tìm kiếm, không thực tiếp bán/cho thuê. 
              Nếu bạn có nhu cầu về bất động sản, vui lòng liên hệ trực tiếp với người bán/cho thuê thông qua thông tin trong từng bài đăng.
            </p>
          </div>
        </section>
      </div>
    </div>
  `,
  styles: [`
    .contact-page {
      padding: 3rem 0;
    }

    .contact-container {
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

    /* Contact Grid */
    .contact-grid {
      display: grid;
      grid-template-columns: 1fr;
      gap: 3rem;
      margin-bottom: 4rem;
    }

    @media (min-width: 1024px) {
      .contact-grid {
        grid-template-columns: 1fr 1.5fr;
      }
    }

    /* Contact Info Section */
    .contact-info-section {
      display: flex;
      flex-direction: column;
      gap: 1.5rem;
    }

    .info-card {
      background: #ffffff;
      border: 1px solid #e5e7eb;
      border-radius: 12px;
      padding: 2rem;
      transition: all 0.3s ease;
    }

    .info-card:hover {
      border-color: rgb(19, 126, 44);
      box-shadow: 0 4px 12px rgba(19, 126, 44, 0.1);
    }

    .info-icon {
      width: 56px;
      height: 56px;
      background: rgba(19, 126, 44, 0.1);
      border-radius: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
      margin-bottom: 1rem;
    }

    .info-icon svg {
      width: 28px;
      height: 28px;
      color: rgb(19, 126, 44);
      stroke-width: 1.5;
    }

    .info-title {
      font-size: 1.125rem;
      font-weight: 600;
      color: #111827;
      margin: 0 0 0.75rem 0;
    }

    .info-link {
      color: rgb(19, 126, 44);
      text-decoration: none;
      font-size: 1rem;
      transition: color 0.2s ease;
      display: inline-block;
    }

    .info-link:hover {
      color: rgb(16, 110, 38);
      text-decoration: underline;
    }

    .info-text {
      color: #6b7280;
      font-size: 1rem;
      line-height: 1.6;
      margin: 0;
    }

    .social-card {
      background: #ffffff;
      border: 1px solid #e5e7eb;
      border-radius: 12px;
      padding: 2rem;
    }

    .social-title {
      font-size: 1.125rem;
      font-weight: 600;
      color: #111827;
      margin: 0 0 1rem 0;
    }

    .social-links {
      display: flex;
      gap: 1rem;
    }

    .social-link {
      display: flex;
      align-items: center;
      justify-content: center;
      width: 44px;
      height: 44px;
      border-radius: 10px;
      background: #ffffff;
      border: 1px solid #e5e7eb;
      color: #6b7280;
      text-decoration: none;
      transition: all 0.2s ease;
    }

    .social-link svg {
      width: 20px;
      height: 20px;
    }

    .social-link:hover {
      background: rgb(19, 126, 44);
      border-color: rgb(19, 126, 44);
      color: #ffffff;
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(19, 126, 44, 0.2);
    }

    /* Contact Form Section */
    .contact-form-section {
      display: flex;
      flex-direction: column;
    }

    .form-card {
      background: #ffffff;
      border: 1px solid #e5e7eb;
      border-radius: 12px;
      padding: 2.5rem;
    }

    .form-title {
      font-size: 1.75rem;
      font-weight: 600;
      color: #111827;
      margin: 0 0 2rem 0;
      letter-spacing: -0.01em;
    }

    .contact-form {
      display: flex;
      flex-direction: column;
      gap: 1.5rem;
    }

    .form-group {
      display: flex;
      flex-direction: column;
      gap: 0.5rem;
    }

    .form-label {
      font-size: 0.9375rem;
      font-weight: 500;
      color: #374151;
    }

    .form-input,
    .form-textarea {
      width: 100%;
      padding: 0.75rem 1rem;
      border: 1px solid #d1d5db;
      border-radius: 8px;
      font-size: 1rem;
      color: #111827;
      transition: all 0.2s ease;
      font-family: inherit;
    }

    .form-input:focus,
    .form-textarea:focus {
      outline: none;
      border-color: rgb(19, 126, 44);
      box-shadow: 0 0 0 3px rgba(19, 126, 44, 0.1);
    }

    .form-textarea {
      resize: vertical;
      min-height: 120px;
    }

    .submit-button {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 0.5rem;
      background: rgb(19, 126, 44);
      color: #ffffff;
      border: none;
      border-radius: 8px;
      padding: 0.875rem 2rem;
      font-size: 1rem;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.2s ease;
      margin-top: 0.5rem;
    }

    .submit-button:hover {
      background: rgb(16, 110, 38);
      transform: translateY(-1px);
      box-shadow: 0 4px 12px rgba(19, 126, 44, 0.2);
    }

    .submit-button svg {
      width: 20px;
      height: 20px;
      stroke-width: 2;
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
      .contact-page {
        padding: 2rem 0;
      }

      .contact-container {
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

      .contact-grid {
        gap: 2rem;
        margin-bottom: 3rem;
      }

      .form-card {
        padding: 1.5rem;
      }

      .form-title {
        font-size: 1.5rem;
        margin-bottom: 1.5rem;
      }
    }
  `]
})
export class ContactComponent {
  formData = {
    name: '',
    email: '',
    phone: '',
    subject: '',
    message: ''
  };

  onSubmit() {
    // TODO: Implement form submission
    console.log('Form submitted:', this.formData);
    alert('Cảm ơn bạn đã liên hệ! Chúng tôi sẽ phản hồi sớm nhất có thể.');
    this.formData = {
      name: '',
      email: '',
      phone: '',
      subject: '',
      message: ''
    };
  }
}


