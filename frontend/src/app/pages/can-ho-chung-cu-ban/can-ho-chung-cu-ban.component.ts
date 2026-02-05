import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { Title, Meta } from '@angular/platform-browser';
import { takeUntil } from 'rxjs';
import { FormsModule } from '@angular/forms';
import { WarehouseService, UnitType } from '../../services/warehouse.service';
import { ApartmentListingBaseComponent, ApartmentListingConfig } from '../shared/apartment-listing-base.component';
import { DanhSachDuAnComponent } from '../shared/danh-sach-du-an/danh-sach-du-an.component';
import { ApartmentTableComponent, ApartmentTableColumn } from '../../components/apartment-table/apartment-table.component';
import { BreadcrumbService } from '../../services/breadcrumb.service';
import { ApartmentFilterFormComponent } from '../../components/apartment-filter-form/apartment-filter-form.component';

@Component({
  selector: 'app-can-ho-chung-cu-ban',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    FormsModule,
    DanhSachDuAnComponent,
    ApartmentTableComponent,
    ApartmentFilterFormComponent
  ],
  template: `
  <div class="content-wrapper">
      <div class="space-y-6">
        <div class="flex items-center justify-between">
          <h1 class="text-2xl font-semibold text-gray-800">{{ pageTitle }}</h1>
        </div>

        <!-- Filter Form -->
        <app-apartment-filter-form
          [unitTypes]="unitTypes"
          [filters]="filters"
          [priceRangeMin]="priceRangeMin"
          [priceRangeMax]="priceRangeMax"
          [priceRangeStep]="priceRangeStep"
          [areaRangeMin]="areaRangeMin"
          [areaRangeMax]="areaRangeMax"
          [areaRangeStep]="areaRangeStep"
          (unitTypeChange)="onUnitTypeChange($event)"
          (applyFilters)="applyFilters()"
          (resetFilters)="resetFilters()">
        </app-apartment-filter-form>
        
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
        <div class="card mb-4">
          <h3 class="card-title">Danh sách dự án</h3>
          <app-danh-sach-du-an
            [routePath]="config.routePath"
            [propertyGroupSlug]="filters.duAnSlug || undefined">
          </app-danh-sach-du-an>
        </div>

        <!-- Statistics Section -->
        <div *ngIf="apartments && apartments.length > 0" class="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
          <h3 class="text-lg font-semibold text-gray-800 mb-3">Thống kê & Phân tích</h3>
          <p class="text-gray-700 leading-relaxed" [innerHTML]="getStatistics()"></p>
        </div>
      </div>
  </div>
  `,
  styles: [`
    .content-wrapper {
      width: 100%;
    }

    .space-y-6 > * + * {
      margin-top: 1.5rem;
    }

    .card {
      background: #ffffff;
      border-radius: 8px;
      padding: 24px;
      border: 1px solid #e5e7eb;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }

    .card-title {
      font-size: 16px;
      font-weight: 600;
      color: #111827;
      margin: 0 0 16px 0;
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
    if (unitTypeId != null) {
      const selectedType = this.unitTypes.find(t => t.id === unitTypeId);
      if (selectedType) {
        // Dùng slug nếu có, không thì dùng id-{id} để URL vẫn lưu được và parse lại
        this.filters.loaiCanHoSlug = selectedType.slug ?? `id-${unitTypeId}`;
      } else {
        this.filters.loaiCanHoSlug = `id-${unitTypeId}`;
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

