import { ApplicationConfig, provideZoneChangeDetection } from '@angular/core';
import { provideRouter } from '@angular/router';
import { provideAnimations } from '@angular/platform-browser/animations';
import { provideHttpClient, withInterceptors, withFetch } from '@angular/common/http';

import { routes } from './app.routes';
import { AuthInterceptor } from './interceptors/auth.interceptor';
import { provideNzI18n, vi_VN } from 'ng-zorro-antd/i18n';
import { NzMessageService } from 'ng-zorro-antd/message';
import { provideClientHydration, withEventReplay, withHttpTransferCacheOptions } from '@angular/platform-browser';


export const appConfig: ApplicationConfig = {
  providers: [
    provideZoneChangeDetection({ eventCoalescing: true }),
    provideRouter(routes),
    provideAnimations(),
    provideHttpClient(withInterceptors([AuthInterceptor]), withFetch()),
    provideNzI18n(vi_VN),
    {
      provide: 'NzMessageService',
      useClass: NzMessageService
    }, provideClientHydration(
      withEventReplay(),
      withHttpTransferCacheOptions({ includePostRequests: true })
    )
  ]
};
