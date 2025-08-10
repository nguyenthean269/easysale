import { Component, OnInit } from '@angular/core';
import { RouterOutlet, Router, RouterLink, RouterLinkActive } from '@angular/router';
import { CommonModule } from '@angular/common';
import { SsrService } from '../../services/ssr.service';
import { AuthService } from '../../services/auth.service';
import { NzLayoutModule } from 'ng-zorro-antd/layout';
import { NzMenuModule } from 'ng-zorro-antd/menu';
import { NzIconModule } from 'ng-zorro-antd/icon';
import { NzBreadCrumbModule } from 'ng-zorro-antd/breadcrumb';
import { NzButtonModule } from 'ng-zorro-antd/button';

@Component({
  selector: 'app-admin-layout',
  standalone: true,
  imports: [
    RouterOutlet, 
    RouterLink,
    RouterLinkActive,
    CommonModule,
    NzLayoutModule,
    NzIconModule,
    NzBreadCrumbModule,
    NzButtonModule
  ],
  template: `
    <nz-layout class="min-h-screen">
      <!-- Header -->
      <nz-header class="bg-white border-b border-gray-200 px-6 flex items-center justify-between">
        <div class="flex items-center">
          <h1 class="text-xl font-semibold text-gray-800 m-0">EasySale Admin</h1>
        </div>
        <div class="flex items-center space-x-4">
          <span class="text-gray-600">Welcome, {{ authService.getCurrentUser()?.username }}</span>
          <button nz-button nzType="default" (click)="logout()">
            Logout
          </button>
        </div>
      </nz-header>

      <nz-layout>
        <!-- Sidebar -->
        <nz-sider nzCollapsible nzWidth="200" class="bg-white border-r border-gray-200">
          <div class="p-4">
            <nav class="space-y-2">
              <a routerLink="/dashboard" routerLinkActive="bg-blue-100 text-blue-600" 
                 class="flex items-center px-3 py-2 rounded-lg text-gray-700 hover:bg-gray-100 transition-colors">
                <span class="mr-3">📊</span>
                <span>Dashboard</span>
              </a>
              
              <a routerLink="/dashboard/users" routerLinkActive="bg-blue-100 text-blue-600"
                 class="flex items-center px-3 py-2 rounded-lg text-gray-700 hover:bg-gray-100 transition-colors">
                <span class="mr-3">👥</span>
                <span>Users</span>
              </a>
              <a routerLink="/dashboard/documents" routerLinkActive="bg-blue-100 text-blue-600"
                 class="flex items-center px-3 py-2 rounded-lg text-gray-700 hover:bg-gray-100 transition-colors">
                <span class="mr-3">👥</span>
                <span>Documents</span>
              </a>
              
              <a routerLink="/dashboard/content-generate" routerLinkActive="bg-blue-100 text-blue-600"
                 class="flex items-center px-3 py-2 rounded-lg text-gray-700 hover:bg-gray-100 transition-colors">
                <span class="mr-3">🤖</span>
                <span>Tạo Nội Dung AI</span>
              </a>
              
              <a routerLink="/dashboard/products" routerLinkActive="bg-blue-100 text-blue-600"
                 class="flex items-center px-3 py-2 rounded-lg text-gray-700 hover:bg-gray-100 transition-colors">
                <span class="mr-3">🛍️</span>
                <span>Products</span>
              </a>
              
              <a routerLink="/dashboard/orders" routerLinkActive="bg-blue-100 text-blue-600"
                 class="flex items-center px-3 py-2 rounded-lg text-gray-700 hover:bg-gray-100 transition-colors">
                <span class="mr-3">📦</span>
                <span>Orders</span>
              </a>
              
              <a routerLink="/dashboard/settings" routerLinkActive="bg-blue-100 text-blue-600"
                 class="flex items-center px-3 py-2 rounded-lg text-gray-700 hover:bg-gray-100 transition-colors">
                <span class="mr-3">⚙️</span>
                <span>Settings</span>
              </a>
            </nav>
          </div>
        </nz-sider>

        <!-- Content -->
        <nz-layout>
          <nz-content class="bg-gray-50">
            <router-outlet></router-outlet>
          </nz-content>
        </nz-layout>
      </nz-layout>
    </nz-layout>
  `,
  styles: [`
    /* Custom styles for admin layout */
    :host ::ng-deep .ant-layout-sider {
      box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    :host ::ng-deep .ant-layout-sider-trigger {
      background: #1890ff;
      color: white;
    }
    
    :host ::ng-deep .ant-layout-sider-collapsed .ant-layout-sider-trigger {
      background: #1890ff;
    }
    
    :host ::ng-deep .ant-menu-item {
      margin: 4px 8px !important;
      border-radius: 6px !important;
    }
    
    :host ::ng-deep .ant-menu-item-selected {
      background-color: #1890ff !important;
      color: white !important;
    }
    
    /* Fix layout height */
    :host ::ng-deep .ant-layout {
      min-height: 100vh;
    }
    
    :host ::ng-deep .ant-layout-sider {
      min-height: calc(100vh - 64px);
    }
  `]
})
export class AdminLayoutComponent implements OnInit {
  constructor(
    private router: Router,
    private ssrService: SsrService,
    public authService: AuthService
  ) {}

  ngOnInit() {
    // Đảm bảo dashboard routes chỉ chạy trên client
    if (this.ssrService.isServer() && this.ssrService.isDashboardRoute(this.router.url)) {
      console.log('Dashboard route detected on server - should be client-side only');
    }
  }

  logout(): void {
    this.authService.logout();
    this.router.navigate(['/login']);
  }
} 