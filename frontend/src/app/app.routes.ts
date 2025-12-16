import { Routes } from '@angular/router';
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
import { createApartmentListingMatcher } from './pages/shared/route-matcher.util';

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
      { matcher: createApartmentListingMatcher('can-ho-chung-cu-ban'), component: CanHoChungCuBanComponent },
      { matcher: createApartmentListingMatcher('can-ho-chung-cu-cho-thue'), component: CanHoChungCuChoThueComponent },
      { path: 'about', component: HomeComponent }, // Placeholder
      { path: 'contact', component: HomeComponent }, // Placeholder
    ]
  }
];
