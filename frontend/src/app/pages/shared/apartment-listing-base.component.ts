import { Directive, OnInit, OnDestroy } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { Subject, takeUntil } from 'rxjs';
import { WarehouseService, Apartment } from '../../services/warehouse.service';

export interface ApartmentListingConfig {
  routePath: string;
  title: string;
  listingType: 'CAN_THUE' | 'CAN_CHO_THUE' | 'CAN_BAN' | 'CAN_MUA' | 'KHAC';
  priceField?: 'price' | 'price_rent'; // Field to use for price filtering
}

export interface ApartmentFilters {
  duAn: number | null;
  duAnSlug: string | null;
  giaTu: number | null;
  giaDen: number | null;
  dienTichTu: number | null;
  dienTichToi: number | null;
}

export interface ApartmentFiltersBan extends ApartmentFilters {
  // Giá bán thường cao hơn, tính bằng tỷ
}

export interface ApartmentFiltersThue extends ApartmentFilters {
  // Giá thuê thường thấp hơn, tính bằng triệu/tháng
}

@Directive()
export abstract class ApartmentListingBaseComponent implements OnInit, OnDestroy {
  apartments: Apartment[] = [];
  loading = false;
  pageIndex = 1;
  pageSize = 10;
  total = 0;

  // Filters cho bán (giá cao, tính bằng tỷ)
  filtersBan: ApartmentFiltersBan = {
    duAn: null,
    duAnSlug: null,
    giaTu: null,
    giaDen: null,
    dienTichTu: null,
    dienTichToi: null
  };

  // Filters cho thuê (giá thấp, tính bằng triệu/tháng)
  filtersThue: ApartmentFiltersThue = {
    duAn: null,
    duAnSlug: null,
    giaTu: null,
    giaDen: null,
    dienTichTu: null,
    dienTichToi: null
  };

  // Price range cho bán (tính bằng triệu, range lớn hơn)
  priceRangeBan: number[] = [500, 500000]; // 500 triệu đến 500 tỷ

  // Price range cho thuê (tính bằng triệu/tháng, range nhỏ hơn)
  priceRangeThue: number[] = [5, 100]; // 5 triệu đến 100 triệu/tháng

  // Area range (diện tích, không phân biệt bán/thuê, tính bằng m²)
  areaRange: number[] = [30, 200]; // 30 m² đến 200 m²

  // Getter để lấy đúng filter dựa trên loại listing
  get filters(): ApartmentFilters {
    return this.config.priceField === 'price_rent' ? this.filtersThue : this.filtersBan;
  }

  // Getter để lấy đúng price range
  get priceRange(): number[] {
    return this.config.priceField === 'price_rent' ? this.priceRangeThue : this.priceRangeBan;
  }

  set priceRange(value: number[]) {
    if (this.config.priceField === 'price_rent') {
      this.priceRangeThue = value;
    } else {
      this.priceRangeBan = value;
    }
  }

  // Getter cho min/max của slider dựa trên loại listing
  get priceRangeMin(): number {
    return this.config.priceField === 'price_rent' ? 1 : 500; // 1 triệu cho thuê, 500 triệu cho bán
  }

  get priceRangeMax(): number {
    return this.config.priceField === 'price_rent' ? 100 : 500000; // 100 triệu cho thuê, 500 tỷ cho bán
  }

  get priceRangeStep(): number {
    return this.config.priceField === 'price_rent' ? 1 : 500; // Step 1 triệu cho thuê, 500 triệu cho bán
  }

  protected destroy$ = new Subject<void>();

  abstract config: ApartmentListingConfig;

  constructor(
    protected warehouseService: WarehouseService,
    protected route: ActivatedRoute,
    protected router: Router
  ) { }

  ngOnInit() {
    // Khởi tạo price range dựa trên loại listing
    if (this.config.priceField === 'price_rent') {
      this.priceRangeThue = [5, 100]; // 5 triệu đến 100 triệu/tháng
    } else {
      this.priceRangeBan = [500, 500000]; // 500 triệu đến 500 tỷ
    }
    
    // Khởi tạo area range
    this.areaRange = [30, 200]; // 30 m² đến 200 m²
    
    this.parsePathParams();
    this.loadApartments();

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
    // Reset filters dựa trên loại listing
    const currentFilters = this.filters;
    currentFilters.duAn = null;
    currentFilters.duAnSlug = null;
    currentFilters.giaTu = null;
    currentFilters.giaDen = null;
    currentFilters.dienTichTu = null;
    currentFilters.dienTichToi = null;

    if (typeof window !== 'undefined') {
      const url = window.location.pathname;
      const pathSegment = url.split('/').find(part => part.includes(this.config.routePath));

      if (pathSegment) {
        const parts = pathSegment.split(',');

        parts.forEach(part => {
          const trimmedPart = part.trim();

          if (trimmedPart.startsWith('du-an-')) {
            const value = trimmedPart.replace('du-an-', '');
            // Try to parse as number (ID) first for backward compatibility
            const duAn = parseInt(value, 10);
            if (!isNaN(duAn) && value === duAn.toString()) {
              // It's a numeric ID
              currentFilters.duAn = duAn;
            } else {
              // It's a slug
              currentFilters.duAnSlug = value;
            }
          }

          if (trimmedPart.startsWith('gia-tu-')) {
            const slug = trimmedPart.replace('gia-tu-', '');
            const giaTu = this.parsePriceFromSlug(slug);
            currentFilters.giaTu = giaTu > 0 ? giaTu : null;
          }

          if (trimmedPart.startsWith('gia-den-')) {
            const slug = trimmedPart.replace('gia-den-', '');
            const giaDen = this.parsePriceFromSlug(slug);
            currentFilters.giaDen = giaDen > 0 ? giaDen : null;
          }

          if (trimmedPart.startsWith('dien-tich-tu-')) {
            const slug = trimmedPart.replace('dien-tich-tu-', '');
            const dienTichTu = this.parseAreaFromSlug(slug);
            currentFilters.dienTichTu = dienTichTu > 0 ? dienTichTu : null;
          }

          if (trimmedPart.startsWith('dien-tich-toi-')) {
            const slug = trimmedPart.replace('dien-tich-toi-', '');
            const dienTichToi = this.parseAreaFromSlug(slug);
            currentFilters.dienTichToi = dienTichToi > 0 ? dienTichToi : null;
          }
        });

        // Cập nhật priceRange từ filters sau khi parse
        const rangeMin = currentFilters.giaTu ? currentFilters.giaTu / 1000000 : this.priceRange[0];
        const rangeMax = currentFilters.giaDen ? currentFilters.giaDen / 1000000 : this.priceRange[1];
        if (this.config.priceField === 'price_rent') {
          this.priceRangeThue = [rangeMin, rangeMax];
        } else {
          this.priceRangeBan = [rangeMin, rangeMax];
        }

        // Cập nhật areaRange từ filters sau khi parse
        const areaMin = currentFilters.dienTichTu || this.areaRange[0];
        const areaMax = currentFilters.dienTichToi || this.areaRange[1];
        this.areaRange = [areaMin, areaMax];
      }
    }
  }

  applyFilters() {
    const pathParts: string[] = [this.config.routePath];

    if (this.filters.duAn) {
      pathParts.push(`du-an-${this.filters.duAn}`);
    }
    if (this.filters.giaTu) {
      pathParts.push(`gia-tu-${this.formatPriceToSlug(this.filters.giaTu)}`);
    }
    if (this.filters.giaDen) {
      pathParts.push(`gia-den-${this.formatPriceToSlug(this.filters.giaDen)}`);
    }
    if (this.filters.dienTichTu) {
      pathParts.push(`dien-tich-tu-${this.formatAreaToSlug(this.filters.dienTichTu)}`);
    }
    if (this.filters.dienTichToi) {
      pathParts.push(`dien-tich-toi-${this.formatAreaToSlug(this.filters.dienTichToi)}`);
    }

    this.pageIndex = 1;
    const path = '/' + pathParts.join(',');
    this.router.navigateByUrl(path, { replaceUrl: true });
  }

  resetFilters() {
    const currentFilters = this.filters;
    currentFilters.duAn = null;
    currentFilters.giaTu = null;
    currentFilters.giaDen = null;
    currentFilters.dienTichTu = null;
    currentFilters.dienTichToi = null;
    
    // Reset price range về giá trị mặc định
    if (this.config.priceField === 'price_rent') {
      this.priceRangeThue = [5, 100];
    } else {
      this.priceRangeBan = [500, 500000];
    }
    
    // Reset area range về giá trị mặc định
    this.areaRange = [30, 200];
    
    this.pageIndex = 1;
    this.router.navigateByUrl(`/${this.config.routePath}`, { replaceUrl: true });
  }

  onPriceRangeChange(range: number[]) {
    // Convert from millions to VND
    // Giá trị range đã được tính bằng triệu (triệu cho bán, triệu/tháng cho thuê)
    const currentFilters = this.filters;
    currentFilters.giaTu = range[0] * 1000000;
    currentFilters.giaDen = range[1] * 1000000;
  }

  onAreaRangeChange(range: number[]) {
    // Giá trị range đã được tính bằng m²
    const currentFilters = this.filters;
    currentFilters.dienTichTu = range[0];
    currentFilters.dienTichToi = range[1];
  }

  // Getter cho min/max của area slider
  get areaRangeMin(): number {
    return 30; // 30 m²
  }

  get areaRangeMax(): number {
    return 200; // 200 m²
  }

  get areaRangeStep(): number {
    return 5; // Step 5 m²
  }

  /**
   * Convert area in m² to slug format (e.g., 50 -> "50m", 100 -> "100m")
   */
  formatAreaToSlug(valueInM2: number): string {
    return `${Math.round(valueInM2)}m`;
  }

  /**
   * Parse area slug back to m² (e.g., "50m" -> 50, "100m" -> 100)
   */
  parseAreaFromSlug(slug: string): number {
    if (!slug) return 0;
    // Remove 'm' suffix and parse
    const valueStr = slug.replace(/m$/, '');
    const area = parseFloat(valueStr);
    if (!isNaN(area) && area > 0) {
      return area;
    }
    return 0;
  }

  loadApartments() {
    this.loading = true;
    const offset = (this.pageIndex - 1) * this.pageSize;

    const params: any = {
      limit: this.pageSize,
      offset: offset,
      listing_type: this.config.listingType
    };

    if (this.filters.duAnSlug) {
      params.property_group_slug = this.filters.duAnSlug;
    } else if (this.filters.duAn) {
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

  formatPriceLabel(value: number): string {
    if (value >= 1000) {
      const billions = value / 1000;
      return billions % 1 === 0 ? `${billions} tỷ` : `${billions.toFixed(1)} tỷ`;
    }
    return `${value} triệu`;
  }

  /**
   * Convert price in VND to slug format (e.g., 500000000 -> "500-trieu", 13000000000 -> "13-ty")
   */
  formatPriceToSlug(valueInVnd: number): string {
    const valueInMillions = valueInVnd / 1000000;
    if (valueInMillions >= 1000) {
      const billions = valueInMillions / 1000;
      // For whole numbers, use integer; for decimals, use one decimal place
      const billionsStr = billions % 1 === 0 ? Math.round(billions).toString() : billions.toFixed(1);
      // Replace dot with dash for decimal separator in slug
      return `${billionsStr.replace('.', '-')}-ty`;
    }
    // For millions, use integer value
    return `${Math.round(valueInMillions)}-trieu`;
  }

  /**
   * Parse price slug back to VND (e.g., "500-trieu" -> 500000000, "13-ty" -> 13000000000, "13-5-ty" -> 13500000000)
   */
  parsePriceFromSlug(slug: string): number {
    if (!slug) return 0;

    // Handle "ty" (tỷ/billions)
    if (slug.endsWith('-ty')) {
      let valueStr = slug.replace('-ty', '');
      // Replace last dash with dot for decimal (e.g., "13-5-ty" -> "13.5")
      // This handles the case where we have "13-5-ty" (13.5 tỷ)
      const lastDashIndex = valueStr.lastIndexOf('-');
      if (lastDashIndex > 0) {
        // Replace only the last dash with dot
        valueStr = valueStr.substring(0, lastDashIndex) + '.' + valueStr.substring(lastDashIndex + 1);
      }
      const billions = parseFloat(valueStr);
      if (!isNaN(billions) && billions > 0) {
        return billions * 1000 * 1000000; // Convert to VND
      }
    }

    // Handle "trieu" (triệu/millions)
    if (slug.endsWith('-trieu')) {
      const valueStr = slug.replace('-trieu', '');
      const millions = parseFloat(valueStr);
      if (!isNaN(millions) && millions > 0) {
        return millions * 1000000; // Convert to VND
      }
    }

    return 0;
  }

  getStatusColor(status: string): string {
    if (!status) return 'default';
    const statusUpper = status.toUpperCase();
    if (statusUpper.includes('AVAILABLE') || statusUpper.includes('SẴN')) {
      return 'green';
    } else if (statusUpper.includes('SOLD') || statusUpper.includes('ĐÃ BÁN') || statusUpper.includes('RENTED') || statusUpper.includes('ĐÃ THUÊ')) {
      return 'red';
    } else if (statusUpper.includes('RESERVED') || statusUpper.includes('ĐẶT CỌC')) {
      return 'orange';
    }
    return 'default';
  }

  getStatistics(): string {
    if (!this.apartments || this.apartments.length === 0) {
      return '';
    }

    const stats: string[] = [];
    const count = this.apartments.length;

    // Basic count
    stats.push(`Hiện có **${count} căn hộ** đang được hiển thị.`);

    // Price statistics
    const priceField = this.config.priceField || 'price';
    const prices = this.apartments
      .map(apt => priceField === 'price_rent' ? apt.price_rent : apt.price)
      .filter(p => p != null && p > 0) as number[];

    if (prices.length > 0) {
      const avgPrice = prices.reduce((sum, p) => sum + p, 0) / prices.length;
      const minPrice = Math.min(...prices);
      const maxPrice = Math.max(...prices);
      stats.push(`Giá trung bình: **${this.formatPrice(avgPrice)}** (từ **${this.formatPrice(minPrice)}** đến **${this.formatPrice(maxPrice)}**).`);
    }

    // Area statistics
    const areas = this.apartments
      .map(apt => apt.area_net || apt.area_gross)
      .filter(a => a != null && a > 0) as number[];

    if (areas.length > 0) {
      const avgArea = areas.reduce((sum, a) => sum + a, 0) / areas.length;
      const minArea = Math.min(...areas);
      const maxArea = Math.max(...areas);
      stats.push(`Diện tích trung bình: **${avgArea.toFixed(1)} m²** (từ **${minArea.toFixed(1)} m²** đến **${maxArea.toFixed(1)} m²**).`);
    }

    // Bedroom breakdown
    const bedroomCounts = new Map<number, number>();
    this.apartments.forEach(apt => {
      if (apt.num_bedrooms != null) {
        const count = bedroomCounts.get(apt.num_bedrooms) || 0;
        bedroomCounts.set(apt.num_bedrooms, count + 1);
      }
    });

    if (bedroomCounts.size > 0) {
      const bedroomParts = Array.from(bedroomCounts.entries())
        .sort((a, b) => a[0] - b[0])
        .map(([bedrooms, count]) => `**${bedrooms} phòng ngủ** (${count} căn)`);
      stats.push(`Phân bố theo phòng ngủ: ${bedroomParts.join(', ')}.`);
    }

    // Status breakdown
    const statusCounts = new Map<string, number>();
    this.apartments.forEach(apt => {
      if (apt.status) {
        const count = statusCounts.get(apt.status) || 0;
        statusCounts.set(apt.status, count + 1);
      }
    });

    if (statusCounts.size > 0) {
      const statusParts = Array.from(statusCounts.entries())
        .sort((a, b) => b[1] - a[1])
        .map(([status, count]) => `**${status}** (${count} căn)`);
      stats.push(`Trạng thái: ${statusParts.join(', ')}.`);
    }

    return stats.join(' ');
  }

  getPriceDisplay(apartment: Apartment): { main: number | null; early?: number | null } {
    if (this.config.priceField === 'price_rent') {
      return { main: apartment.price_rent || null };
    }
    return {
      main: apartment.price || null,
      early: apartment.price_early || null
    };
  }
}


