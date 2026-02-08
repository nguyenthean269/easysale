import { Component, Input, Output, EventEmitter, OnInit, OnChanges, SimpleChanges } from '@angular/core';
import { CommonModule } from '@angular/common';
import { WarehouseService, Apartment } from '../../../services/warehouse.service';

interface UnprocessedMessage {
  id: number;
  session_id: number;
  config_id?: number;
  sender_id?: string;
  sender_name?: string;
  content: string;
  thread_id?: string;
  thread_type?: string;
  received_at: string;
  status_push_kafka: number;
  warehouse_ids?: number[];
  reply_quote?: string;
  content_hash?: string;
  added_document_chunks?: boolean;
}

interface ProcessResult {
  message_id: number;
  apartment_id: number;
  warehouse_success: boolean;
  replaced?: boolean;
  previous_warehouse_id?: number;
  price_rent?: number;
  phone_number?: string;
  [key: string]: any;
}

@Component({
  selector: 'app-apartment-details-modal',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div *ngIf="visible" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50 modal-backdrop" (click)="onClose()">
      <div class="relative top-10 mx-auto p-5 border w-11/12 md:w-5/6 lg:w-4/5 xl:w-3/4 shadow-lg rounded-md bg-white modal-content" (click)="$event.stopPropagation()">
        <!-- Modal Header -->
        <div class="flex justify-between items-center pb-3 border-b">
          <h3 class="text-lg font-semibold text-gray-900">
            🏠 Apartment Details {{ displayApartments.length > 1 ? '(' + displayApartments.length + ')' : '' }}
          </h3>
          <button (click)="onClose()" class="text-gray-400 hover:text-gray-600">
            <i class="fas fa-times text-xl"></i>
          </button>
        </div>

        <!-- Loading State -->
        <div *ngIf="loading" class="mt-4 text-center py-8">
          <i class="fas fa-spinner fa-spin text-4xl text-blue-600 mb-4"></i>
          <p class="text-gray-600">Loading apartment details...</p>
        </div>

        <!-- Error State -->
        <div *ngIf="error && !loading" class="mt-4 bg-red-50 border border-red-200 rounded-lg p-4">
          <div class="flex items-center">
            <i class="fas fa-exclamation-circle text-red-500 mr-2"></i>
            <span class="text-red-800 font-medium">Error loading apartments</span>
          </div>
          <p class="text-red-700 text-sm mt-1">{{ error }}</p>
        </div>

        <!-- Modal Body -->
        <div *ngIf="!loading && !error && displayApartments.length > 0" class="mt-4">
          <div class="space-y-6">
            <div *ngFor="let apartment of displayApartments; let i = index" class="border border-gray-200 rounded-lg p-4">
              <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                
                <!-- Column 1: Insert result (from insertResults) -->
                <div class="space-y-4">
                  <h4 class="text-lg font-semibold text-blue-900 border-b-2 border-blue-200 pb-2">
                    📊 Process Result {{ i + 1 }}
                  </h4>
                  
                  <div *ngIf="getResultForApartment(apartment) as result" class="space-y-3">
                    <div class="flex justify-between">
                      <span class="font-medium text-gray-600">Message ID:</span>
                      <span class="text-gray-900 font-mono">{{ result.message_id || 'N/A' }}</span>
                    </div>
                    
                    <div class="flex justify-between">
                      <span class="font-medium text-gray-600">Apartment ID:</span>
                      <span class="text-green-600 font-semibold">{{ result.apartment_id || 'N/A' }}</span>
                    </div>
                    
                    <div class="flex justify-between">
                      <span class="font-medium text-gray-600">Warehouse Success:</span>
                      <span class="inline-flex items-center">
                        <i *ngIf="result.warehouse_success" class="fas fa-check-circle text-green-500 mr-1"></i>
                        <i *ngIf="!result.warehouse_success" class="fas fa-times-circle text-red-500 mr-1"></i>
                        <span [ngClass]="result.warehouse_success ? 'text-green-600' : 'text-red-600'">
                          {{ result.warehouse_success ? 'Success' : 'Failed' }}
                        </span>
                      </span>
                    </div>
                    
                    <div *ngIf="result.replaced" class="flex justify-between">
                      <span class="font-medium text-gray-600">Replaced:</span>
                      <span class="text-orange-600 font-semibold">Yes</span>
                    </div>
                    
                    <div *ngIf="result.previous_warehouse_id" class="flex justify-between">
                      <span class="font-medium text-gray-600">Previous Warehouse ID:</span>
                      <span class="text-gray-900">{{ result.previous_warehouse_id }}</span>
                    </div>
                    
                    <div *ngIf="result.price_rent" class="flex justify-between">
                      <span class="font-medium text-gray-600">Rent Price:</span>
                      <span class="text-red-600 font-semibold">{{ formatPrice(result.price_rent) }}</span>
                    </div>
                    
                    <div *ngIf="result.phone_number" class="flex justify-between">
                      <span class="font-medium text-gray-600">Phone Number:</span>
                      <span class="text-blue-600 font-mono">{{ result.phone_number }}</span>
                    </div>
                    
                    <!-- Display all other fields from result -->
                    <div *ngIf="hasAdditionalFields(result)" class="mt-4">
                      <h5 class="font-medium text-gray-700 mb-2">📋 Additional Info:</h5>
                      <div class="bg-gray-50 p-3 rounded-lg max-h-40 overflow-y-auto">
                        <div *ngFor="let key of getAdditionalFields(result)" class="text-xs mb-1">
                          <span class="font-medium text-gray-600">{{ key }}:</span>
                          <span class="text-gray-800 ml-2">{{ formatValue(result[key]) }}</span>
                        </div>
                      </div>
                    </div>
                    
                    <!-- Message Content (if available from messages) -->
                    <div *ngIf="getMessageForApartment(apartment) as message" class="mt-4">
                      <h5 class="font-medium text-gray-700 mb-2">📝 Message Content:</h5>
                      <div class="bg-gray-50 p-3 rounded-lg max-h-40 overflow-y-auto">
                        <p class="text-sm text-gray-800 whitespace-pre-wrap">{{ message.content }}</p>
                      </div>
                    </div>
                  </div>
                  
                  <div *ngIf="!getResultForApartment(apartment)" class="text-gray-500 text-sm">
                    No result data available for this apartment
                  </div>
                </div>
                
                <!-- Column 2: Warehouse Apartment Details -->
                <div class="space-y-4">
                  <h4 class="text-lg font-semibold text-green-900 border-b-2 border-green-200 pb-2">
                    🏠 Apartment {{ i + 1 }} (ID: {{ apartment.id }})
                  </h4>
                  {{apartment | json}}
                  
                  <!-- Basic Information -->
                  <div class="space-y-2 text-sm">
                    <div class="flex justify-between">
                      <span class="font-medium text-gray-600">Loại tin:</span>
                      <span class="text-gray-900">{{ apartment.listing_type ?? 'N/A' }}</span>
                    </div>
                    
                    <div class="flex justify-between">
                      <span class="font-medium text-gray-600">Tòa/Khu:</span>
                      <span class="text-gray-900">{{ apartment.property_group_name || 'N/A' }}</span>
                    </div>
                    
                    <div class="flex justify-between">
                      <span class="font-medium text-gray-600">Mã căn:</span>
                      <span class="text-gray-900 font-mono">{{ apartment.unit_code || 'N/A' }}</span>
                    </div>
                    
                    <div class="flex justify-between">
                      <span class="font-medium text-gray-600">Loại căn:</span>
                      <span class="text-gray-900">{{ apartment.unit_type_name || 'N/A' }}</span>
                    </div>
                    
                    <div class="flex justify-between">
                      <span class="font-medium text-gray-600">Tầng:</span>
                      <span class="text-gray-900">{{ apartment.unit_floor_number || 'N/A' }}</span>
                    </div>
                    
                    <div class="flex justify-between">
                      <span class="font-medium text-gray-600">Diện tích:</span>
                      <span class="text-gray-900">{{ formatArea(apartment.area_gross) }}</span>
                    </div>
                    
                    <div class="flex justify-between">
                      <span class="font-medium text-gray-600">Giá:</span>
                      <span class="text-green-600 font-semibold">{{ formatPrice(apartment.price) }}</span>
                    </div>
                    
                    <div class="flex justify-between">
                      <span class="font-medium text-gray-600">Giá thuê:</span>
                      <span class="text-red-600">{{ formatPrice(apartment.price_rent) }}</span>
                    </div>
                    
                    <div class="flex justify-between">
                      <span class="font-medium text-gray-600">Số phòng ngủ:</span>
                      <span class="text-gray-900">{{ apartment.num_bedrooms || 'N/A' }}</span>
                    </div>
                    
                    <div class="flex justify-between">
                      <span class="font-medium text-gray-600">Số phòng tắm:</span>
                      <span class="text-gray-900">{{ apartment.num_bathrooms || 'N/A' }}</span>
                    </div>
                    
                    <div class="flex justify-between">
                      <span class="font-medium text-gray-600">Nội thất:</span>
                      <span class="text-gray-900">{{ apartment.furnished_status ?? 'N/A' }}</span>
                    </div>
                    
                    <div class="flex justify-between">
                      <span class="font-medium text-gray-600">Khoảng tầng:</span>
                      <span class="text-gray-900">{{ apartment.floor_level_category ?? 'N/A' }}</span>
                    </div>
                    
                    <div class="flex justify-between">
                      <span class="font-medium text-gray-600">Vào luôn:</span>
                      <span class="text-gray-900">{{ formatBoolean(apartment.move_in_ready) }}</span>
                    </div>
                    
                    <div class="flex justify-between">
                      <span class="font-medium text-gray-600">Bao phí:</span>
                      <span class="text-gray-900">{{ formatBoolean(apartment.includes_transfer_fees) }}</span>
                    </div>
                    
                    <div class="flex justify-between">
                      <span class="font-medium text-gray-600">Trạng thái:</span>
                      <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium"
                            [ngClass]="{
                              'bg-amber-100 text-amber-800': apartment.data_status === 'REVIEWING',
                              'bg-gray-100 text-gray-800': apartment.data_status === 'PENDING',
                              'bg-green-100 text-green-800': apartment.data_status === 'APPROVED'
                            }">
                        {{ apartment.data_status || 'N/A' }}
                      </span>
                    </div>
                    
                    <div class="mt-4 flex gap-2 flex-wrap">
                      <button *ngIf="apartment.data_status === 'REVIEWING'"
                              (click)="approveApartment(apartment)"
                              [disabled]="actionLoading[apartment.id]"
                              class="px-3 py-1.5 text-sm font-medium rounded-md bg-green-600 text-white hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed">
                        <i *ngIf="!actionLoading[apartment.id]" class="fas fa-check mr-1"></i>
                        <i *ngIf="actionLoading[apartment.id]" class="fas fa-spinner fa-spin mr-1"></i>
                        Duyệt
                      </button>
                      <button (click)="deleteApartmentItem(apartment)"
                              [disabled]="actionLoading[apartment.id]"
                              class="px-3 py-1.5 text-sm font-medium rounded-md bg-red-600 text-white hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed">
                        <i *ngIf="!actionLoading[apartment.id]" class="fas fa-trash mr-1"></i>
                        <i *ngIf="actionLoading[apartment.id]" class="fas fa-spinner fa-spin mr-1"></i>
                        Xóa
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Modal Footer -->
        <div class="flex justify-end pt-4 border-t mt-4">
          <button (click)="onClose()" 
                  class="px-4 py-2 bg-gray-500 text-white text-base font-medium rounded-md shadow-sm hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-gray-300">
            Close
          </button>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .fa-spinner {
      animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
      from { transform: rotate(0deg); }
      to { transform: rotate(360deg); }
    }
    
    .max-h-40 {
      max-height: 10rem;
    }
    
    .overflow-y-auto::-webkit-scrollbar {
      width: 4px;
    }
    
    .overflow-y-auto::-webkit-scrollbar-track {
      background: #f1f1f1;
      border-radius: 2px;
    }
    
    .overflow-y-auto::-webkit-scrollbar-thumb {
      background: #c1c1c1;
      border-radius: 2px;
    }
    
    .overflow-y-auto::-webkit-scrollbar-thumb:hover {
      background: #a8a8a8;
    }
    
    /* Modal animations */
    .modal-backdrop {
      animation: fadeIn 0.3s ease-out;
    }
    
    .modal-content {
      animation: slideIn 0.3s ease-out;
    }
    
    @keyframes fadeIn {
      from { opacity: 0; }
      to { opacity: 1; }
    }
    
    @keyframes slideIn {
      from { 
        opacity: 0;
        transform: translateY(-50px);
      }
      to { 
        opacity: 1;
        transform: translateY(0);
      }
    }
  `]
})
export class ApartmentDetailsModalComponent implements OnInit, OnChanges {
  @Input() visible: boolean = false;
  @Input() warehouseApartmentIds: number[] = [];
  @Input() warehouseApartments: Apartment[] = [];
  @Input() insertResults: ProcessResult[] = [];
  @Input() zaloMessages: UnprocessedMessage[] = [];
  
  @Output() close = new EventEmitter<void>();
  @Output() apartmentUpdated = new EventEmitter<{ apartmentId: number; action: 'approved' | 'deleted' }>();

  displayApartments: Apartment[] = [];
  loading: boolean = false;
  error: string | null = null;
  actionLoading: { [id: number]: boolean } = {};

  constructor(private warehouseService: WarehouseService) {}

  ngOnInit() {
    // Không load ở đây, chỉ load khi modal được mở (visible = true)
  }

  ngOnChanges(changes: SimpleChanges) {
    if (changes['warehouseApartments'] && this.warehouseApartments && this.warehouseApartments.length > 0) {
      this.displayApartments = this.warehouseApartments;
      this.loading = false;
      this.error = null;
      return;
    }
    
    if (changes['visible'] && this.visible && !changes['visible'].previousValue) {
      if (this.warehouseApartments && this.warehouseApartments.length > 0) {
        this.displayApartments = this.warehouseApartments;
        this.loading = false;
        this.error = null;
      } else if (this.warehouseApartmentIds.length > 0) {
        this.loadApartments();
      }
    }
    
    if (changes['warehouseApartmentIds'] && this.visible && this.warehouseApartmentIds.length > 0 && (!this.warehouseApartments || this.warehouseApartments.length === 0)) {
      const prevIds = changes['warehouseApartmentIds'].previousValue || [];
      const currentIds = changes['warehouseApartmentIds'].currentValue || [];
      if (JSON.stringify(prevIds.sort()) !== JSON.stringify(currentIds.sort())) {
        this.loadApartments();
      }
    }
  }

  loadApartments() {
    if (this.warehouseApartments && this.warehouseApartments.length > 0) {
      this.displayApartments = this.warehouseApartments;
      return;
    }
    
    if (this.warehouseApartmentIds.length === 0) {
      this.error = 'No warehouse apartment IDs provided';
      return;
    }

    this.loading = true;
    this.error = null;
    this.displayApartments = [];

    this.warehouseService.getApartmentsByIds(this.warehouseApartmentIds).subscribe({
      next: (response) => {
        this.loading = false;
        if (response.success && response.data.length > 0) {
          this.displayApartments = response.data;
        } else {
          this.error = 'No apartments found';
        }
      },
      error: (error) => {
        this.loading = false;
        this.error = error.message || 'Failed to load apartments';
        console.error('Error loading apartments:', error);
      }
    });
  }

  onClose() {
    this.close.emit();
  }

  /** Chuẩn hóa warehouse_ids (array hoặc chuỗi JSON) thành number[]. */
  private getMessageWarehouseIds(msg: UnprocessedMessage): number[] {
    const raw = msg?.warehouse_ids;
    if (raw == null) return [];
    if (Array.isArray(raw)) return raw.map(id => Number(id)).filter(n => !Number.isNaN(n));
    if (typeof raw === 'string') {
      try {
        const parsed = JSON.parse(raw);
        return Array.isArray(parsed) ? parsed.map((id: any) => Number(id)).filter((n: number) => !Number.isNaN(n)) : [];
      } catch {
        return [];
      }
    }
    return [];
  }

  getMessageForApartment(apartment: Apartment): UnprocessedMessage | null {
    const result = this.insertResults.find(r => r.apartment_id === apartment.id);
    if (result) {
      return this.zaloMessages.find(msg => msg.id === result.message_id) || null;
    }
    return this.zaloMessages.find(msg => this.getMessageWarehouseIds(msg).includes(apartment.id)) || null;
  }

  getResultForApartment(apartment: Apartment): ProcessResult | null {
    return this.insertResults.find(r => r.apartment_id === apartment.id) || null;
  }

  approveApartment(apartment: Apartment): void {
    this.actionLoading = { ...this.actionLoading, [apartment.id]: true };
    this.warehouseService.updateApartmentDataStatus(apartment.id, 'APPROVED').subscribe({
      next: (res) => {
        this.actionLoading = { ...this.actionLoading, [apartment.id]: false };
        if (res.success) {
          apartment.data_status = 'APPROVED';
          this.apartmentUpdated.emit({ apartmentId: apartment.id, action: 'approved' });
        }
      },
      error: () => { this.actionLoading = { ...this.actionLoading, [apartment.id]: false }; }
    });
  }

  deleteApartmentItem(apartment: Apartment): void {
    if (!confirm('Xóa căn này khỏi warehouse?')) return;
    this.actionLoading = { ...this.actionLoading, [apartment.id]: true };
    this.warehouseService.deleteApartment(apartment.id).subscribe({
      next: (res) => {
        this.actionLoading = { ...this.actionLoading, [apartment.id]: false };
        if (res.success) {
          this.displayApartments = this.displayApartments.filter(a => a.id !== apartment.id);
          this.apartmentUpdated.emit({ apartmentId: apartment.id, action: 'deleted' });
        }
      },
      error: () => { this.actionLoading = { ...this.actionLoading, [apartment.id]: false }; }
    });
  }

  hasAdditionalFields(result: ProcessResult): boolean {
    const standardFields = ['message_id', 'apartment_id', 'warehouse_success', 'replaced', 'previous_warehouse_id', 'price_rent', 'phone_number'];
    return Object.keys(result).some(key => !standardFields.includes(key));
  }

  getAdditionalFields(result: ProcessResult): string[] {
    const standardFields = ['message_id', 'apartment_id', 'warehouse_success', 'replaced', 'previous_warehouse_id', 'price_rent', 'phone_number'];
    return Object.keys(result).filter(key => !standardFields.includes(key));
  }

  formatValue(value: any): string {
    if (value === null || value === undefined) return 'N/A';
    if (typeof value === 'object') return JSON.stringify(value);
    return String(value);
  }

  formatPrice(price: number | undefined): string {
    if (!price) return 'N/A';
    if (price >= 1000000000) {
      return `${(price / 1000000000).toFixed(1)} tỷ`;
    } else if (price >= 1000000) {
      return `${(price / 1000000).toFixed(0)} triệu`;
    }
    return price.toLocaleString();
  }

  formatArea(area: number | undefined): string {
    if (!area) return 'N/A';
    return `${area}m²`;
  }

  formatBoolean(value: boolean | undefined | null): string {
    if (value === null || value === undefined) return 'N/A';
    return value ? 'Có' : 'Không';
  }
}

