import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-footer',
  standalone: true,
  imports: [CommonModule, RouterLink],
  template: `
    <footer class="footer">
      <div class="footer-wrapper">
        <div class="footer-main">
          <div class="footer-brand">
            <img src="assets/images/logo.png" alt="Exhome" class="h-[40px] w-[100px]">
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

          <div class="footer-links-grid">
            <div class="footer-column">
              <h3 class="footer-title">Tìm kiếm</h3>
              <ul class="footer-links">
                <li><a routerLink="/can-ho-chung-cu-ban">BĐS đang bán</a></li>
                <li><a routerLink="/can-ho-chung-cu-cho-thue">BĐS cho thuê</a></li>
                <li><a href="/">Nội thất cũ</a></li>
                <li><a href="/">Ô tô cũ</a></li>
                <li><a href="/">Tin tức</a></li>
              </ul>
            </div>

            <div class="footer-column">
              <h3 class="footer-title">Về chúng tôi</h3>
              <ul class="footer-links">
                <li><a routerLink="/about">Giới thiệu</a></li>
                <li><a href="/">Sứ mệnh</a></li>
                <li><a href="/">Câu hỏi thường gặp</a></li>
                <li><a href="/">Tuyển dụng</a></li>
              </ul>
            </div>

            <div class="footer-column">
              <h3 class="footer-title">Pháp lý</h3>
              <ul class="footer-links">
                <li><a href="/chinh-sach-bao-mat.html">Chính sách bảo mật</a></li>
                <li><a href="/">Điều khoản sử dụng</a></li>
              </ul>
            </div>

            <div class="footer-column">
              <h3 class="footer-title">Liên hệ</h3>
              <div class="contact-info">
                <a href="mailto:exhome.net&#64;gmail.com" class="contact-link">
                  <svg class="contact-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
                  </svg>
                  <span>exhome.net&#64;gmail.com</span>
                </a>
                <a href="tel:0582994406" class="contact-link">
                  <svg class="contact-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"></path>
                  </svg>
                  <span>058.299.44.06</span>
                </a>
              </div>
            </div>
          </div>
        </div>

        <div class="footer-bottom">
          <div class="footer-bottom-content">
            <p class="footer-disclaimer">Website thử nghiệm đang trong quá trình hoàn thiện hồ sơ làm thủ tục cấp giấy phép MXH bộ TTTT và giấy phép TMDT với BCT.</p>
            <p class="footer-disclaimer">Exhome.net là máy tìm kiếm, không thực tiếp bán/cho thuê, quý khách có nhu cầu vui lòng liên hệ người bán/cho thuê.</p>
            <p class="footer-copyright">© 2020 - 2024 Exhome.net. Bản quyền thuộc về ExHome.Net</p>
          </div>
        </div>
      </div>
    </footer>
  `,
  styles: [`
    .footer {
      background: var(--gradient-bg-reverse);
      border-top: 1px solid transparent;
      border-image: var(--gradient-brand-border) 1;
      margin-top: auto;
    }

    .footer-wrapper {
      max-width: var(--container-max-width);
      margin: 0 auto;
      padding: 0;
    }

    .footer-main {
      padding: var(--spacing-4xl) var(--container-padding);
      display: grid;
      grid-template-columns: 1fr;
      gap: var(--spacing-3xl);
    }

    @media (min-width: 768px) {
      .footer-main {
        grid-template-columns: 280px 1fr;
        gap: 4rem;
      }
    }

    .footer-brand {
      display: flex;
      flex-direction: column;
    }

    .brand-name {
      font-size: var(--font-size-3xl);
      font-weight: var(--font-weight-bold);
      color: var(--brand);
      margin: 0 0 var(--spacing-xs);
      letter-spacing: var(--letter-spacing-normal);
    }

    .brand-tagline {
      color: var(--text-muted);
      font-size: var(--font-size-base);
      margin: 0 0 var(--spacing-lg);
      line-height: var(--line-height-normal);
    }

    .footer-links-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: var(--spacing-2xl);
    }

    @media (min-width: 1024px) {
      .footer-links-grid {
        grid-template-columns: repeat(4, 1fr);
        gap: var(--spacing-xl);
      }
    }

    .footer-column {
      display: flex;
      flex-direction: column;
    }

    .footer-title {
      font-size: var(--font-size-sm);
      font-weight: var(--font-weight-semibold);
      color: var(--text-main);
      margin: 0 0 var(--spacing-md);
      letter-spacing: var(--letter-spacing-wide);
    }

    .footer-links {
      list-style: none;
      padding: 0;
      margin: 0;
      display: flex;
      flex-direction: column;
      gap: var(--spacing-sm);
    }

    .footer-links a {
      color: var(--text-muted);
      text-decoration: none;
      font-size: var(--font-size-base);
      line-height: var(--line-height-relaxed);
      transition: color var(--transition-base);
      display: inline-block;
    }

    .footer-links a:hover {
      color: var(--brand);
    }

    .contact-info {
      display: flex;
      flex-direction: column;
      gap: 1rem;
    }

    .contact-link {
      display: flex;
      align-items: center;
      gap: var(--spacing-sm);
      color: var(--text-muted);
      text-decoration: none;
      font-size: var(--font-size-base);
      transition: color var(--transition-base);
    }

    .contact-link:hover {
      color: var(--brand);
    }

    .contact-icon {
      width: 18px;
      height: 18px;
      flex-shrink: 0;
      stroke-width: 2;
    }

    .social-links {
      display: flex;
      gap: var(--spacing-sm);
      margin-top: var(--spacing-xs);
    }

    .social-link {
      display: flex;
      align-items: center;
      justify-content: center;
      width: 40px;
      height: 40px;
      border-radius: var(--radius-md);
      background: rgba(255,255,255,.6);
      backdrop-filter: blur(8px);
      border: 1px solid var(--border);
      color: var(--text-muted);
      text-decoration: none;
      transition: all var(--transition-base);
    }

    .social-link svg {
      width: 18px;
      height: 18px;
    }

    .social-link:hover {
      background: var(--brand);
      border-color: var(--brand);
      color: #ffffff;
      transform: translateY(-2px);
      box-shadow: 0 8px 20px rgba(19,126,44,.25);
    }

    .footer-bottom {
      border-top: 1px solid var(--border);
      background: var(--bg);
      padding: var(--spacing-xl) var(--container-padding);
    }

    .footer-bottom-content {
      max-width: 100%;
    }

    .footer-disclaimer {
      margin: 0 0 var(--spacing-sm);
      color: var(--text-muted);
      font-size: var(--font-size-xs);
      line-height: var(--line-height-relaxed);
    }

    .footer-disclaimer:last-of-type {
      margin-bottom: var(--spacing-md);
    }

    .footer-copyright {
      margin: 0;
      color: var(--text-muted);
      font-size: var(--font-size-xs);
      font-weight: var(--font-weight-medium);
      padding-top: var(--spacing-md);
      border-top: 1px solid var(--border);
    }

    @media (max-width: 767px) {
      .footer-main {
        padding: var(--spacing-3xl) var(--container-padding);
        gap: var(--spacing-2xl);
      }

      .footer-links-grid {
        grid-template-columns: 1fr;
        gap: var(--spacing-2xl);
      }

      .footer-bottom {
        padding: var(--spacing-lg) var(--container-padding);
      }

      .brand-name {
        font-size: var(--font-size-2xl);
      }
    }
  `]
})
export class FooterComponent {
}

