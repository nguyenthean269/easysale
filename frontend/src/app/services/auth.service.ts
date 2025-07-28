import { Injectable, Inject, PLATFORM_ID } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable, tap } from 'rxjs';
import { isPlatformBrowser } from '@angular/common';
import { environment } from '../../environments/environment';

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  message: string;
  access_token: string;
  refresh_token: string;
  user: {
    id: number;
    username: string;
    full_name: string;
    email: string;
    role: string;
  };
}

export interface RefreshResponse {
  access_token: string;
  message: string;
}

export interface User {
  id: number;
  username: string;
  full_name: string;
  email: string;
  role: string;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private currentUserSubject = new BehaviorSubject<User | null>(null);
  public currentUser$ = this.currentUserSubject.asObservable();

  constructor(
    private http: HttpClient,
    @Inject(PLATFORM_ID) private platformId: Object
  ) {
    // Kiểm tra token trong localStorage khi khởi tạo (chỉ trên browser)
    if (isPlatformBrowser(this.platformId)) {
      this.loadUserFromStorage();
    }
  }

  private loadUserFromStorage(): void {
    if (!isPlatformBrowser(this.platformId)) {
      return;
    }
    
    const token = localStorage.getItem('access_token');
    const refreshToken = localStorage.getItem('refresh_token');
    const userStr = localStorage.getItem('current_user');
    
    if (token && refreshToken && userStr) {
      try {
        const user = JSON.parse(userStr);
        this.currentUserSubject.next(user);
      } catch (error) {
        this.clearAuth();
      }
    }
  }

  login(credentials: LoginRequest): Observable<LoginResponse> {
    return this.http.post<LoginResponse>(`${environment.apiBaseUrl}/auth/login`, credentials)
      .pipe(
        tap(response => {
          console.log('🔐 Login response:', response);
          console.log('Access token:', response.access_token ? 'Present' : 'Missing');
          console.log('Refresh token:', response.refresh_token ? 'Present' : 'Missing');
          
          // Lưu token và user info (chỉ trên browser)
          if (isPlatformBrowser(this.platformId)) {
            localStorage.setItem('access_token', response.access_token);
            localStorage.setItem('refresh_token', response.refresh_token);
            localStorage.setItem('current_user', JSON.stringify(response.user));
            
            console.log('✅ Tokens saved to localStorage');
            console.log('Access token in localStorage:', !!localStorage.getItem('access_token'));
            console.log('Refresh token in localStorage:', !!localStorage.getItem('refresh_token'));
          }
          this.currentUserSubject.next(response.user);
        })
      );
  }

  refreshToken(): Observable<RefreshResponse> {
    const refreshToken = this.getRefreshToken();
    console.log('🔄 AuthService.refreshToken() called');
    console.log('Refresh token available:', !!refreshToken);
    
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }
    
    console.log('🔄 Making refresh API call with refresh token...');
    return this.http.post<RefreshResponse>(`${environment.apiBaseUrl}/auth/refresh`, {}, {
      headers: {
        'Authorization': `Bearer ${refreshToken}`
      }
    }).pipe(
      tap(response => {
        console.log('✅ Refresh API response received:', response);
        if (isPlatformBrowser(this.platformId)) {
          localStorage.setItem('access_token', response.access_token);
          console.log('✅ New access token saved to localStorage');
        }
      })
    );
  }

  logout(): Observable<any> {
    return this.http.post(`${environment.apiBaseUrl}/auth/logout`, {}, {
      headers: {
        'Authorization': `Bearer ${this.getToken()}`
      }
    }).pipe(
      tap(() => {
        this.clearAuth();
      })
    );
  }

  clearAuth(): void {
    if (isPlatformBrowser(this.platformId)) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('current_user');
    }
    this.currentUserSubject.next(null);
  }

  getToken(): string | null {
    if (!isPlatformBrowser(this.platformId)) {
      return null;
    }
    return localStorage.getItem('access_token');
  }

  getRefreshToken(): string | null {
    if (!isPlatformBrowser(this.platformId)) {
      return null;
    }
    return localStorage.getItem('refresh_token');
  }

  isAuthenticated(): boolean {
    return !!(this.getToken() && this.getRefreshToken());
  }

  getCurrentUser(): User | null {
    return this.currentUserSubject.value;
  }

  isAdmin(): boolean {
    const user = this.getCurrentUser();
    return user?.role === 'admin';
  }
} 