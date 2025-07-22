import { RenderMode, ServerRoute } from '@angular/ssr';

export const serverRoutes: ServerRoute[] = [
  // Dashboard routes - will be client-side rendered
  {
    path: 'dashboard',
    renderMode: RenderMode.Prerender
  },
  {
    path: 'dashboard/**',
    renderMode: RenderMode.Prerender
  },
  
  // Regular routes - with SSR
  {
    path: '',
    renderMode: RenderMode.Prerender
  },
  {
    path: 'products',
    renderMode: RenderMode.Prerender
  },
  {
    path: 'about',
    renderMode: RenderMode.Prerender
  },
  {
    path: 'contact',
    renderMode: RenderMode.Prerender
  },
  {
    path: 'login',
    renderMode: RenderMode.Prerender
  }
];
