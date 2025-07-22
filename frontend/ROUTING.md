# EasySale Frontend Routing Structure

## Overview

This Angular application implements a dual-layout routing system with different rendering strategies:

### 1. Dashboard Routes (No SSR - Client-side only)
- **Path**: `/dashboard/*`
- **Layout**: Admin Layout (`AdminLayoutComponent`)
- **Rendering**: Client-side only (no server-side rendering)
- **Features**: 
  - Dark admin theme
  - Navigation sidebar
  - Dashboard-specific components

#### Available Dashboard Routes:
- `/dashboard` - Main dashboard
- `/dashboard/users` - User management
- `/dashboard/products` - Product management (placeholder)
- `/dashboard/orders` - Order management (placeholder)
- `/dashboard/settings` - Settings (placeholder)

### 2. Regular Routes (With SSR)
- **Path**: All other routes (`/`, `/products`, `/about`, etc.)
- **Layout**: Page Layout (`PageLayoutComponent`)
- **Rendering**: Server-side rendering enabled
- **Features**:
  - Light theme
  - Standard website navigation
  - SEO-friendly

#### Available Regular Routes:
- `/` - Home page
- `/products` - Products page
- `/about` - About page (placeholder)
- `/contact` - Contact page (placeholder)
- `/login` - Login page (placeholder)

## File Structure

```
src/app/
├── layouts/
│   ├── admin-layout/
│   │   └── admin-layout.component.ts
│   └── page-layout/
│       └── page-layout.component.ts
├── pages/
│   ├── dashboard/
│   │   ├── dashboard.component.ts
│   │   └── users/
│   │       └── users.component.ts
│   ├── home/
│   │   └── home.component.ts
│   └── products/
│       └── products.component.ts
├── app.routes.ts
├── app.routes.server.ts
└── app.component.html
```

## Configuration

### Client-side Routing (`app.routes.ts`)
Defines the route structure with layout components and child routes.

### Server-side Routing (`app.routes.server.ts`)
Configures which routes use SSR (Prerender) and which are client-side only.

## Benefits

1. **Performance**: Dashboard routes load faster without SSR overhead
2. **SEO**: Regular routes benefit from server-side rendering
3. **User Experience**: Different layouts for different user types
4. **Maintainability**: Clear separation of concerns

## Adding New Routes

### For Dashboard (Admin):
1. Create component in `pages/dashboard/`
2. Add route to `app.routes.ts` under dashboard children
3. Add navigation link to `AdminLayoutComponent`

### For Regular Pages:
1. Create component in `pages/`
2. Add route to `app.routes.ts` under page layout children
3. Add navigation link to `PageLayoutComponent`
4. Add route to `app.routes.server.ts` for SSR 