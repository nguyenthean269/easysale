import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { NzFormModule } from 'ng-zorro-antd/form';
import { NzButtonModule } from 'ng-zorro-antd/button';
import { NzSliderModule } from 'ng-zorro-antd/slider';
import { NzIconModule } from 'ng-zorro-antd/icon';
import { CustomDropdownComponent } from '../../pages/shared/custom-dropdown.component';
import { SearchableSelectComponent } from '../searchable-select/searchable-select.component';
import { UnitType } from '../../services/warehouse.service';
import { ApartmentFilters } from '../../pages/shared/apartment-listing-base.component';

@Component({
  selector: 'app-apartment-filter-form',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    NzFormModule,
    NzButtonModule,
    NzSliderModule,
    NzIconModule,
    CustomDropdownComponent,
    SearchableSelectComponent
  ],
  template: `
    <div class="filter-wrapper">
      <div>

        <form nz-form class="filter-form">
          <div class="filter-grid">
            <!-- Loại căn hộ -->
            <app-searchable-select
              [(ngModel)]="filters.loaiCanHo"
              (ngModelChange)="onUnitTypeChange($event)"
              name="loaiCanHo"
              [options]="unitTypes"
              placeholder="Chọn loại căn hộ"
              [allowClear]="true">
            </app-searchable-select>

            <!-- Khoảng giá -->
            <app-custom-dropdown [placement]="'bottomLeft'">
              <button nz-button nzType="default" class="modern-dropdown-btn" trigger>
                <span class="btn-value" *ngIf="!filters.giaTu && !filters.giaDen">Khoảng giá</span>
                <span class="btn-value" *ngIf="filters.giaTu || filters.giaDen">
                  {{ filters.giaTu ? formatPriceLabel(filters.giaTu / 1000000) : formatPriceLabel(priceRangeMin) }} -
                  {{ filters.giaDen ? formatPriceLabel(filters.giaDen / 1000000) : formatPriceLabel(priceRangeMax) }}
                </span>
                <span nz-icon nzType="down" class="btn-arrow"></span>
              </button>
              <div menu class="dropdown-menu">
                <div class="slider-wrapper">
                  <div class="slider-header">
                    <span class="slider-value">{{ formatPriceLabel((filters.giaTu || priceRangeMin * 1000000) / 1000000) }}</span>
                    <span class="slider-separator">-</span>
                    <span class="slider-value">{{ formatPriceLabel((filters.giaDen || priceRangeMax * 1000000) / 1000000) }}</span>
                  </div>
                  <nz-slider
                    nzRange
                    [nzMin]="priceRangeMin"
                    [nzMax]="priceRangeMax"
                    [nzStep]="priceRangeStep"
                    [(ngModel)]="priceRange"
                    (ngModelChange)="onPriceRangeChange($event)"
                    name="priceRange"
                    class="modern-slider">
                  </nz-slider>
                </div>
              </div>
            </app-custom-dropdown>

            <!-- Diện tích -->
            <app-custom-dropdown [placement]="'bottomLeft'">
              <button nz-button nzType="default" class="modern-dropdown-btn" trigger>
                <span class="btn-value" *ngIf="!filters.dienTichTu && !filters.dienTichToi">Diện tích</span>
                <span class="btn-value" *ngIf="filters.dienTichTu || filters.dienTichToi">
                  {{ filters.dienTichTu || areaRangeMin }}m² - {{ filters.dienTichToi || areaRangeMax }}m²
                </span>
                <span nz-icon nzType="down" class="btn-arrow"></span>
              </button>
              <div menu class="dropdown-menu">
                <div class="slider-wrapper">
                  <div class="slider-header">
                    <span class="slider-value">{{ filters.dienTichTu || areaRangeMin }}m²</span>
                    <span class="slider-separator">-</span>
                    <span class="slider-value">{{ filters.dienTichToi || areaRangeMax }}m²</span>
                  </div>
                  <nz-slider
                    nzRange
                    [nzMin]="areaRangeMin"
                    [nzMax]="areaRangeMax"
                    [nzStep]="areaRangeStep"
                    [(ngModel)]="areaRange"
                    (ngModelChange)="onAreaRangeChange($event)"
                    name="areaRange"
                    class="modern-slider">
                  </nz-slider>
                </div>
              </div>
            </app-custom-dropdown>

            <!-- Actions -->
            <div class="filter-actions">
              <button nz-button class="modern-reset-btn" (click)="onResetFilters()">
                <span nz-icon nzType="reload"></span>
              </button>
              <button nz-button class="modern-apply-btn" (click)="onApplyFilters()">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-search"><path d="m21 21-4.34-4.34"/><circle cx="11" cy="11" r="8"/></svg>
                <span>Tìm kiếm</span>
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  `,
  styles: [`
    .filter-wrapper {
      margin-bottom: 20px;
    }

    .filter-form {
      width: 100%;
    }

    .filter-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 12px;
      align-items: center;
    }

    .filter-actions {
      display: flex;
      gap: 8px;
    }

    /* Dropdown Button Styles */
    :host ::ng-deep .modern-dropdown-btn {
      width: 100%;
      height: 40px;
      background: #fafafa !important;
      border: 1px solid #d9d9d9 !important;
      border-radius: 8px !important;
      display: flex !important;
      align-items: center !important;
      justify-content: space-between !important;
      padding: 0 12px !important;
      transition: all 0.3s ease !important;
      color: #333 !important;
      font-size: 14px !important;
    }

    :host ::ng-deep .modern-dropdown-btn:hover {
      border-color: #008000 !important;
      background: white !important;
    }

    :host ::ng-deep .modern-dropdown-btn .btn-value {
      flex: 1;
      text-align: left;
      font-weight: 400;
    }

    :host ::ng-deep .modern-dropdown-btn .btn-arrow {
      color: #999;
      font-size: 12px;
      transition: transform 0.3s ease;
    }

    :host ::ng-deep .modern-dropdown-btn:hover .btn-arrow {
      color: #008000;
    }

    /* Dropdown Menu */
    :host ::ng-deep .dropdown-menu {
      background: white;
      border-radius: 12px;
      padding: 20px;
      box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
      min-width: 320px;
      border: 1px solid #e8e8e8;
    }

    .slider-wrapper {
      width: 100%;
    }

    .slider-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 16px;
      padding: 10px 12px;
      background: #f5f5f5;
      border-radius: 6px;
    }

    .slider-value {
      color: #008000;
      font-size: 14px;
      font-weight: 600;
    }

    .slider-separator {
      color: #999;
      font-weight: 300;
    }

    /* Slider Styles */
    :host ::ng-deep .modern-slider {
      margin: 0 8px;
    }

    :host ::ng-deep .modern-slider .ant-slider-rail {
      background: #e8e8e8 !important;
      height: 4px !important;
      border-radius: 2px !important;
    }

    :host ::ng-deep .modern-slider .ant-slider-track {
      background: #008000 !important;
      height: 4px !important;
      border-radius: 2px !important;
    }

    :host ::ng-deep .modern-slider .ant-slider-handle {
      border: 3px solid #008000 !important;
      background: white !important;
      width: 16px !important;
      height: 16px !important;
      margin-top: -6px !important;
      box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15) !important;
    }

    :host ::ng-deep .modern-slider .ant-slider-handle:hover,
    :host ::ng-deep .modern-slider .ant-slider-handle:focus {
      border-color: #00a000 !important;
      box-shadow: 0 2px 8px rgba(0, 128, 0, 0.3) !important;
    }

    /* Button Styles */
    :host ::ng-deep .modern-reset-btn {
      height: 40px;
      width: 40px;
      min-width: 40px;
      padding: 0;
      background: white !important;
      border: 1px solid #d9d9d9 !important;
      border-radius: 8px !important;
      color: #666 !important;
      font-size: 16px !important;
      display: flex !important;
      align-items: center !important;
      justify-content: center !important;
      transition: all 0.3s ease !important;
    }

    :host ::ng-deep .modern-reset-btn:hover {
      color: #008000 !important;
      border-color: #008000 !important;
    }

    :host ::ng-deep .modern-apply-btn {
      flex: 1;
      height: 40px;
      background: #008000 !important;
      border: 1px solid #008000 !important;
      border-radius: 8px !important;
      color: white !important;
      font-weight: 600 !important;
      font-size: 14px !important;
      display: flex !important;
      align-items: center !important;
      justify-content: center !important;
      gap: 6px !important;
      transition: all 0.3s ease !important;
    }

    :host ::ng-deep .modern-apply-btn:hover {
      background: #00a000 !important;
      border-color: #00a000 !important;
    }

    :host ::ng-deep .modern-apply-btn svg {
      width: 16px;
      height: 16px;
    }

    /* Responsive */
    @media (max-width: 1024px) {
      .filter-grid {
        grid-template-columns: repeat(2, 1fr);
      }

      .filter-actions {
        grid-column: 1 / -1;
      }
    }

    @media (max-width: 768px) {
      .filter-grid {
        grid-template-columns: 1fr;
        gap: 10px;
      }

      .filter-wrapper {
        margin-bottom: 16px;
      }
    }
  `]
})
export class ApartmentFilterFormComponent {
  @Input() unitTypes: UnitType[] = [];
  @Input() filters!: ApartmentFilters;
  @Input() priceRangeMin: number = 500;
  @Input() priceRangeMax: number = 500000;
  @Input() priceRangeStep: number = 500;
  @Input() areaRangeMin: number = 30;
  @Input() areaRangeMax: number = 200;
  @Input() areaRangeStep: number = 5;

  @Output() unitTypeChange = new EventEmitter<number | null>();
  @Output() applyFilters = new EventEmitter<void>();
  @Output() resetFilters = new EventEmitter<void>();

  // Internal state for range sliders
  priceRange: number[] = [500, 500000];
  areaRange: number[] = [30, 200];

  ngOnInit() {
    // Initialize ranges from filters
    this.priceRange = [
      this.filters.giaTu ? this.filters.giaTu / 1000000 : this.priceRangeMin,
      this.filters.giaDen ? this.filters.giaDen / 1000000 : this.priceRangeMax
    ];

    this.areaRange = [
      this.filters.dienTichTu || this.areaRangeMin,
      this.filters.dienTichToi || this.areaRangeMax
    ];
  }

  ngOnChanges() {
    // Update ranges when filters change externally
    if (this.filters) {
      this.priceRange = [
        this.filters.giaTu ? this.filters.giaTu / 1000000 : this.priceRangeMin,
        this.filters.giaDen ? this.filters.giaDen / 1000000 : this.priceRangeMax
      ];

      this.areaRange = [
        this.filters.dienTichTu || this.areaRangeMin,
        this.filters.dienTichToi || this.areaRangeMax
      ];
    }
  }

  onUnitTypeChange(unitTypeId: number | null) {
    this.unitTypeChange.emit(unitTypeId);
  }

  onPriceRangeChange(range: number[]) {
    // Convert from millions to VND
    this.filters.giaTu = range[0] * 1000000;
    this.filters.giaDen = range[1] * 1000000;
  }

  onAreaRangeChange(range: number[]) {
    this.filters.dienTichTu = range[0];
    this.filters.dienTichToi = range[1];
  }

  onApplyFilters() {
    this.applyFilters.emit();
  }

  onResetFilters() {
    this.resetFilters.emit();
  }

  formatPriceLabel(value: number): string {
    if (value >= 1000) {
      const billions = value / 1000;
      return billions % 1 === 0 ? `${billions} tỷ` : `${billions.toFixed(1)} tỷ`;
    }
    return `${value} triệu`;
  }
}
