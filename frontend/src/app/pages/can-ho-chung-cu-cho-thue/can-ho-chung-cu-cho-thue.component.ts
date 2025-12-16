import { Component } from '@angular/core';
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
import { NzSliderModule } from 'ng-zorro-antd/slider';
import { NzIconModule } from 'ng-zorro-antd/icon';
import { FormsModule } from '@angular/forms';
import { WarehouseService } from '../../services/warehouse.service';
import { ApartmentListingBaseComponent, ApartmentListingConfig } from '../shared/apartment-listing-base.component';
import { CustomDropdownComponent } from '../shared/custom-dropdown.component';
import { DanhSachDuAnComponent } from '../shared/danh-sach-du-an/danh-sach-du-an.component';

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
    NzGridModule,
    NzSliderModule,
    NzIconModule,
    CustomDropdownComponent,
    DanhSachDuAnComponent
  ],
  template: `
  <div class="p-6">
    <div class="bg-white p-6 rounded-lg shadow-sm">
      <div class="space-y-6">
        <div class="flex items-center justify-between">
          <h1 class="text-2xl font-semibold text-gray-800">{{ title }}</h1>
        </div>
        
        <!-- Danh sách dự án -->
        <nz-card nzTitle="Danh sách dự án" [nzBordered]="false" class="mb-4">
          <app-danh-sach-du-an 
            [routePath]="config.routePath" 
            [propertyGroupSlug]="filters.duAnSlug || undefined">
          </app-danh-sach-du-an>
        </nz-card>
        
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
                <label class="block text-sm font-medium mb-2">Khoảng giá</label>
                <app-custom-dropdown [placement]="'bottomLeft'">
                  <button nz-button nzType="default" class="w-full text-left" trigger>
                    <span *ngIf="!filters.giaTu && !filters.giaDen">Chọn khoảng giá</span>
                    <span *ngIf="filters.giaTu || filters.giaDen">
                      {{ filters.giaTu ? formatPriceLabel(filters.giaTu / 1000000) : formatPriceLabel(priceRangeMin) }} - 
                      {{ filters.giaDen ? formatPriceLabel(filters.giaDen / 1000000) : formatPriceLabel(priceRangeMax) }}
                    </span>
                    <span nz-icon nzType="down" class="float-right mt-1"></span>
                  </button>
                  <div menu class="p-4" style="width: 320px;">
                    <div class="mb-4">
                      <div class="flex justify-between mb-2 text-sm font-medium text-gray-700">
                        <span>{{ formatPriceLabel((filters.giaTu || priceRangeMin * 1000000) / 1000000) }}</span>
                        <span>{{ formatPriceLabel((filters.giaDen || priceRangeMax * 1000000) / 1000000) }}</span>
                      </div>
                      <nz-slider
                        nzRange
                        [nzMin]="priceRangeMin"
                        [nzMax]="priceRangeMax"
                        [nzStep]="priceRangeStep"
                        [(ngModel)]="priceRange"
                        (ngModelChange)="onPriceRangeChange($event)"
                        name="priceRange">
                      </nz-slider>
                    </div>
                  </div>
                </app-custom-dropdown>
              </div>
              <div>
                <label class="block text-sm font-medium mb-2">Diện tích</label>
                <app-custom-dropdown [placement]="'bottomLeft'">
                  <button nz-button nzType="default" class="w-full text-left" trigger>
                    <span *ngIf="!filters.dienTichTu && !filters.dienTichToi">Chọn diện tích</span>
                    <span *ngIf="filters.dienTichTu || filters.dienTichToi">
                      {{ filters.dienTichTu || areaRangeMin }} m² - 
                      {{ filters.dienTichToi || areaRangeMax }} m²
                    </span>
                    <span nz-icon nzType="down" class="float-right mt-1"></span>
                  </button>
                  <div menu class="p-4" style="width: 320px;">
                    <div class="mb-4">
                      <div class="flex justify-between mb-2 text-sm font-medium text-gray-700">
                        <span>{{ filters.dienTichTu || areaRangeMin }} m²</span>
                        <span>{{ filters.dienTichToi || areaRangeMax }} m²</span>
                      </div>
                      <nz-slider
                        nzRange
                        [nzMin]="areaRangeMin"
                        [nzMax]="areaRangeMax"
                        [nzStep]="areaRangeStep"
                        [(ngModel)]="areaRange"
                        (ngModelChange)="onAreaRangeChange($event)"
                        name="areaRange">
                      </nz-slider>
                    </div>
                  </div>
                </app-custom-dropdown>
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
                <th>{{ priceColumnLabel }}</th>
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
                  <ng-container *ngIf="getPriceDisplay(apartment).main">
                    <div class="font-medium text-blue-600">
                      {{ formatPrice(getPriceDisplay(apartment).main!) }}
                    </div>
                    <div *ngIf="getPriceDisplay(apartment).early" class="text-sm text-gray-500">
                      Sớm: {{ formatPrice(getPriceDisplay(apartment).early!) }}
                    </div>
                  </ng-container>
                  <div *ngIf="!getPriceDisplay(apartment).main" class="text-gray-400">-</div>
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
          
          <!-- Statistics Section -->
          <div *ngIf="apartments && apartments.length > 0" class="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
            <h3 class="text-lg font-semibold text-gray-800 mb-3">Thống kê & Phân tích</h3>
            <p class="text-gray-700 leading-relaxed" [innerHTML]="getStatistics()"></p>
          </div>
          
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
export class CanHoChungCuChoThueComponent extends ApartmentListingBaseComponent {
  config: ApartmentListingConfig = {
    routePath: 'can-ho-chung-cu-cho-thue',
    title: 'Căn hộ chung cư cho thuê',
    listingType: 'CAN_CHO_THUE',
    priceField: 'price_rent'
  };

  get title(): string {
    return this.config.title;
  }

  get priceColumnLabel(): string {
    return 'Giá thuê (VNĐ/tháng)';
  }

  constructor(
    warehouseService: WarehouseService,
    route: ActivatedRoute,
    router: Router
  ) {
    super(warehouseService, route, router);
  }
}
