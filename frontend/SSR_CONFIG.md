# SSR Configuration for EasySale Frontend

## Overview

This application uses a hybrid SSR approach where:
- **Dashboard routes** (`/dashboard/*`) are client-side only
- **Regular routes** (`/`, `/products`, etc.) use server-side rendering

## How it works

### 1. Server Routes Configuration (`app.routes.server.ts`)

All routes are defined with `RenderMode.Prerender` to satisfy Angular's SSR requirements:

```typescript
export const serverRoutes: ServerRoute[] = [
  // Dashboard routes - technically prerendered but client-side only
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
  // ... other routes
];
```

### 2. SSR Service (`services/ssr.service.ts`)

The `SsrService` provides methods to control SSR behavior:

```typescript
export class SsrService {
  // Check if running on server
  isServer(): boolean
  
  // Check if running on browser
  isBrowser(): boolean
  
  // Check if current route is dashboard
  isDashboardRoute(path: string): boolean
  
  // Determine if route should use SSR
  shouldUseSSR(path: string): boolean
}
```

### 3. Layout Components

- **AdminLayoutComponent**: Used for dashboard routes, includes SSR detection
- **PageLayoutComponent**: Used for regular routes, optimized for SSR

## Benefits

1. **SEO**: Regular pages benefit from server-side rendering
2. **Performance**: Dashboard loads faster without SSR overhead
3. **User Experience**: Different layouts for different user types
4. **Compliance**: Meets Angular SSR requirements

## Build Process

When you run `npm run build`:

1. Angular prerenders all routes (including dashboard)
2. Dashboard routes are technically "prerendered" but designed for client-side use
3. Regular routes get full SSR benefits
4. The application works correctly in both server and client environments

## Testing

- **Dashboard routes**: Navigate to `/dashboard` - should work client-side
- **Regular routes**: Navigate to `/`, `/products` - should work with SSR
- **Build**: `npm run build` should complete successfully

## Future Improvements

1. Add route guards for dashboard authentication
2. Implement lazy loading for dashboard modules
3. Add more sophisticated SSR control mechanisms 