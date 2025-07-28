import { HttpRequest, HttpHandlerFn, HttpErrorResponse, HttpEvent } from '@angular/common/http';
import { inject } from '@angular/core';
import { Observable, throwError, switchMap, catchError } from 'rxjs';
import { AuthService } from '../services/auth.service';
import { Router } from '@angular/router';

export function AuthInterceptor(
  request: HttpRequest<unknown>,
  next: HttpHandlerFn
): Observable<HttpEvent<unknown>> {
  const authService = inject(AuthService);
  const router = inject(Router);
  
  // Không intercept refresh endpoint để tránh infinite loop
  if (request.url.includes('/auth/refresh')) {
    console.log('🔄 Skipping interceptor for refresh endpoint');
    return next(request);
  }
  
  const token = authService.getToken();
  
  if (token) {
    request = request.clone({
      setHeaders: {
        Authorization: `Bearer ${token}`
      }
    });
  }

  return next(request).pipe(
    catchError((error: HttpErrorResponse) => {
      console.log('🔄 Interceptor caught error:', error.status, error.url);
      
      if (error.status === 401) {
        console.log('🔄 401 Error detected, attempting token refresh...');
        console.log('Request URL:', request.url);
        
        // Token hết hạn, thử refresh token
        const refreshToken = authService.getRefreshToken();
        console.log('Refresh token available:', !!refreshToken);
        console.log('Refresh token preview:', refreshToken ? `${refreshToken.substring(0, 30)}...` : 'null');
        
        if (refreshToken) {
          console.log('🔄 Calling refresh token API...');
          return authService.refreshToken().pipe(
            switchMap(response => {
              console.log('✅ Token refreshed successfully');
              console.log('New access token:', response.access_token ? `${response.access_token.substring(0, 30)}...` : 'null');
              
              // Tạo lại request với token mới
              const newRequest = request.clone({
                setHeaders: {
                  Authorization: `Bearer ${response.access_token}`
                }
              });
              console.log('🔄 Retrying original request with new token...');
              return next(newRequest);
            }),
            catchError(refreshError => {
              console.log('❌ Refresh token failed:', refreshError);
              // Refresh token cũng hết hạn, đăng xuất
              authService.clearAuth();
              router.navigate(['/login']);
              return throwError(() => refreshError);
            })
          );
        } else {
          console.log('❌ No refresh token available');
          // Không có refresh token, đăng xuất
          authService.clearAuth();
          router.navigate(['/login']);
        }
      }
      return throwError(() => error);
    })
  );
} 