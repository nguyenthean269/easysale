import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { NzTableModule } from 'ng-zorro-antd/table';
import { NzSpinModule } from 'ng-zorro-antd/spin';
import { NzCardModule } from 'ng-zorro-antd/card';
import { NzTagModule } from 'ng-zorro-antd/tag';
import { NzPaginationModule } from 'ng-zorro-antd/pagination';
import { NzFormModule } from 'ng-zorro-antd/form';
import { NzInputModule } from 'ng-zorro-antd/input';
import { NzInputNumberModule } from 'ng-zorro-antd/input-number';
import { NzButtonModule } from 'ng-zorro-antd/button';
import { NzGridModule } from 'ng-zorro-antd/grid';
import { FormsModule } from '@angular/forms';
import { WarehouseService, Apartment } from '../../services/warehouse.service';
import { Subject, takeUntil } from 'rxjs';

@Component({
  selector: 'app-can-ho-chung-cu-cho-thue',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    FormsModule,
    NzTableModule,
    NzSpinModule,
    NzCardModule,
    NzTagModule,
    NzPaginationModule,
    NzFormModule,
    NzInputModule,
    NzInputNumberModule,
    NzButtonModule,
    NzGridModule
  ],
  template: `
    <div class="p-6">
      <div class="bg-white p-6 rounded-lg shadow-sm">
        <div class="space-y-6">
          <div class="flex items-center justify-between">
            <h1 class="text-2xl font-semibold text-gray-800">Căn hộ chung cư cho thuê</h1>
          </div>
          
          <!-- Filter Form -->
          <nz-card nzTitle="Bộ lọc" [nzBordered]="false" class="mb-4">
            <form nz-form [nzLayout]="'inline'" class="w-full">
              <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
                <div>
                  <label class="block text-sm font-medium mb-2">Dự án (ID)</label>
                  <input 
                    nz-input 
                    [(ngModel)]="filters.duAn"
                    name="duAn"
                    placeholder="Nhập ID dự án"
                    class="w-full"
                  />
                </div>
                <div>
                  <label class="block text-sm font-medium mb-2">Giá từ (VNĐ)</label>
                  <nz-input-number 
                    [(ngModel)]="filters.giaTu"
                    name="giaTu"
                    [nzMin]="0"
                    [nzFormatter]="formatPriceInput"
                    [nzParser]="parsePriceInput"
                    class="w-full"
                    placeholder="Giá từ">
                  </nz-input-number>
                </div>
                <div>
                  <label class="block text-sm font-medium mb-2">Giá đến (VNĐ)</label>
                  <nz-input-number 
                    [(ngModel)]="filters.giaDen"
                    name="giaDen"
                    [nzMin]="0"
                    [nzFormatter]="formatPriceInput"
                    [nzParser]="parsePriceInput"
                    class="w-full"
                    placeholder="Giá đến">
                  </nz-input-number>
                </div>
                <div>
                  <label class="block text-sm font-medium mb-2">Diện tích từ (m²)</label>
                  <nz-input-number 
                    [(ngModel)]="filters.dienTichTu"
                    name="dienTichTu"
                    [nzMin]="0"
                    [nzStep]="1"
                    class="w-full"
                    placeholder="Diện tích từ">
                  </nz-input-number>
                </div>
                <div>
                  <label class="block text-sm font-medium mb-2">Diện tích đến (m²)</label>
                  <nz-input-number 
                    [(ngModel)]="filters.dienTichToi"
                    name="dienTichToi"
                    [nzMin]="0"
                    [nzStep]="1"
                    class="w-full"
                    placeholder="Diện tích đến">
                  </nz-input-number>
                </div>
              </div>
              <div class="mt-4 flex justify-end gap-2">
                <button nz-button nzType="default" (click)="resetFilters()">
                  Xóa bộ lọc
                </button>
                <button nz-button nzType="primary" (click)="applyFilters()">
                  Lọc
                </button>
              </div>
            </form>
          </nz-card>
          
          <nz-spin [nzSpinning]="loading">
            <nz-table 
              #apartmentsTable 
              [nzData]="apartments"
              [nzPageSize]="pageSize"
              [nzShowSizeChanger]="true"
              [nzShowQuickJumper]="true"
              [nzShowTotal]="totalTemplate"
              [nzPageIndex]="pageIndex"
              (nzPageIndexChange)="onPageChange($event)"
              (nzPageSizeChange)="onPageSizeChange($event)">
              
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Mã căn hộ</th>
                  <th>Dự án</th>
                  <th>Loại căn hộ</th>
                  <th>Tầng</th>
                  <th>Diện tích (m²)</th>
                  <th>Phòng ngủ</th>
                  <th>Phòng tắm</th>
                  <th>Giá thuê (VNĐ/tháng)</th>
                  <th>Trạng thái</th>
                  <th>Số điện thoại</th>
                </tr>
              </thead>
              <tbody>
                <tr *ngFor="let apartment of apartmentsTable.data">
                  <td>{{ apartment.id }}</td>
                  <td>
                    <div class="font-medium">{{ apartment.unit_code || '-' }}</div>
                    <div class="text-sm text-gray-500">{{ apartment.unit_axis || '-' }}</div>
                  </td>
                  <td>{{ apartment.property_group_name || '-' }}</td>
                  <td>{{ apartment.unit_type_name || '-' }}</td>
                  <td>{{ apartment.unit_floor_number || '-' }}</td>
                  <td>
                    <div *ngIf="apartment.area_net">Net: {{ apartment.area_net }}</div>
                    <div *ngIf="apartment.area_gross" class="text-sm text-gray-500">Gross: {{ apartment.area_gross }}</div>
                  </td>
                  <td>{{ apartment.num_bedrooms || '-' }}</td>
                  <td>{{ apartment.num_bathrooms || '-' }}</td>
                  <td>
                    <div *ngIf="apartment.price_rent" class="font-medium text-blue-600">
                      {{ formatPrice(apartment.price_rent) }}
                    </div>
                    <div *ngIf="!apartment.price_rent" class="text-gray-400">-</div>
                  </td>
                  <td>
                    <nz-tag [nzColor]="getStatusColor(apartment.status)">
                      {{ apartment.status || '-' }}
                    </nz-tag>
                  </td>
                  <td>{{ apartment.phone_number || '-' }}</td>
                </tr>
              </tbody>
            </nz-table>
            
            <ng-template #totalTemplate let-total>
              Tổng {{ total }} căn hộ
            </ng-template>
          </nz-spin>
        </div>
      </div>
    </div>
  `,
  styles: [`
    :host ::ng-deep .ant-table {
      border-radius: 8px;
      overflow: hidden;
    }
    
    :host ::ng-deep .ant-table-thead > tr > th {
      background: #fafafa;
      font-weight: 600;
    }
  `]
})
export class CanHoChungCuChoThueComponent implements OnInit, OnDestroy {
  apartments: Apartment[] = [];
  loading = false;
  pageIndex = 1;
  pageSize = 10;
  total = 0;
  
  filters = {
    duAn: null as number | null,
    giaTu: null as number | null,
    giaDen: null as number | null,
    dienTichTu: null as number | null,
    dienTichToi: null as number | null
  };
  
  private destroy$ = new Subject<void>();

  constructor(
    private warehouseService: WarehouseService,
    private route: ActivatedRoute,
    private router: Router
  ) {}

  ngOnInit() {
    // Đọc path từ URL lần đầu
    this.parsePathParams();
    this.loadApartments();
    
    // Subscribe để theo dõi thay đổi route
    this.route.url
      .pipe(takeUntil(this.destroy$))
      .subscribe(() => {
        this.parsePathParams();
        this.loadApartments();
      });
  }

  ngOnDestroy() {
    this.destroy$.next();
    this.destroy$.complete();
  }

  parsePathParams() {
    // Reset filters
    this.filters = {
      duAn: null,
      giaTu: null,
      giaDen: null,
      dienTichTu: null,
      dienTichToi: null
    };

    // Lấy path từ URL
    if (typeof window !== 'undefined') {
      const url = window.location.pathname;
      // URL format: /can-ho-chung-cu-cho-thue,du-an-32,dien-tich-tu-20m,dien-tich-toi-50m
      
      // Tìm phần chứa 'can-ho-chung-cu-cho-thue'
      const pathSegment = url.split('/').find(part => part.includes('can-ho-chung-cu-cho-thue'));
      
      if (pathSegment) {
        // Split bằng dấu phẩy để lấy các filter
        const parts = pathSegment.split(',');
        
        parts.forEach(part => {
          const trimmedPart = part.trim();
          
          // Parse du-an-32
          if (trimmedPart.startsWith('du-an-')) {
            const value = trimmedPart.replace('du-an-', '');
            const duAn = parseInt(value, 10);
            this.filters.duAn = isNaN(duAn) ? null : duAn;
          }
          
          // Parse gia-tu-1
          if (trimmedPart.startsWith('gia-tu-')) {
            const value = trimmedPart.replace('gia-tu-', '');
            const giaTu = parseFloat(value);
            this.filters.giaTu = isNaN(giaTu) ? null : giaTu;
          }
          
          // Parse gia-den-2
          if (trimmedPart.startsWith('gia-den-')) {
            const value = trimmedPart.replace('gia-den-', '');
            const giaDen = parseFloat(value);
            this.filters.giaDen = isNaN(giaDen) ? null : giaDen;
          }
          
          // Parse dien-tich-tu-40m
          if (trimmedPart.startsWith('dien-tich-tu-')) {
            const value = trimmedPart.replace('dien-tich-tu-', '').replace(/[^0-9.]/g, '');
            const dienTichTu = parseFloat(value);
            this.filters.dienTichTu = isNaN(dienTichTu) ? null : dienTichTu;
          }
          
          // Parse dien-tich-toi-80m
          if (trimmedPart.startsWith('dien-tich-toi-')) {
            const value = trimmedPart.replace('dien-tich-toi-', '').replace(/[^0-9.]/g, '');
            const dienTichToi = parseFloat(value);
            this.filters.dienTichToi = isNaN(dienTichToi) ? null : dienTichToi;
          }
        });
      }
    }
  }

  applyFilters() {
    // Tạo path với format: can-ho-chung-cu-cho-thue,du-an-32,dien-tich-tu-20m,dien-tich-toi-50m
    const pathParts: string[] = ['can-ho-chung-cu-cho-thue'];
    
    if (this.filters.duAn) {
      pathParts.push(`du-an-${this.filters.duAn}`);
    }
    if (this.filters.giaTu) {
      pathParts.push(`gia-tu-${this.filters.giaTu}`);
    }
    if (this.filters.giaDen) {
      pathParts.push(`gia-den-${this.filters.giaDen}`);
    }
    if (this.filters.dienTichTu) {
      pathParts.push(`dien-tich-tu-${this.filters.dienTichTu}m`);
    }
    if (this.filters.dienTichToi) {
      pathParts.push(`dien-tich-toi-${this.filters.dienTichToi}m`);
    }

    // Reset về trang 1 khi filter thay đổi
    this.pageIndex = 1;
    
    // Navigate với path mới
    const path = '/' + pathParts.join(',');
    this.router.navigateByUrl(path, { replaceUrl: true });
  }

  resetFilters() {
    this.filters = {
      duAn: null,
      giaTu: null,
      giaDen: null,
      dienTichTu: null,
      dienTichToi: null
    };
    this.pageIndex = 1;
    this.router.navigateByUrl('/can-ho-chung-cu-cho-thue', { replaceUrl: true });
  }

  loadApartments() {
    this.loading = true;
    const offset = (this.pageIndex - 1) * this.pageSize;
    
    const params: any = {
      limit: this.pageSize,
      offset: offset,
      listing_type: 'CAN_CHO_THUE'
    };

    if (this.filters.duAn) {
      params.property_group_id = this.filters.duAn;
    }
    if (this.filters.giaTu) {
      params.price_from = this.filters.giaTu;
    }
    if (this.filters.giaDen) {
      params.price_to = this.filters.giaDen;
    }
    if (this.filters.dienTichTu) {
      params.area_from = this.filters.dienTichTu;
    }
    if (this.filters.dienTichToi) {
      params.area_to = this.filters.dienTichToi;
    }
    
    this.warehouseService.getApartmentsList(params).subscribe({
      next: (response) => {
        if (response.success) {
          this.apartments = response.data;
          this.total = response.total;
        }
        this.loading = false;
      },
      error: (error) => {
        console.error('Error loading apartments:', error);
        this.loading = false;
      }
    });
  }

  onPageChange(page: number) {
    this.pageIndex = page;
    this.loadApartments();
  }

  onPageSizeChange(size: number) {
    this.pageSize = size;
    this.pageIndex = 1;
    this.loadApartments();
  }

  formatPrice(price: number): string {
    if (!price) return '-';
    return new Intl.NumberFormat('vi-VN').format(price);
  }

  formatPriceInput = (value: number): string => {
    if (!value) return '';
    return new Intl.NumberFormat('vi-VN').format(value);
  }

  parsePriceInput = (value: string): number => {
    if (!value) return 0;
    return parseFloat(value.replace(/[^0-9.]/g, '')) || 0;
  }

  getStatusColor(status: string): string {
    if (!status) return 'default';
    const statusUpper = status.toUpperCase();
    if (statusUpper.includes('AVAILABLE') || statusUpper.includes('SẴN')) {
      return 'green';
    } else if (statusUpper.includes('RENTED') || statusUpper.includes('ĐÃ THUÊ')) {
      return 'red';
    } else if (statusUpper.includes('RESERVED') || statusUpper.includes('ĐẶT CỌC')) {
      return 'orange';
    }
    return 'default';
  }
}

