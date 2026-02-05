import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';

interface MarketCard {
  routerLink: string;
  title: string;
  description: string;
  iconPath: string;
}

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule, RouterLink],
  template: `
    <div>
      <!-- Hero Section -->
      <header class="hero-section relative overflow-hidden bg-gradient-to-b from-white to-slate-50 border-b border-slate-100">
        <div class="container grid grid-cols-1 lg:grid-cols-[1.2fr_0.8fr] gap-12 lg:gap-16 py-20 lg:pt-[140px] lg:pb-[110px] relative">
          <div>
            <h1 class="text-4xl md:text-5xl lg:text-[4rem] leading-[1.05] tracking-[-0.035em] mb-8 text-slate-950">
              Tìm kiếm bất động sản <span class="text-emerald-500">thông minh</span>,<br/>nhanh chóng & đáng tin cậy
            </h1>
            <p class="text-lg lg:text-xl max-w-[560px] text-slate-500 mb-10 leading-relaxed">
              Nền tảng tìm kiếm BĐS thế hệ mới được thiết kế với sự rõ ràng, chính xác và đáng tin cậy.
            </p>
            <div class="flex gap-6 max-md:flex-col max-md:gap-4">
              <a routerLink="/can-ho-chung-cu-ban" class="btn-primary max-md:w-full max-md:text-center">Bắt đầu tìm kiếm</a>
              <a routerLink="/about" class="btn-ghost max-md:w-full max-md:text-center">Tìm hiểu thêm</a>
            </div>
          </div>
          <div class="self-center bg-white border border-slate-100 rounded-[20px] p-10 shadow-[0_4px_20px_-2px_rgba(0,0,0,0.05)] relative">
            <div class="flex justify-between py-4 border-b border-gray-200 text-[0.9375rem]">
              <strong class="text-slate-950 font-semibold">Danh sách</strong>
              <span class="text-emerald-500 font-semibold">10,000+</span>
            </div>
            <div class="flex justify-between py-4 border-b border-gray-200 text-[0.9375rem]">
              <strong class="text-slate-950 font-semibold">Cập nhật</strong>
              <span class="text-emerald-500 font-semibold">Hàng giờ</span>
            </div>
            <div class="flex justify-between py-4 border-b border-gray-200 text-[0.9375rem]">
              <strong class="text-slate-950 font-semibold">Độ chính xác</strong>
              <span class="text-emerald-500 font-semibold">98.4%</span>
            </div>
            <div class="flex justify-between py-4 text-[0.9375rem]">
              <strong class="text-slate-950 font-semibold">Trạng thái</strong>
              <span class="text-emerald-500 font-semibold">Hoạt động</span>
            </div>
          </div>
        </div>
      </header>

      <!-- Trust Bar -->
      <section class="py-12 bg-slate-50 border-b border-slate-100">
        <div class="container">
          <div class="flex gap-10 items-center flex-wrap text-slate-500 text-[0.9375rem]">
            <span>Được tin dùng bởi</span>
            <strong class="text-slate-950 font-semibold">Khách hàng cá nhân</strong>
            <strong class="text-slate-950 font-semibold">Nhà đầu tư</strong>
            <strong class="text-slate-950 font-semibold">Môi giới BĐS</strong>
            <strong class="text-slate-950 font-semibold">Doanh nghiệp</strong>
          </div>
        </div>
      </section>

      <!-- Features Section -->
      <section class="py-16 lg:py-[120px] bg-white">
        <div class="container">
          <h2 class="text-[1.75rem] md:text-4xl lg:text-[3rem] tracking-[-0.035em] text-slate-950 mb-10 lg:mb-16 text-center">
            Hệ thống được thiết kế cho trải nghiệm thông minh
          </h2>
          <div class="grid grid-cols-1 md:grid-cols-[repeat(auto-fit,minmax(260px,1fr))] gap-8 lg:gap-12">
            <div class="p-8 lg:p-10 rounded-2xl bg-white border border-slate-100 shadow-[0_4px_20px_-2px_rgba(0,0,0,0.05)] transition-all duration-300 relative hover:-translate-y-1 hover:shadow-[0_4px_20px_-2px_rgba(0,0,0,0.08)] hover:border-emerald-500/20 hover:bg-slate-50">
              <h3 class="mb-4 text-slate-950 text-[1.75rem]">Lõi tìm kiếm mạnh mẽ</h3>
              <p class="text-slate-500 leading-relaxed">Công nghệ AI tiên tiến quét và phân tích từ hàng nghìn nguồn tin cậy.</p>
            </div>
            <div class="p-8 lg:p-10 rounded-2xl bg-white border border-slate-100 shadow-[0_4px_20px_-2px_rgba(0,0,0,0.05)] transition-all duration-300 relative hover:-translate-y-1 hover:shadow-[0_4px_20px_-2px_rgba(0,0,0,0.08)] hover:border-emerald-500/20 hover:bg-slate-50">
              <h3 class="mb-4 text-slate-950 text-[1.75rem]">Giao diện thân thiện</h3>
              <p class="text-slate-500 leading-relaxed">Thiết kế tối giản và dễ sử dụng, giảm tải nhận thức cho người dùng.</p>
            </div>
            <div class="p-8 lg:p-10 rounded-2xl bg-white border border-slate-100 shadow-[0_4px_20px_-2px_rgba(0,0,0,0.05)] transition-all duration-300 relative hover:-translate-y-1 hover:shadow-[0_4px_20px_-2px_rgba(0,0,0,0.08)] hover:border-emerald-500/20 hover:bg-slate-50">
              <h3 class="mb-4 text-slate-950 text-[1.75rem]">Thiết kế đáng tin cậy</h3>
              <p class="text-slate-500 leading-relaxed">Mọi tương tác đều rõ ràng, dự đoán được và có chủ đích.</p>
            </div>
            <div class="p-8 lg:p-10 rounded-2xl bg-white border border-slate-100 shadow-[0_4px_20px_-2px_rgba(0,0,0,0.05)] transition-all duration-300 relative hover:-translate-y-1 hover:shadow-[0_4px_20px_-2px_rgba(0,0,0,0.08)] hover:border-emerald-500/20 hover:bg-slate-50">
              <h3 class="mb-4 text-slate-950 text-[1.75rem]">AI thế hệ mới</h3>
              <p class="text-slate-500 leading-relaxed">Ngôn ngữ trực quan phát triển cùng với hệ thống thông minh.</p>
            </div>
          </div>
        </div>
      </section>

      <!-- Introduction Section -->
      <section class="py-16 lg:py-[120px] bg-slate-50">
        <div class="container">
          <h2 class="text-4xl lg:text-[3rem] font-bold text-slate-950 mb-10 lg:mb-12 leading-[1.05] tracking-[-0.035em] text-center">
            Cách chúng tôi giúp bạn tìm kiếm bất động sản mong muốn?
          </h2>
          <div class="bg-white rounded-[20px] py-8 px-10 lg:py-12 lg:px-16 shadow-[0_4px_20px_-2px_rgba(0,0,0,0.05)] border border-slate-100 max-w-[900px] mx-auto relative">
            <p class="text-slate-700 text-lg lg:text-xl leading-[1.8] text-center">
              Exhome.net sử dụng công nghệ máy tìm kiếm tiên tiến để quét và thu thập thông tin từ các nguồn uy tín trên mạng,
              như các nhóm, diễn đàn, trang tin rao về bất động sản, sau đó xử lý và loại bỏ những nội dung trùng lặp, lỗi thời,
              hoặc không liên quan. Chúng tôi cũng phân loại và gắn nhãn những nội dung theo các tiêu chí như loại đất, địa điểm,
              giá cả, diện tích, pháp lý, và thời gian đăng,... Cuối cùng là sắp xếp và hiển thị những nội dung cho người dùng
              theo thứ tự mới nhất, giúp người dùng tiết kiệm thời gian và công sức khi tìm kiếm bất động sản.
            </p>
          </div>
        </div>
      </section>

      <!-- Rental Market Section -->
      <section class="market-section">
        <div class="container">
          <h2 class="text-4xl lg:text-[3rem] font-bold text-slate-950 mb-12 lg:mb-16 tracking-[-0.035em] text-center relative z-[1]">Thị trường thuê</h2>
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8 relative z-[1]">
            @for (card of rentalMarketCards; track card.routerLink) {
              <a [routerLink]="card.routerLink" class="market-card group">
                <div class="card-icon-wrapper">
                  <svg class="card-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path [attr.d]="card.iconPath" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"/>
                  </svg>
                </div>
                <h3 class="text-lg md:text-2xl font-bold text-slate-950 mb-3 md:mb-4 text-center transition-all duration-[400ms] tracking-[-0.035em] leading-[1.3] group-hover:text-emerald-500">{{ card.title }}</h3>
                <p class="text-slate-500 text-sm md:text-[0.9375rem] leading-relaxed text-center flex-1 transition-colors duration-[400ms] group-hover:text-slate-700">{{ card.description }}</p>
              </a>
            }
          </div>
        </div>
      </section>

      <!-- Sale Market Section -->
      <section class="market-section">
        <div class="container">
          <h2 class="text-4xl lg:text-[3rem] font-bold text-slate-950 mb-12 lg:mb-16 tracking-[-0.035em] text-center relative z-[1]">Thị trường bán</h2>
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8 relative z-[1]">
            @for (card of saleMarketCards; track card.routerLink) {
              <a [routerLink]="card.routerLink" class="market-card group">
                <div class="card-icon-wrapper">
                  <svg class="card-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path [attr.d]="card.iconPath" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"/>
                  </svg>
                </div>
                <h3 class="text-lg md:text-2xl font-bold text-slate-950 mb-3 md:mb-4 text-center transition-all duration-[400ms] tracking-[-0.035em] leading-[1.3] group-hover:text-emerald-500">{{ card.title }}</h3>
                <p class="text-slate-500 text-sm md:text-[0.9375rem] leading-relaxed text-center flex-1 transition-colors duration-[400ms] group-hover:text-slate-700">{{ card.description }}</p>
              </a>
            }
          </div>
        </div>
      </section>
    </div>
  `,
  styles: [`
    /* === CSS khong the dung Tailwind: pseudo-elements, masks, complex gradients === */

    /* Hero SVG background pattern */
    .hero-section::before {
      content: "";
      position: absolute;
      inset: 0;
      background: url("data:image/svg+xml,%3Csvg width='1440' height='800' viewBox='0 0 1440 800' fill='none' xmlns='http://www.w3.org/2000/svg'%3E%3Cdefs%3E%3ClinearGradient id='grad1' x1='0%25' y1='0%25' x2='100%25' y2='100%25'%3E%3Cstop offset='0%25' style='stop-color:%2310b981;stop-opacity:0.12'/%3E%3Cstop offset='100%25' style='stop-color:%2374c858;stop-opacity:0.06'/%3E%3C/linearGradient%3E%3ClinearGradient id='grad2' x1='0%25' y1='0%25' x2='100%25' y2='100%25'%3E%3Cstop offset='0%25' style='stop-color:%2310b981;stop-opacity:0.08'/%3E%3Cstop offset='100%25' style='stop-color:%2374c858;stop-opacity:0.04'/%3E%3C/linearGradient%3E%3ClinearGradient id='grad3' x1='0%25' y1='0%25' x2='100%25' y2='100%25'%3E%3Cstop offset='0%25' style='stop-color:%2310b981;stop-opacity:0.06'/%3E%3Cstop offset='100%25' style='stop-color:%2374c858;stop-opacity:0.03'/%3E%3C/linearGradient%3E%3C/defs%3E%3Cpath d='M0 500C200 450 350 580 550 540C750 500 850 350 1050 300C1250 250 1440 350 1440 350V800H0V500Z' fill='url(%23grad1)'/%3E%3Cpath d='M0 580C250 520 400 650 600 610C800 570 950 420 1150 380C1350 340 1440 420 1440 420V800H0V580Z' fill='url(%23grad2)'/%3E%3Cpath d='M0 650C300 600 500 700 700 670C900 640 1100 500 1300 460C1400 440 1440 480 1440 480V800H0V650Z' fill='url(%23grad3)'/%3E%3Ccircle cx='1200' cy='200' r='150' fill='rgba(16,185,129,0.04)'/%3E%3Ccircle cx='200' cy='300' r='120' fill='rgba(116,200,88,0.03)'/%3E%3Ccircle cx='1000' cy='500' r='100' fill='rgba(16,185,129,0.03)'/%3E%3C/svg%3E") center bottom no-repeat;
      background-size: cover;
      pointer-events: none;
      opacity: 0.9;
    }

    /* Market section gradient backgrounds & wave dividers */
    .market-section {
      padding: 120px 0;
      background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 50%, #ecfdf5 100%);
      position: relative;
      overflow: hidden;
    }

    .market-section:nth-child(even) {
      background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 50%, #ecfdf5 100%);
    }

    .market-section:nth-child(even)::before {
      content: "";
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      height: 100px;
      background: url("data:image/svg+xml,%3Csvg viewBox='0 0 1440 100' preserveAspectRatio='none' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M0,40 C240,80 480,0 720,20 960,40 1200,80 1440,40 L1440,100 L0,100 Z' fill='%23ecfdf5'/%3E%3C/svg%3E") top center no-repeat;
      background-size: 100% 100%;
      pointer-events: none;
      z-index: 1;
    }

    /* Market card - gradient border mask & hover effects */
    .market-card {
      display: flex;
      flex-direction: column;
      align-items: center;
      background: #ffffff;
      border-radius: 24px;
      padding: var(--spacing-3xl) var(--spacing-2xl);
      text-decoration: none;
      transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
      border: 2px solid transparent;
      position: relative;
      overflow: hidden;
      box-shadow: 0 2px 12px rgba(0,0,0,0.04);
      height: 100%;
    }

    .market-card::before {
      content: "";
      position: absolute;
      inset: 0;
      border-radius: 24px;
      padding: 2px;
      background: linear-gradient(135deg, #10b981, #74c858);
      -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
      -webkit-mask-composite: xor;
      mask-composite: exclude;
      opacity: 0;
      transition: opacity 0.4s ease;
    }

    .market-card::after {
      content: "";
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      height: 100%;
      background: linear-gradient(180deg, rgba(16, 185, 129, 0.02) 0%, transparent 100%);
      opacity: 0;
      transition: opacity 0.4s ease;
    }

    .market-card:hover {
      transform: translateY(-8px);
      box-shadow: 0 16px 48px -8px rgba(16, 185, 129, 0.2);
    }

    .market-card:hover::before,
    .market-card:hover::after {
      opacity: 1;
    }

    /* Card icon wrapper with gradient pseudo-element */
    .card-icon-wrapper {
      display: flex;
      justify-content: center;
      align-items: center;
      width: 96px;
      height: 96px;
      margin: 0 auto var(--spacing-xl);
      transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
      position: relative;
    }

    .card-icon-wrapper::before {
      content: "";
      position: absolute;
      inset: 0;
      background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(116, 200, 88, 0.08));
      border-radius: 24px;
      transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
      z-index: 0;
    }

    .market-card:hover .card-icon-wrapper {
      transform: scale(1.1);
    }

    .market-card:hover .card-icon-wrapper::before {
      background: linear-gradient(135deg, #10b981, #74c858);
      box-shadow: 0 12px 32px rgba(16, 185, 129, 0.3);
      transform: rotate(5deg);
    }

    /* Card icon */
    .card-icon {
      width: 48px;
      height: 48px;
      color: #10b981;
      stroke-width: 2;
      transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
      position: relative;
      z-index: 1;
    }

    .market-card:hover .card-icon {
      color: #ffffff;
      transform: scale(1.1);
    }

    /* Responsive for market cards */
    @media (max-width: 768px) {
      .market-section {
        padding: 64px 0;
      }

      .market-card {
        padding: var(--spacing-lg);
      }

      .card-icon-wrapper {
        width: 64px;
        height: 64px;
        margin-bottom: var(--spacing-md);
      }

      .card-icon {
        width: 32px;
        height: 32px;
      }
    }
  `]
})
export class HomeComponent {
  rentalMarketCards: MarketCard[] = [
    {
      routerLink: '/can-ho-chung-cu-cho-thue,can-studio',
      title: 'Căn studio',
      description: 'Phù hợp người độc thân, chuyên gia, người đi làm ngắn hạn, ưu tiên tiện nghi, chi phí thuê tối ưu',
      iconPath: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6'
    },
    {
      routerLink: '/can-ho-chung-cu-cho-thue,can-1-pn-plus',
      title: 'Căn 1 PN +',
      description: 'Lý tưởng cặp đôi, chuyên gia làm việc tại nhà, cần thêm không gian linh hoạt, riêng tư và yên tĩnh',
      iconPath: 'M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4'
    },
    {
      routerLink: '/can-ho-chung-cu-cho-thue,can-2-pn',
      title: 'Căn 2 PN',
      description: 'Phù hợp gia đình trẻ hoặc nhóm bạn ở chung, cần không gian đủ rộng, chi phí thuê hợp lý',
      iconPath: 'M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z'
    },
    {
      routerLink: '/can-ho-chung-cu-cho-thue,can-3-pn',
      title: 'Căn 3 PN',
      description: 'Dành cho gia đình nhiều thế hệ hoặc chuyên gia cao cấp, cần không gian lớn, tiện nghi và riêng tư',
      iconPath: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6'
    }
  ];

  saleMarketCards: MarketCard[] = [
    {
      routerLink: '/can-ho-chung-cu-ban,can-studio',
      title: 'Căn studio',
      description: 'Phù hợp người độc thân hoặc nhà đầu tư, tài chính vừa phải, mua ở hoặc cho thuê linh hoạt, dễ thanh khoản',
      iconPath: 'M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z'
    },
    {
      routerLink: '/can-ho-chung-cu-ban,can-1-pn-plus',
      title: 'Căn 1 PN +',
      description: 'Lý tưởng cặp đôi trẻ, người mua để ở lâu dài, cần không gian đa năng, giá hợp lý, dễ nâng cấp',
      iconPath: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6'
    },
    {
      routerLink: '/can-ho-chung-cu-ban,can-2-pn',
      title: 'Căn 2 PN',
      description: 'Phù hợp gia đình trẻ, nhu cầu ổn định, sinh hoạt thoải mái, vừa ở vừa đầu tư giá trị bền vững',
      iconPath: 'M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4'
    },
    {
      routerLink: '/can-ho-chung-cu-ban,can-3-pn',
      title: 'Căn 3 PN',
      description: 'Dành cho gia đình đông thành viên, mua ở lâu dài, ưu tiên không gian rộng, riêng tư và đẳng cấp sống',
      iconPath: 'M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z'
    }
  ];
}
