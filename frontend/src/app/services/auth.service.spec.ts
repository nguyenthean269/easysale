import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { PLATFORM_ID } from '@angular/core';
import { AuthService, LoginRequest, LoginResponse, RefreshResponse } from './auth.service';
import { environment } from '../../environments/environment';

describe('AuthService', () => {
  let service: AuthService;
  let httpMock: HttpTestingController;
  let platformId: any;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [
        AuthService,
        { provide: PLATFORM_ID, useValue: 'browser' }
      ]
    });
    service = TestBed.inject(AuthService);
    httpMock = TestBed.inject(HttpTestingController);
    platformId = TestBed.inject(PLATFORM_ID);
    
    // Clear localStorage before each test
    localStorage.clear();
  });

  afterEach(() => {
    httpMock.verify();
    localStorage.clear();
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  describe('login', () => {
    it('should store tokens and user data on successful login', () => {
      const mockLoginRequest: LoginRequest = {
        username: 'testuser',
        password: 'testpass'
      };

      const mockResponse: LoginResponse = {
        access_token: 'mock-access-token',
        refresh_token: 'mock-refresh-token',
        token_type: 'Bearer',
        user: {
          id: 1,
          username: 'testuser',
          name: 'Test User',
          role: 'user'
        }
      };

      service.login(mockLoginRequest).subscribe(response => {
        expect(response).toEqual(mockResponse);
        expect(localStorage.getItem('access_token')).toBe('mock-access-token');
        expect(localStorage.getItem('refresh_token')).toBe('mock-refresh-token');
        expect(localStorage.getItem('current_user')).toBe(JSON.stringify(mockResponse.user));
      });

      const req = httpMock.expectOne(`${environment.apiBaseUrl}/auth/login`);
      expect(req.request.method).toBe('POST');
      expect(req.request.body).toEqual(mockLoginRequest);
      req.flush(mockResponse);
    });
  });

  describe('refreshToken', () => {
    it('should refresh access token successfully', () => {
      // Setup: Store refresh token
      localStorage.setItem('refresh_token', 'mock-refresh-token');

      const mockResponse: RefreshResponse = {
        access_token: 'new-access-token',
        message: 'Token đã được refresh thành công'
      };

      service.refreshToken().subscribe(response => {
        expect(response).toEqual(mockResponse);
        expect(localStorage.getItem('access_token')).toBe('new-access-token');
      });

      const req = httpMock.expectOne(`${environment.apiBaseUrl}/auth/refresh`);
      expect(req.request.method).toBe('POST');
      expect(req.request.headers.get('Authorization')).toBe('Bearer mock-refresh-token');
      req.flush(mockResponse);
    });

    it('should throw error when no refresh token available', () => {
      expect(() => service.refreshToken()).toThrow('No refresh token available');
    });
  });

  describe('logout', () => {
    it('should call logout endpoint and clear auth data', () => {
      // Setup: Store tokens
      localStorage.setItem('access_token', 'mock-access-token');
      localStorage.setItem('refresh_token', 'mock-refresh-token');
      localStorage.setItem('current_user', '{"id": 1}');

      service.logout().subscribe();

      const req = httpMock.expectOne(`${environment.apiBaseUrl}/auth/logout`);
      expect(req.request.method).toBe('POST');
      expect(req.request.headers.get('Authorization')).toBe('Bearer mock-access-token');
      req.flush({ message: 'Đăng xuất thành công' });

      // Check that auth data is cleared
      expect(localStorage.getItem('access_token')).toBeNull();
      expect(localStorage.getItem('refresh_token')).toBeNull();
      expect(localStorage.getItem('current_user')).toBeNull();
    });
  });

  describe('getToken', () => {
    it('should return access token from localStorage', () => {
      localStorage.setItem('access_token', 'test-token');
      expect(service.getToken()).toBe('test-token');
    });

    it('should return null when no token exists', () => {
      expect(service.getToken()).toBeNull();
    });
  });

  describe('getRefreshToken', () => {
    it('should return refresh token from localStorage', () => {
      localStorage.setItem('refresh_token', 'test-refresh-token');
      expect(service.getRefreshToken()).toBe('test-refresh-token');
    });

    it('should return null when no refresh token exists', () => {
      expect(service.getRefreshToken()).toBeNull();
    });
  });

  describe('isAuthenticated', () => {
    it('should return true when both tokens exist', () => {
      localStorage.setItem('access_token', 'test-token');
      localStorage.setItem('refresh_token', 'test-refresh-token');
      expect(service.isAuthenticated()).toBe(true);
    });

    it('should return false when only access token exists', () => {
      localStorage.setItem('access_token', 'test-token');
      expect(service.isAuthenticated()).toBe(false);
    });

    it('should return false when only refresh token exists', () => {
      localStorage.setItem('refresh_token', 'test-refresh-token');
      expect(service.isAuthenticated()).toBe(false);
    });

    it('should return false when no tokens exist', () => {
      expect(service.isAuthenticated()).toBe(false);
    });
  });

  describe('clearAuth', () => {
    it('should clear all auth data from localStorage', () => {
      // Setup: Store auth data
      localStorage.setItem('access_token', 'test-token');
      localStorage.setItem('refresh_token', 'test-refresh-token');
      localStorage.setItem('current_user', '{"id": 1}');

      service.clearAuth();

      expect(localStorage.getItem('access_token')).toBeNull();
      expect(localStorage.getItem('refresh_token')).toBeNull();
      expect(localStorage.getItem('current_user')).toBeNull();
    });
  });
}); 