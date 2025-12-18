import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { NzSpinModule } from 'ng-zorro-antd/spin';
import { NzCardModule } from 'ng-zorro-antd/card';
import { NzFormModule } from 'ng-zorro-antd/form';
import { NzInputModule } from 'ng-zorro-antd/input';
import { NzButtonModule } from 'ng-zorro-antd/button';
import { NzGridModule } from 'ng-zorro-antd/grid';
import { NzSliderModule } from 'ng-zorro-antd/slider';
import { NzIconModule } from 'ng-zorro-antd/icon';
import { FormsModule } from '@angular/forms';
import { WarehouseService, UnitType } from '../../services/warehouse.service';
import { ApartmentListingBaseComponent, ApartmentListingConfig } from '../shared/apartment-listing-base.component';
import { CustomDropdownComponent } from '../shared/custom-dropdown.component';
import { DanhSachDuAnComponent } from '../shared/danh-sach-du-an/danh-sach-du-an.component';
import { ApartmentTableComponent, ApartmentTableColumn } from '../../components/apartment-table/apartment-table.component';
import { NzSelectModule } from 'ng-zorro-antd/select';
import { BreadcrumbService } from '../../services/breadcrumb.service';

@Component({
  selector: 'app-can-ho-chung-cu-ban',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    FormsModule,
    NzSpinModule,
    NzCardModule,
    NzFormModule,
    NzInputModule,
    NzButtonModule,
    NzGridModule,
    NzSliderModule,
    NzIconModule,
    NzSelectModule,
    CustomDropdownComponent,
    DanhSachDuAnComponent,
    ApartmentTableComponent
  ],
  template: `
  <div class="p-6">
    <div class="bg-white p-6 rounded-lg shadow-sm">
      <div class="space-y-6">
        <div class="flex items-center justify-between">
          <h1 class="text-2xl font-semibold text-gray-800">{{ title }}</h1>
        </div>

        <!-- Filter Form -->
        <nz-card nzTitle="Bộ lọc" [nzBordered]="false" class="mb-4">
          <form nz-form [nzLayout]="'inline'" class="w-full">
            <div class="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
              <div>
                <nz-select
                  [(ngModel)]="filters.loaiCanHo"
                  (ngModelChange)="onUnitTypeChange($event)"
                  name="loaiCanHo"
                  nzPlaceHolder="Chọn loại căn hộ"
                  nzAllowClear
                  class="w-full">
                  <nz-option *ngFor="let type of unitTypes" [nzValue]="type.id" [nzLabel]="type.name"></nz-option>
                </nz-select>
              </div>
              <div>
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
              <div>
                <button nz-button nzType="default" (click)="resetFilters()" class="w-full">
                  Xóa bộ lọc
                </button>
              </div>
              <div>
                <button nz-button nzType="primary" (click)="applyFilters()" class="w-full">
                  Lọc
                </button>
              </div>
            </div>
          </form>
        </nz-card>
        
        <app-apartment-table
          [data]="apartments"
          [columns]="tableColumns"
          [loading]="loading"
          [pagination]="paginationData"
          [priceField]="config.priceField || 'price'"
          (pageChange)="onPageChange($event)"
          (pageSizeChange)="onPageSizeChange($event)">
        </app-apartment-table>

        <!-- Danh sách dự án -->
        <nz-card nzTitle="Danh sách dự án" [nzBordered]="false" class="mb-4">
          <app-danh-sach-du-an
            [routePath]="config.routePath"
            [propertyGroupSlug]="filters.duAnSlug || undefined">
          </app-danh-sach-du-an>
        </nz-card>

        <!-- Statistics Section -->
        <div *ngIf="apartments && apartments.length > 0" class="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
          <h3 class="text-lg font-semibold text-gray-800 mb-3">Thống kê & Phân tích</h3>
          <p class="text-gray-700 leading-relaxed" [innerHTML]="getStatistics()"></p>
        </div>
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
export class CanHoChungCuBanComponent extends ApartmentListingBaseComponent {
  config: ApartmentListingConfig = {
    routePath: 'can-ho-chung-cu-ban',
    title: 'Căn hộ chung cư bán',
    listingType: 'CAN_BAN',
    priceField: 'price'
  };

  tableColumns: ApartmentTableColumn[] = [
    { key: 'id', label: 'ID', width: '80px' },
    { key: 'property_group_name', label: 'Dự án', width: '200px' },
    { key: 'unit_type_name', label: 'Loại căn hộ', width: '150px' },
    { key: 'unit_floor_number', label: 'Tầng', width: '80px' },
    { key: 'area', label: 'Diện tích (m²)', width: '150px' },
    { key: 'num_bedrooms', label: 'Phòng ngủ', width: '100px' },
    { key: 'num_bathrooms', label: 'Phòng tắm', width: '100px' },
    { key: 'price', label: 'Giá bán (VNĐ)', width: '180px' }
  ];

  unitTypes: UnitType[] = [];

  // Override onRouteChange to handle slug-to-ID mapping before loading apartments
  protected override onRouteChange() {
    this.parsePathParams();
    this.mapUnitTypeSlugToId();
    this.loadApartments();
  }

  get title(): string {
    return this.config.title;
  }

  get priceColumnLabel(): string {
    return 'Giá bán (VNĐ)';
  }

  get paginationData() {
    return {
      pageIndex: this.pageIndex,
      pageSize: this.pageSize,
      total: this.total
    };
  }

  constructor(
    warehouseService: WarehouseService,
    route: ActivatedRoute,
    router: Router,
    breadcrumbService: BreadcrumbService
  ) {
    super(warehouseService, route, router, breadcrumbService);
    this.loadUnitTypes();
  }

  loadUnitTypes() {
    this.warehouseService.getUnitTypes().subscribe({
      next: (response) => {
        if (response.success) {
          this.unitTypes = response.data;
          // If we have a slug from URL, find the matching unit type ID
          if (this.filters.loaiCanHoSlug && !this.filters.loaiCanHo) {
            const matchedType = this.unitTypes.find(t => t.slug === this.filters.loaiCanHoSlug);
            if (matchedType) {
              this.filters.loaiCanHo = matchedType.id;
              // Reload apartments with the unit type ID
              this.loadApartments();
            }
          }
        }
      },
      error: (error) => {
        console.error('Error loading unit types:', error);
      }
    });
  }

  onUnitTypeChange(unitTypeId: number | null) {
    if (unitTypeId) {
      const selectedType = this.unitTypes.find(t => t.id === unitTypeId);
      if (selectedType && selectedType.slug) {
        this.filters.loaiCanHoSlug = selectedType.slug;
      }
    } else {
      this.filters.loaiCanHoSlug = null;
    }
  }

  mapUnitTypeSlugToId() {
    // If we have a slug and unit types are loaded, map slug to ID
    if (this.filters.loaiCanHoSlug && this.unitTypes.length > 0) {
      const matchedType = this.unitTypes.find(t => t.slug === this.filters.loaiCanHoSlug);
      if (matchedType) {
        this.filters.loaiCanHo = matchedType.id;
      }
    }
  }
}

