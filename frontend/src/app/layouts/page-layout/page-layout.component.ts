import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterOutlet, RouterLink, RouterLinkActive, Router, NavigationEnd } from '@angular/router';
import { filter, takeUntil } from 'rxjs/operators';
import { Subject } from 'rxjs';

import { AuthService } from '../../services/auth.service';
import { BreadcrumbComponent, BreadcrumbItem } from '../../shared/breadcrumb/breadcrumb.component';
import { BreadcrumbService } from '../../services/breadcrumb.service';
import { FooterComponent } from '../../components/footer/footer.component';

@Component({
  selector: 'app-page-layout',
  standalone: true,
  imports: [
    CommonModule,
    RouterOutlet,
    RouterLink,
    RouterLinkActive,
    BreadcrumbComponent,
    FooterComponent
  ],
  template: `
    <div class="page-layout">
      <!-- Header -->
      <header class="header">
        <div class="header-container">
          <div class="header-brand">
            <a routerLink="/" class="brand-link">
              <img src="assets/images/logo.png" alt="Exhome" class="brand-logo">
            </a>
          </div>
          
          <nav class="header-nav">
            <a 
              routerLink="/" 
              routerLinkActive="nav-link-active" 
              [routerLinkActiveOptions]="{exact: true}"
              class="nav-link">
              Trang chủ
            </a>
            <a 
              routerLink="/can-ho-chung-cu-ban" 
              routerLinkActive="nav-link-active"
              [routerLinkActiveOptions]="{exact: false}"
              class="nav-link">
              Căn hộ bán
            </a>
            <a 
              routerLink="/can-ho-chung-cu-cho-thue" 
              routerLinkActive="nav-link-active"
              [routerLinkActiveOptions]="{exact: false}"
              class="nav-link">
              Căn hộ cho thuê
            </a>
            <a 
              routerLink="/about" 
              routerLinkActive="nav-link-active"
              class="nav-link">
              Giới thiệu
            </a>
            <a 
              routerLink="/contact" 
              routerLinkActive="nav-link-active"
              class="nav-link">
              Liên hệ
            </a>
          </nav>

          <div class="header-actions">
            <ng-container *ngIf="!authService.isAuthenticated(); else userMenu">
              <a routerLink="/login" class="btn-login">
                Đăng nhập
              </a>
            </ng-container>
            
            <ng-template #userMenu>
              <div class="user-menu">
                <a 
                  routerLink="/dashboard/documents" 
                  class="nav-link">
                  Dashboard
                </a>
                <div class="user-info">
                  <span class="username">{{ authService.getCurrentUser()?.username }}</span>
                  <button class="btn-logout" (click)="logout()">
                    Đăng xuất
                  </button>
                </div>
              </div>
            </ng-template>
          </div>
        </div>
      </header>

      <!-- Content -->
      <main class="main-content" [class.full-width]="isHomePage">
        <div class="content-wrapper" [class.no-max-width]="isHomePage">
          <div class="breadcrumb-container" *ngIf="breadcrumbItems.length > 0 && !isHomePage">
            <app-breadcrumb [items]="breadcrumbItems"></app-breadcrumb>
          </div>
          <div class="page-content">
            <router-outlet></router-outlet>
          </div>
        </div>
      </main>

      <!-- Footer -->
      <app-footer></app-footer>
    </div>
  `,
  styles: [`
    .page-layout {
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      background: var(--bg);
      color: var(--text-body);
    }

    /* Header Styles */
    .header {
      background: rgba(255, 255, 255, 0.8);
      backdrop-filter: blur(8px);
      border-bottom: 1px solid transparent;
      border-image: var(--gradient-brand-border) 1;
      position: sticky;
      top: 0;
      z-index: 100;
    }

    .header::before {
      content: "";
      position: absolute;
      inset: 0;
      background: url("data:image/svg+xml,%3Csvg width='1200' height='100' viewBox='0 0 1200 100' fill='none' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M0 70C180 60 300 80 480 75C660 70 720 50 900 45C1080 40 1200 50 1200 50V100H0V70Z' fill='rgba(19,126,44,0.04)'/%3E%3C/svg%3E") center bottom no-repeat;
      background-size: 1200px auto;
      pointer-events: none;
      opacity: 0.5;
    }

    .header-container {
      max-width: var(--container-max-width);
      margin: 0 auto;
      padding: 0 var(--container-padding);
      display: flex;
      align-items: center;
      justify-content: space-between;
      height: 72px;
      position: relative;
    }

    .header-brand {
      display: flex;
      align-items: center;
    }

    .brand-link {
      display: flex;
      align-items: center;
      gap: 0.75rem;
      text-decoration: none;
      transition: opacity 0.2s ease;
    }

    .brand-link:hover {
      opacity: 0.8;
    }

    .brand-logo {
      height: 40px;
      width: auto;
    }

    .brand-text {
      font-size: var(--font-size-2xl);
      font-weight: var(--font-weight-bold);
      color: var(--brand);
      letter-spacing: var(--letter-spacing-normal);
    }

    .header-nav {
      display: flex;
      align-items: center;
      gap: var(--spacing-xs);
      flex: 1;
      justify-content: center;
    }

    .nav-link {
      color: var(--text-muted);
      text-decoration: none;
      font-size: var(--font-size-base);
      font-weight: var(--font-weight-medium);
      padding: var(--spacing-xs) var(--spacing-md);
      border-radius: var(--radius-md);
      transition: all var(--transition-base);
      position: relative;
    }

    .nav-link:hover {
      color: var(--brand);
      background: var(--brand-soft);
    }

    .nav-link-active {
      color: var(--brand);
      background: var(--brand-soft);
    }

    .header-actions {
      display: flex;
      align-items: center;
      gap: 1rem;
    }

    .btn-login {
      background: linear-gradient(135deg, var(--brand), rgb(88,200,136));
      color: #ffffff;
      text-decoration: none;
      padding: var(--spacing-sm) var(--spacing-lg);
      border-radius: var(--radius-md);
      font-size: var(--font-size-base);
      font-weight: var(--font-weight-semibold);
      transition: all var(--transition-base);
      display: inline-block;
      box-shadow: var(--shadow-md);
    }

    .btn-login:hover {
      transform: translateY(-2px);
      box-shadow: 0 8px 20px rgba(19,126,44,.35);
      background: linear-gradient(135deg, var(--brand-hover), rgb(70,180,120));
    }

    .user-menu {
      display: flex;
      align-items: center;
      gap: 1rem;
    }

    .user-info {
      display: flex;
      align-items: center;
      gap: 0.75rem;
      padding-left: 1rem;
      border-left: 1px solid var(--border);
    }

    .username {
      color: var(--text-muted);
      font-size: 0.9375rem;
      font-weight: 500;
    }

    .btn-logout {
      background: rgba(255,255,255,.6);
      backdrop-filter: blur(8px);
      color: var(--text-main);
      border: 1px solid var(--border);
      padding: var(--spacing-xs) var(--spacing-md);
      border-radius: var(--radius-md);
      font-size: var(--font-size-base);
      font-weight: var(--font-weight-medium);
      cursor: pointer;
      transition: all var(--transition-base);
    }

    .btn-logout:hover {
      color: var(--brand);
      border-color: var(--brand);
      background: var(--brand-soft);
    }

    /* Main Content Styles */
    .main-content {
      flex: 1;
      background: var(--bg);
      padding: 0;
    }

    .main-content.full-width {
      width: 100%;
    }

    .content-wrapper {
      max-width: var(--container-max-width);
      margin: 0 auto;
      padding: 0 var(--container-padding);
    }

    .content-wrapper.no-max-width {
      max-width: none;
      padding: 0;
    }

    .breadcrumb-container {
      margin-bottom: 1.5rem;
      padding-top: 2rem;
    }

    .page-content {
      background: transparent;
      overflow: visible;
    }

    /* Responsive */
    @media (max-width: 1024px) {
      .header-nav {
        display: none;
      }

      .header-container {
        padding: 0 var(--container-padding);
      }
    }

    @media (max-width: 900px) {
      .header-container {
        height: 64px;
        padding: 0 var(--container-padding);
      }

      .brand-text {
        font-size: var(--font-size-xl);
      }

      .brand-logo {
        height: 32px;
      }

      .main-content {
        padding: 0;
      }

      .content-wrapper {
        padding: 0 var(--container-padding);
      }

      .user-info {
        flex-direction: column;
        gap: 0.5rem;
        padding-left: 0.75rem;
        align-items: flex-start;
      }

      .username {
        font-size: var(--font-size-sm);
      }

      .btn-login {
        padding: var(--spacing-xs) var(--spacing-md);
        font-size: var(--font-size-sm);
      }
    }
  `]
})
export class PageLayoutComponent implements OnInit, OnDestroy {
  breadcrumbItems: BreadcrumbItem[] = [];
  isHomePage = false;
  private destroy$ = new Subject<void>();

  constructor(
    public authService: AuthService,
    private router: Router,
    private breadcrumbService: BreadcrumbService
  ) { }

  ngOnInit() {
    // Subscribe to breadcrumb changes from BreadcrumbService
    this.breadcrumbService.breadcrumbs$.subscribe(breadcrumbs => {
      this.breadcrumbItems = breadcrumbs;
    });

    // Check if current route is home page
    this.router.events
      .pipe(
        filter(event => event instanceof NavigationEnd),
        takeUntil(this.destroy$)
      )
      .subscribe(() => {
        this.isHomePage = this.router.url === '/' || this.router.url === '';
      });
    
    // Initial check
    this.isHomePage = this.router.url === '/' || this.router.url === '';
  }

  ngOnDestroy() {
    this.destroy$.next();
    this.destroy$.complete();
  }

  logout(): void {
    this.authService.logout();
    this.router.navigate(['/login']);
  }
} 