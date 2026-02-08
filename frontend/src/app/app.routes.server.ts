import { RenderMode, ServerRoute } from '@angular/ssr';

export const serverRoutes: ServerRoute[] = [
  // Chỉ prerender các route có path tĩnh (không dùng matcher)
  { path: '', renderMode: RenderMode.Prerender },
  { path: 'about', renderMode: RenderMode.Prerender },
  { path: 'contact', renderMode: RenderMode.Prerender },
  { path: 'login', renderMode: RenderMode.Prerender },
  { path: 'dashboard', renderMode: RenderMode.Client },
  { path: 'dashboard/*', renderMode: RenderMode.Client },
  // Route có matcher (can-ho-chung-cu-ban, can-ho-chung-cu-cho-thue, dashboard, ...) dùng Server
  { path: '**', renderMode: RenderMode.Server }
];
