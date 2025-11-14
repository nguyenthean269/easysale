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
  warehouse_id?: number;
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
                
                <!-- Column 1: Process Results (from modalResults/results) -->
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
                  
                  <!-- Basic Information -->
                  <div class="space-y-2 text-sm">
                    <div class="flex justify-between">
                      <span class="font-medium text-gray-600">Property Group:</span>
                      <span class="text-gray-900">{{ apartment.property_group_name || 'N/A' }}</span>
                    </div>
                    
                    <div class="flex justify-between">
                      <span class="font-medium text-gray-600">Unit Code:</span>
                      <span class="text-gray-900 font-mono">{{ apartment.unit_code || 'N/A' }}</span>
                    </div>
                    
                    <div class="flex justify-between">
                      <span class="font-medium text-gray-600">Unit Type:</span>
                      <span class="text-gray-900">{{ apartment.unit_type_name || 'N/A' }}</span>
                    </div>
                    
                    <div class="flex justify-between">
                      <span class="font-medium text-gray-600">Floor:</span>
                      <span class="text-gray-900">{{ apartment.unit_floor_number || 'N/A' }}</span>
                    </div>
                    
                    <div class="flex justify-between">
                      <span class="font-medium text-gray-600">Area:</span>
                      <span class="text-gray-900">{{ formatArea(apartment.area_gross) }}</span>
                    </div>
                    
                    <div class="flex justify-between">
                      <span class="font-medium text-gray-600">Price:</span>
                      <span class="text-green-600 font-semibold">{{ formatPrice(apartment.price) }}</span>
                    </div>
                    
                    <div class="flex justify-between">
                      <span class="font-medium text-gray-600">Rent Price:</span>
                      <span class="text-red-600">{{ formatPrice(apartment.price_rent) }}</span>
                    </div>
                    
                    <div class="flex justify-between">
                      <span class="font-medium text-gray-600">Bedrooms:</span>
                      <span class="text-gray-900">{{ apartment.num_bedrooms || 'N/A' }}</span>
                    </div>
                    
                    <div class="flex justify-between">
                      <span class="font-medium text-gray-600">Bathrooms:</span>
                      <span class="text-gray-900">{{ apartment.num_bathrooms || 'N/A' }}</span>
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
  @Input() apartmentIds: number[] = []; // Fallback: chỉ dùng khi không có apartments data
  @Input() apartments: Apartment[] = []; // Full apartment data từ API response (ưu tiên)
  @Input() results: ProcessResult[] = [];
  @Input() messages: UnprocessedMessage[] = [];
  
  @Output() close = new EventEmitter<void>();

  displayApartments: Apartment[] = []; // Apartments để hiển thị
  loading: boolean = false;
  error: string | null = null;

  constructor(private warehouseService: WarehouseService) {}

  ngOnInit() {
    // Không load ở đây, chỉ load khi modal được mở (visible = true)
  }

  ngOnChanges(changes: SimpleChanges) {
    // Nếu có apartments data sẵn, dùng luôn (không cần gọi API)
    if (changes['apartments'] && this.apartments && this.apartments.length > 0) {
      this.displayApartments = this.apartments;
      this.loading = false;
      this.error = null;
      return;
    }
    
    // Nếu không có apartments data, chỉ load khi visible thay đổi từ false sang true
    if (changes['visible'] && this.visible && !changes['visible'].previousValue) {
      if (this.apartments && this.apartments.length > 0) {
        // Có apartments data sẵn, dùng luôn
        this.displayApartments = this.apartments;
        this.loading = false;
        this.error = null;
      } else if (this.apartmentIds.length > 0) {
        // Không có apartments data, gọi API với apartmentIds
        this.loadApartments();
      }
    }
    
    // Nếu apartmentIds thay đổi và modal đang visible, reload (chỉ khi không có apartments data)
    if (changes['apartmentIds'] && this.visible && this.apartmentIds.length > 0 && (!this.apartments || this.apartments.length === 0)) {
      const prevIds = changes['apartmentIds'].previousValue || [];
      const currentIds = changes['apartmentIds'].currentValue || [];
      // Chỉ reload nếu IDs thực sự khác nhau
      if (JSON.stringify(prevIds.sort()) !== JSON.stringify(currentIds.sort())) {
        this.loadApartments();
      }
    }
  }

  loadApartments() {
    // Chỉ gọi API khi không có apartments data sẵn
    if (this.apartments && this.apartments.length > 0) {
      this.displayApartments = this.apartments;
      return;
    }
    
    if (this.apartmentIds.length === 0) {
      this.error = 'No apartment IDs provided';
      return;
    }

    this.loading = true;
    this.error = null;
    this.displayApartments = [];

    this.warehouseService.getApartmentsByIds(this.apartmentIds).subscribe({
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

  getMessageForApartment(apartment: Apartment): UnprocessedMessage | null {
    // Tìm message từ results dựa trên apartment_id
    const result = this.results.find(r => r.apartment_id === apartment.id);
    if (result) {
      return this.messages.find(msg => msg.id === result.message_id) || null;
    }
    // Fallback: tìm từ warehouse_id
    return this.messages.find(msg => msg.warehouse_id === apartment.id) || null;
  }

  getResultForApartment(apartment: Apartment): ProcessResult | null {
    return this.results.find(r => r.apartment_id === apartment.id) || null;
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
}

