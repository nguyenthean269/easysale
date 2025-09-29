import { bootstrapApplication } from '@angular/platform-browser';
import { appConfig } from './app/app.config';
import { AppComponent } from './app/app.component';
import { importProvidersFrom } from '@angular/core';
import { provideAnimations } from '@angular/platform-browser/animations';
import { provideNzI18n, vi_VN } from 'ng-zorro-antd/i18n';

bootstrapApplication(AppComponent, appConfig)
  .catch((err) => console.error(err));
