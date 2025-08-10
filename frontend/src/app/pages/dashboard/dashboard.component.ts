import { Component } from '@angular/core';
import { NzCardModule } from 'ng-zorro-antd/card';
import { NzStatisticModule } from 'ng-zorro-antd/statistic';
import { NzGridModule } from 'ng-zorro-antd/grid';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [NzCardModule, NzStatisticModule, NzGridModule],
  template: `
    <div class="p-6">
      <div class="bg-white p-6 rounded-lg shadow-sm">
        <div class="space-y-6">
          <div class="flex items-center justify-between">
            <h1 class="text-2xl font-semibold text-gray-800">Dashboard</h1>
            <span class="text-gray-500">Welcome back, Admin!</span>
          </div>
      
      <nz-row [nzGutter]="[16, 16]">
        <nz-col [nzSpan]="6">
          <nz-card class="shadow-sm">
            <nz-statistic
              nzTitle="Total Users"
              [nzValue]="1234"
              [nzValueStyle]="{ color: '#3f8600' }">
            </nz-statistic>
          </nz-card>
        </nz-col>
        
        <nz-col [nzSpan]="6">
          <nz-card class="shadow-sm">
            <nz-statistic
              nzTitle="Total Products"
              [nzValue]="567"
              [nzValueStyle]="{ color: '#1890ff' }">
            </nz-statistic>
          </nz-card>
        </nz-col>
        
        <nz-col [nzSpan]="6">
          <nz-card class="shadow-sm">
            <nz-statistic
              nzTitle="Total Orders"
              [nzValue]="890"
              [nzValueStyle]="{ color: '#722ed1' }">
            </nz-statistic>
          </nz-card>
        </nz-col>
        
        <nz-col [nzSpan]="6">
          <nz-card class="shadow-sm">
            <nz-statistic
              nzTitle="Revenue"
              [nzValue]="12345"
              nzPrefix="$"
              [nzValueStyle]="{ color: '#cf1322' }">
            </nz-statistic>
          </nz-card>
        </nz-col>
      </nz-row>
      
      <nz-row [nzGutter]="[16, 16]" class="mt-6">
        <nz-col [nzSpan]="12">
          <nz-card title="Recent Activity" class="shadow-sm">
            <p class="text-gray-600">No recent activity</p>
          </nz-card>
        </nz-col>
        
        <nz-col [nzSpan]="12">
          <nz-card title="Quick Actions" class="shadow-sm">
            <div class="space-y-2">
              <button class="w-full text-left px-3 py-2 rounded hover:bg-gray-50 transition-colors">
                Add New Product
              </button>
              <button class="w-full text-left px-3 py-2 rounded hover:bg-gray-50 transition-colors">
                View Orders
              </button>
              <button class="w-full text-left px-3 py-2 rounded hover:bg-gray-50 transition-colors">
                Manage Users
              </button>
            </div>
          </nz-card>
        </nz-col>
      </nz-row>
        </div>
      </div>
    </div>
  `,
  styles: [`
    /* Custom styles for dashboard */
    :host ::ng-deep .ant-card {
      border-radius: 8px;
      border: 1px solid #f0f0f0;
    }
    
    :host ::ng-deep .ant-statistic-title {
      font-size: 14px;
      color: #666;
    }
    
    :host ::ng-deep .ant-statistic-content {
      font-size: 24px;
      font-weight: 600;
    }
  `]
})
export class DashboardComponent {} 