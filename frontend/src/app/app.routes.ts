import { Routes } from '@angular/router';
import { AdminLayoutComponent } from './layouts/admin-layout/admin-layout.component';
import { PageLayoutComponent } from './layouts/page-layout/page-layout.component';
import { DashboardComponent } from './pages/dashboard/dashboard.component';
import { UsersComponent } from './pages/dashboard/users/users.component';
import { HomeComponent } from './pages/home/home.component';
import { ProductsComponent } from './pages/products/products.component';
import { LoginComponent } from './pages/login/login.component';
import { ContentGenerateComponent } from './pages/content-generate/content-generate.component';

export const routes: Routes = [
  // Dashboard routes with admin layout (no SSR)
  {
    path: 'dashboard',
    component: AdminLayoutComponent,
    children: [
      { path: '', component: DashboardComponent },
      { path: 'documents', component: UsersComponent },
      { path: 'content-generate', component: ContentGenerateComponent },
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
      { path: 'about', component: HomeComponent }, // Placeholder
      { path: 'contact', component: HomeComponent }, // Placeholder
    ]
  }
];
