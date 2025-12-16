export const APARTMENT_LISTING_TEMPLATE = `
  <div class="p-6">
    <div class="bg-white p-6 rounded-lg shadow-sm">
      <div class="space-y-6">
        <div class="flex items-center justify-between">
          <h1 class="text-2xl font-semibold text-gray-800">{{ title }}</h1>
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
`;

