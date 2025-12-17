import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { NzTagModule } from 'ng-zorro-antd/tag';
import { NzSpinModule } from 'ng-zorro-antd/spin';

export interface ApartmentTableColumn {
  key: string;
  label: string;
  width?: string;
  sortable?: boolean;
}

export interface PaginationData {
  pageIndex: number;
  pageSize: number;
  total: number;
}

@Component({
  selector: 'app-apartment-table',
  standalone: true,
  imports: [CommonModule, NzTagModule, NzSpinModule],
  template: `
    <div class="w-full">
      <nz-spin [nzSpinning]="loading">
        <div class="overflow-x-auto rounded-lg border border-gray-200 shadow-sm">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th *ngFor="let column of columns"
                    [style.width]="column.width"
                    class="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                  {{ column.label }}
                </th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr *ngFor="let apartment of data"
                  class="hover:bg-gray-50 transition-colors duration-150">
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {{ apartment.id }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {{ apartment.property_group_name || '-' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {{ apartment.unit_type_name || '-' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {{ apartment.unit_floor_number || '-' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <div *ngIf="apartment.area_net" class="text-sm text-gray-900">{{ apartment.area_net }} m²</div>
                  <div *ngIf="apartment.area_gross" class="text-sm text-gray-900">{{ apartment.area_gross }} m²</div>
                  <div *ngIf="!apartment.area_net && !apartment.area_gross" class="text-sm text-gray-400">-</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {{ apartment.num_bedrooms || '-' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {{ apartment.num_bathrooms || '-' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <ng-container *ngIf="getPriceDisplay(apartment).main">
                    <div class="text-sm font-medium text-blue-600">
                      {{ formatPrice(getPriceDisplay(apartment).main!) }}
                    </div>
                    <div *ngIf="getPriceDisplay(apartment).early" class="text-xs text-gray-500">
                      Sớm: {{ formatPrice(getPriceDisplay(apartment).early!) }}
                    </div>
                  </ng-container>
                  <div *ngIf="!getPriceDisplay(apartment).main" class="text-sm text-gray-400">-</div>
                </td>
              </tr>

              <!-- Empty state -->
              <tr *ngIf="!data || data.length === 0">
                <td [attr.colspan]="columns.length" class="px-6 py-12 text-center">
                  <div class="text-gray-400">
                    <svg class="mx-auto h-12 w-12 text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
                    </svg>
                    <p class="mt-2 text-sm font-medium">Không có dữ liệu</p>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Pagination -->
        <div *ngIf="pagination && data && data.length > 0"
             class="mt-4 flex items-center justify-between px-4 py-3 bg-white rounded-lg border border-gray-200">
          <div class="flex items-center gap-4">
            <span class="text-sm text-gray-700">
              Tổng <span class="font-medium">{{ pagination.total }}</span> căn hộ
            </span>

            <div class="flex items-center gap-2">
              <label class="text-sm text-gray-700">Hiển thị:</label>
              <select
                [value]="pagination.pageSize"
                (change)="onPageSizeChange($event)"
                class="rounded-md border-gray-300 text-sm focus:border-blue-500 focus:ring-blue-500">
                <option [value]="10">10</option>
                <option [value]="20">20</option>
                <option [value]="50">50</option>
                <option [value]="100">100</option>
              </select>
            </div>
          </div>

          <div class="flex items-center gap-2">
            <button
              (click)="onPageChange(pagination.pageIndex - 1)"
              [disabled]="pagination.pageIndex === 1"
              class="px-3 py-1 text-sm font-medium rounded-md border border-gray-300 bg-white text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors">
              Trước
            </button>

            <div class="flex items-center gap-1">
              <ng-container *ngFor="let page of getPageNumbers()">
                <button
                  *ngIf="page !== '...'"
                  (click)="onPageChange(+page)"
                  [class.bg-blue-600]="page === pagination.pageIndex"
                  [class.text-white]="page === pagination.pageIndex"
                  [class.bg-white]="page !== pagination.pageIndex"
                  [class.text-gray-700]="page !== pagination.pageIndex"
                  class="px-3 py-1 text-sm font-medium rounded-md border border-gray-300 hover:bg-gray-50 transition-colors">
                  {{ page }}
                </button>
                <span *ngIf="page === '...'" class="px-2 text-gray-500">...</span>
              </ng-container>
            </div>

            <button
              (click)="onPageChange(pagination.pageIndex + 1)"
              [disabled]="pagination.pageIndex >= Math.ceil(pagination.total / pagination.pageSize)"
              class="px-3 py-1 text-sm font-medium rounded-md border border-gray-300 bg-white text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors">
              Sau
            </button>
          </div>
        </div>
      </nz-spin>
    </div>
  `,
  styles: [`
    :host {
      display: block;
      width: 100%;
    }
  `]
})
export class ApartmentTableComponent {
  @Input() data: any[] = [];
  @Input() columns: ApartmentTableColumn[] = [];
  @Input() loading = false;
  @Input() pagination?: PaginationData;
  @Input() priceField: 'price' | 'price_rent' = 'price';

  @Output() pageChange = new EventEmitter<number>();
  @Output() pageSizeChange = new EventEmitter<number>();

  Math = Math;

  getPriceDisplay(apartment: any): { main?: number, early?: number } {
    if (this.priceField === 'price') {
      return {
        main: apartment.price,
        early: apartment.price_early
      };
    } else {
      return {
        main: apartment.price_rent,
        early: apartment.price_rent_early
      };
    }
  }

  formatPrice(price: number): string {
    if (!price) return '-';

    if (price >= 1000000000) {
      return `${(price / 1000000000).toFixed(2)} tỷ`;
    } else if (price >= 1000000) {
      return `${(price / 1000000).toFixed(2)} triệu`;
    } else if (price >= 1000) {
      return `${(price / 1000).toFixed(2)}K`;
    }
    return price.toString();
  }

  getStatusColor(status: string): string {
    const statusColors: { [key: string]: string } = {
      'Còn trống': 'green',
      'Đã bán': 'red',
      'Đã đặt cọc': 'orange',
      'Đang bán': 'blue',
      'Không bán': 'default',
      'Cho thuê': 'cyan',
      'Đã cho thuê': 'purple'
    };
    return statusColors[status] || 'default';
  }

  onPageChange(page: number): void {
    if (!this.pagination) return;
    const maxPage = Math.ceil(this.pagination.total / this.pagination.pageSize);
    if (page >= 1 && page <= maxPage) {
      this.pageChange.emit(page);
    }
  }

  onPageSizeChange(event: Event): void {
    const target = event.target as HTMLSelectElement;
    this.pageSizeChange.emit(+target.value);
  }

  getPageNumbers(): (number | string)[] {
    if (!this.pagination) return [];

    const current = this.pagination.pageIndex;
    const total = Math.ceil(this.pagination.total / this.pagination.pageSize);
    const pages: (number | string)[] = [];

    if (total <= 7) {
      for (let i = 1; i <= total; i++) {
        pages.push(i);
      }
    } else {
      if (current <= 4) {
        for (let i = 1; i <= 5; i++) {
          pages.push(i);
        }
        pages.push('...');
        pages.push(total);
      } else if (current >= total - 3) {
        pages.push(1);
        pages.push('...');
        for (let i = total - 4; i <= total; i++) {
          pages.push(i);
        }
      } else {
        pages.push(1);
        pages.push('...');
        for (let i = current - 1; i <= current + 1; i++) {
          pages.push(i);
        }
        pages.push('...');
        pages.push(total);
      }
    }

    return pages;
  }
}
