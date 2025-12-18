import { Injectable } from '@angular/core';
import { Observable, of, Subject } from 'rxjs';
import { tap, shareReplay } from 'rxjs';

interface CacheEntry<T> {
  observable: Observable<T>;
  expiresAt: number;
}

@Injectable({
  providedIn: 'root'
})
export class ApiCacheService {
  private cache = new Map<string, CacheEntry<any>>();
  private clearCache$ = new Subject<string>();
  private readonly DEFAULT_TTL = 5 * 60 * 1000; // 5 minutes

  constructor() {}

  /**
   * Get cached data or execute the API call
   * @param key Cache key
   * @param apiCall Function that returns the Observable API call
   * @param ttl Time-to-live in milliseconds (default: 5 minutes)
   */
  get<T>(key: string, apiCall: () => Observable<T>, ttl: number = this.DEFAULT_TTL): Observable<T> {
    const now = Date.now();
    const cached = this.cache.get(key);

    // Return cached data if still valid
    if (cached && cached.expiresAt > now) {
      return cached.observable;
    }

    // Execute API call and cache the result
    const observable = apiCall().pipe(
      shareReplay(1), // Share the result with all subscribers
      tap(() => {
        // Set expiration time
        this.cache.set(key, {
          observable,
          expiresAt: now + ttl
        });
      })
    );

    // Cache immediately to prevent duplicate calls
    this.cache.set(key, {
      observable,
      expiresAt: now + ttl
    });

    return observable;
  }

  /**
   * Clear specific cache entry
   */
  clear(key: string): void {
    this.cache.delete(key);
    this.clearCache$.next(key);
  }

  /**
   * Clear all cache entries
   */
  clearAll(): void {
    this.cache.clear();
  }

  /**
   * Clear cache entries matching a pattern
   */
  clearPattern(pattern: RegExp): void {
    const keysToDelete: string[] = [];
    this.cache.forEach((_, key) => {
      if (pattern.test(key)) {
        keysToDelete.push(key);
      }
    });
    keysToDelete.forEach(key => this.clear(key));
  }
}
