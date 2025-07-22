import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { NzFormModule } from 'ng-zorro-antd/form';
import { NzInputModule } from 'ng-zorro-antd/input';
import { NzButtonModule } from 'ng-zorro-antd/button';
import { NzCardModule } from 'ng-zorro-antd/card';
import { NzMessageService } from 'ng-zorro-antd/message';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    NzFormModule,
    NzInputModule,
    NzButtonModule,
    NzCardModule
  ],
  template: `
    <div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div class="max-w-md w-full space-y-8">
        <div class="text-center">
          <h2 class="text-3xl font-bold text-gray-900">Sign in to EasySale</h2>
          <p class="mt-2 text-sm text-gray-600">
            Welcome back! Please sign in to your account.
          </p>
        </div>
        
        <nz-card class="shadow-lg">
          <form nz-form [formGroup]="loginForm" (ngSubmit)="onSubmit()" class="space-y-6">
            <nz-form-item>
              <nz-form-label [nzSpan]="24" nzRequired>Username</nz-form-label>
              <nz-form-control nzErrorTip="Please input your username!">
                <input 
                  nz-input 
                  formControlName="username" 
                  placeholder="Enter your username"
                  type="text" />
              </nz-form-control>
            </nz-form-item>

            <nz-form-item>
              <nz-form-label [nzSpan]="24" nzRequired>Password</nz-form-label>
              <nz-form-control nzErrorTip="Please input your password!">
                <input 
                  nz-input 
                  formControlName="password" 
                  placeholder="Enter your password"
                  type="password" />
              </nz-form-control>
            </nz-form-item>

            <nz-form-item>
              <nz-form-control>
                <button 
                  nz-button 
                  nzType="primary" 
                  nzSize="large" 
                  class="w-full"
                  [nzLoading]="isLoading"
                  >
                  Sign In
                </button>
              </nz-form-control>
            </nz-form-item>
          </form>
        </nz-card>
      </div>
    </div>
  `,
  styles: [`
    :host ::ng-deep .ant-form-item {
      margin-bottom: 16px;
    }
    
    :host ::ng-deep .ant-card {
      border-radius: 8px;
    }
  `]
})
export class LoginComponent {
  loginForm: FormGroup;
  isLoading = false;

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private router: Router,
    private message: NzMessageService
  ) {
    this.loginForm = this.fb.group({
      username: ['', [Validators.required]],
      password: ['', [Validators.required, Validators.minLength(6)]]
    });
  }

  onSubmit(): void {
    if (this.loginForm.valid) {
      this.isLoading = true;
      
      this.authService.login(this.loginForm.value).subscribe({
        next: (response) => {
          this.message.success('Login successful!');
          
          // Redirect based on user role
          if (response.user.role === 'admin') {
            this.router.navigate(['/dashboard']);
          } else {
            this.router.navigate(['/']);
          }
        },
        error: (error) => {
          this.isLoading = false;
          console.error('Login error:', error);
          
          if (error.status === 401) {
            this.message.error('Invalid username or password');
          } else {
            this.message.error('Login failed. Please try again.');
          }
        },
        complete: () => {
          this.isLoading = false;
        }
      });
    } else {
      this.markFormGroupTouched();
    }
  }

  private markFormGroupTouched(): void {
    Object.keys(this.loginForm.controls).forEach(key => {
      const control = this.loginForm.get(key);
      control?.markAsTouched();
    });
  }
} 