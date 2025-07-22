import { Injectable, Inject, PLATFORM_ID } from '@angular/core';
import { isPlatformServer } from '@angular/common';

@Injectable({
  providedIn: 'root'
})
export class SsrService {
  constructor(@Inject(PLATFORM_ID) private platformId: Object) {}

  /**
   * Kiểm tra xem có đang chạy trên server không
   */
  isServer(): boolean {
    return isPlatformServer(this.platformId);
  }

  /**
   * Kiểm tra xem có đang chạy trên browser không
   */
  isBrowser(): boolean {
    return !isPlatformServer(this.platformId);
  }

  /**
   * Kiểm tra xem route hiện tại có phải là dashboard route không
   */
  isDashboardRoute(path: string): boolean {
    return path.startsWith('/dashboard');
  }

  /**
   * Kiểm tra xem route có nên sử dụng SSR không
   */
  shouldUseSSR(path: string): boolean {
    // Dashboard routes không sử dụng SSR
    if (this.isDashboardRoute(path)) {
      return false;
    }
    
    // Các routes khác sử dụng SSR
    return true;
  }
} 