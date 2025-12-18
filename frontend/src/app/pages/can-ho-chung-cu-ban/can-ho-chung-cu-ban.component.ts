import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { Title, Meta } from '@angular/platform-browser';
import { takeUntil } from 'rxjs';
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
          <h1 class="text-2xl font-semibold text-gray-800">{{ pageTitle }}</h1>
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
    priceField: 'price',
    titleTemplates: {
      default: 'Căn hộ chung cư bán',
      withPropertyGroup: 'Căn hộ chung cư bán tại{propertyGroup}',
      withFilters: 'Căn hộ{unitType}{priceArea} bán',
      withFiltersAndPropertyGroup: 'Căn hộ{unitType} bán tại{propertyGroup}{priceArea}'
    },
    metaTitleTemplates: {
      default: 'Mua bán căn hộ chung cư giá tốt | EasySale',
      withPropertyGroup: 'Mua bán căn hộ chung cư tại{propertyGroup} | EasySale',
      withFilters: 'Căn hộ{unitType}{priceArea} bán | EasySale',
      withFiltersAndPropertyGroup: 'Căn hộ{unitType} bán tại{propertyGroup}{priceArea} | EasySale'
    },
    metaDescriptionTemplates: {
      default: 'Tìm kiếm và mua bán căn hộ chung cư với giá tốt nhất. Danh sách căn hộ đầy đủ thông tin, cập nhật liên tục.',
      withPropertyGroup: 'Mua bán căn hộ chung cư tại{propertyGroup}. Thông tin chi tiết, giá cả minh bạch, hỗ trợ tư vấn nhiệt tình.',
      withFilters: 'Tìm căn hộ{unitType}{priceArea} để mua. Danh sách căn hộ đầy đủ thông tin, giá tốt nhất thị trường.',
      withFiltersAndPropertyGroup: 'Mua căn hộ{unitType} tại{propertyGroup}{priceArea}. Thông tin chi tiết, giá cả minh bạch, hỗ trợ xem nhà và tư vấn.'
    }
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
  private unitTypesLoaded = false;
  private initialLoadPending = false;

  // Override onRouteChange to handle slug-to-ID mapping before loading apartments
  protected override onRouteChange() {
    this.parsePathParams();

    // If unit types are loaded, map slug to ID and load apartments
    if (this.unitTypesLoaded) {
      this.mapUnitTypeSlugToId();
      this.loadApartments();
    } else {
      // Mark that we need to load apartments once unit types are ready
      this.initialLoadPending = true;
    }
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
    breadcrumbService: BreadcrumbService,
    titleService: Title,
    metaService: Meta
  ) {
    super(warehouseService, route, router, breadcrumbService, titleService, metaService);
  }

  override ngOnInit() {
    // Initialize page title with config title
    this.pageTitle = this.config.title;

    // Initialize price range
    if (this.config.priceField === 'price_rent') {
      this.priceRangeThue = [5, 100];
    } else {
      this.priceRangeBan = [500, 500000];
    }

    // Initialize area range
    this.areaRange = [30, 200];

    // Parse path params first
    this.parsePathParams();

    // Load unit types first, then load apartments in the callback
    this.loadUnitTypes();

    // Subscribe to route changes
    this.route.url
      .pipe(takeUntil(this.destroy$))
      .subscribe(() => {
        this.onRouteChange();
      });
  }

  loadUnitTypes() {
    this.warehouseService.getUnitTypes().subscribe({
      next: (response) => {
        if (response.success) {
          this.unitTypes = response.data;
          this.unitTypesLoaded = true;

          // If we have a slug from URL, find the matching unit type ID
          if (this.filters.loaiCanHoSlug && !this.filters.loaiCanHo) {
            const matchedType = this.unitTypes.find(t => t.slug === this.filters.loaiCanHoSlug);
            if (matchedType) {
              this.filters.loaiCanHo = matchedType.id;
            }
          }

          // Always load apartments after unit types are loaded (for initial load)
          // or if there was a pending load from route change
          if (!this.initialLoadPending) {
            // This is the initial load from ngOnInit
            this.loadApartments();
          } else {
            // This was triggered by a route change
            this.initialLoadPending = false;
            this.loadApartments();
          }
        }
      },
      error: (error) => {
        console.error('Error loading unit types:', error);
        this.unitTypesLoaded = true;

        // Load apartments anyway even if unit types failed
        this.loadApartments();
        this.initialLoadPending = false;
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

