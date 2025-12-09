import { Routes, UrlMatchResult, UrlSegment } from '@angular/router';
import { AdminLayoutComponent } from './layouts/admin-layout/admin-layout.component';
import { PageLayoutComponent } from './layouts/page-layout/page-layout.component';
import { DashboardComponent } from './pages/dashboard/dashboard.component';
import { UsersComponent } from './pages/dashboard/users/users.component';
import { HomeComponent } from './pages/home/home.component';
import { ProductsComponent } from './pages/products/products.component';
import { LoginComponent } from './pages/login/login.component';
import { ContentGenerateComponent } from './pages/content-generate/content-generate.component';
import { PostComponent } from './pages/dashboard/post/post.component';
import { ZaloTestComponent } from './pages/zalo-test/zalo-test.component';
import { ZaloBotComponent } from './pages/zalo-bot/zalo-bot.component';
import { CanHoChungCuBanComponent } from './pages/can-ho-chung-cu-ban/can-ho-chung-cu-ban.component';
import { CanHoChungCuChoThueComponent } from './pages/can-ho-chung-cu-cho-thue/can-ho-chung-cu-cho-thue.component';

// Custom matcher để match route với dấu phẩy trong path
export function canHoChungCuBanMatcher(segments: UrlSegment[]): UrlMatchResult | null {
  if (segments.length === 0) {
    return null;
  }
  
  const firstSegment = segments[0].path;
  
  // Match nếu segment bắt đầu với 'can-ho-chung-cu-ban'
  if (firstSegment.startsWith('can-ho-chung-cu-ban')) {
    return { consumed: segments };
  }
  
  return null;
}

export function canHoChungCuChoThueMatcher(segments: UrlSegment[]): UrlMatchResult | null {
  if (segments.length === 0) {
    return null;
  }
  
  const firstSegment = segments[0].path;
  
  // Match nếu segment bắt đầu với 'can-ho-chung-cu-cho-thue'
  if (firstSegment.startsWith('can-ho-chung-cu-cho-thue')) {
    return { consumed: segments };
  }
  
  return null;
}

export const routes: Routes = [
  // Dashboard routes with admin layout (no SSR)
  {
    path: 'dashboard',
    component: AdminLayoutComponent,
    children: [
      { path: '', component: DashboardComponent },
      { path: 'documents', component: UsersComponent },
      { path: 'content-generate', component: ContentGenerateComponent },
      { path: 'post', component: PostComponent },
      { path: 'zalo-test', component: ZaloTestComponent },
      { path: 'zalo-bot', component: ZaloBotComponent },
      { path: 'products', component: DashboardComponent }, // Placeholder
      { path: 'orders', component: DashboardComponent }, // Placeholder
      { path: 'settings', component: DashboardComponent }, // Placeholder
    ]
  },
  
  // Login route (no layout)
  { path: 'login', component: LoginComponent },
  
  // Regular routes with page layout (with SSR)
  {
    path: '',
    component: PageLayoutComponent,
    children: [
      { path: '', component: HomeComponent },
      { path: 'products', component: ProductsComponent },
      { matcher: canHoChungCuBanMatcher, component: CanHoChungCuBanComponent },
      { matcher: canHoChungCuChoThueMatcher, component: CanHoChungCuChoThueComponent },
      { path: 'about', component: HomeComponent }, // Placeholder
      { path: 'contact', component: HomeComponent }, // Placeholder
    ]
  }
];
