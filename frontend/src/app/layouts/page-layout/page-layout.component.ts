import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterOutlet, RouterLink, RouterLinkActive, Router } from '@angular/router';
import { NzLayoutModule } from 'ng-zorro-antd/layout';
import { NzMenuModule } from 'ng-zorro-antd/menu';
import { NzButtonModule } from 'ng-zorro-antd/button';

import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-page-layout',
  standalone: true,
  imports: [
    CommonModule,
    RouterOutlet, 
    RouterLink, 
    RouterLinkActive,
    NzLayoutModule,
    NzMenuModule,
    NzButtonModule
  ],
  template: `
    <nz-layout class="min-h-screen">
      <!-- Header -->
      <nz-header class="bg-white border-b border-gray-200 px-6 flex items-center justify-between">
        <div class="flex items-center">
          <a routerLink="/" class="text-2xl font-bold text-blue-600 no-underline">
            EasySale
          </a>
        </div>
        
        <nav class="flex items-center space-x-6">
          <a 
            routerLink="/" 
            routerLinkActive="text-blue-600 font-medium" 
            [routerLinkActiveOptions]="{exact: true}"
            class="text-gray-600 hover:text-blue-600 transition-colors">
            Home
          </a>
          <a 
            routerLink="/products" 
            routerLinkActive="text-blue-600 font-medium"
            class="text-gray-600 hover:text-blue-600 transition-colors">
            Products
          </a>
          <a 
            routerLink="/about" 
            routerLinkActive="text-blue-600 font-medium"
            class="text-gray-600 hover:text-blue-600 transition-colors">
            About
          </a>
          <a 
            routerLink="/contact" 
            routerLinkActive="text-blue-600 font-medium"
            class="text-gray-600 hover:text-blue-600 transition-colors">
            Contact
          </a>
          <ng-container *ngIf="!authService.isAuthenticated(); else userMenu">
            <button nz-button nzType="primary" routerLink="/login">
              Login
            </button>
          </ng-container>
          
          <ng-template #userMenu>
            <a 
              routerLink="/dashboard/documents" 
              routerLinkActive="text-blue-600 font-medium"
              class="text-gray-600 hover:text-blue-600 transition-colors">
              Dashboard
            </a>
            <div class="flex items-center space-x-2">
              <span class="text-gray-600">{{ authService.getCurrentUser()?.username }}</span>
              <button nz-button nzType="default" (click)="logout()">
                Logout
              </button>
              <button *ngIf="authService.isAdmin()" nz-button nzType="primary" routerLink="/dashboard">
                Dashboard
              </button>
            </div>
          </ng-template>
        </nav>
      </nz-header>

      <!-- Content -->
      <nz-content class="flex-1">
        <router-outlet></router-outlet>
      </nz-content>

      <!-- Footer -->
      <nz-footer class="bg-gray-50 border-t border-gray-200 text-center py-8">
        <div class="max-w-6xl mx-auto px-6">
          <p class="text-gray-600">&copy; 2024 EasySale. All rights reserved.</p>
        </div>
      </nz-footer>
    </nz-layout>
  `,
  styles: [`
    /* Custom styles for page layout */
    :host ::ng-deep .ant-layout-header {
      height: auto !important;
      line-height: normal !important;
      padding: 1rem 1.5rem !important;
    }
    
    :host ::ng-deep .ant-layout-footer {
      padding: 2rem 0 !important;
    }
  `]
})
export class PageLayoutComponent {
  constructor(
    public authService: AuthService,
    private router: Router
  ) {}

  logout(): void {
    this.authService.logout();
    this.router.navigate(['/login']);
  }
} 