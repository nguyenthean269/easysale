import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { WarehouseService, Apartment } from '../../services/warehouse.service';
import { ZaloTestService } from '../../services/zalo-test.service';
import { ApartmentDetailsModalComponent } from './apartment-details-modal/apartment-details-modal.component';

interface ZaloTestMessage {
  message_id?: number;
  message_content?: string;
}

interface ZaloTestResponse {
  success: boolean;
  data?: any;
  error?: string;
  message?: string;
}

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

interface ProcessorStatus {
  is_running: boolean;
  thread_alive: boolean;
  interval: number;
  interval_minutes: number;
  schedule_enabled: boolean;
  started_at?: string;
}

interface PropertyTreeData {
  root_id: number;
  property_tree: string;
}

interface BatchProcessResult {
  processed_count: number;
  error_count: number;
  total_processed: number;
}

interface ParsedApartmentData {
  property_group?: number;
  unit_code?: string;
  unit_axis?: string;
  unit_floor_number?: number;
  area_land?: number;
  area_construction?: number;
  area_net?: number;
  area_gross?: number;
  num_bedrooms?: number;
  num_bathrooms?: number;
  unit_type?: number;
  direction_door?: string;
  direction_balcony?: string;
  price?: number;
  price_early?: number;
  price_schedule?: number;
  price_loan?: number;
  notes?: string;
  status?: string;
}


@Component({
  selector: 'app-zalo-test',
  standalone: true,
  imports: [CommonModule, FormsModule, ApartmentDetailsModalComponent],
  template: `
    <div class="min-h-screen bg-gray-50 p-6">
      <div class="max-w-7xl mx-auto">
        <div class="bg-white rounded-lg shadow-sm border border-gray-200">
          <div class="px-6 py-4 border-b border-gray-200">
            <h3 class="text-xl font-semibold text-gray-800">
              <i class="fas fa-comments mr-2 text-blue-600"></i>
              Zalo Message Processor Test
            </h3>
          </div>
          <div class="p-6">
            
            <!-- Processor Status -->
            <div class="mb-6">
              <div class="bg-gray-50 rounded-lg border border-gray-200">
                <div class="p-4">
                  <div class="flex justify-between items-center mb-4">
                    <h5 class="text-lg font-semibold text-gray-800">Processor Status</h5>
                    <div class="flex items-center gap-2">
                      <span class="text-xs text-gray-500" *ngIf="autoRefreshEnabled">
                        <i class="fas fa-sync-alt fa-spin mr-1"></i> Auto-refresh
                      </span>
                      <button class="bg-gray-500 hover:bg-gray-600 text-white px-3 py-1 rounded text-xs font-medium transition-colors" 
                              (click)="toggleAutoRefresh()">
                        <i class="fas mr-1" [ngClass]="autoRefreshEnabled ? 'fa-pause' : 'fa-play'"></i>
                        {{ autoRefreshEnabled ? 'Pause' : 'Start' }} Auto-refresh
                      </button>
                    </div>
                  </div>
                  <div class="grid md:grid-cols-2 gap-4">
                    <div>
                      <p class="mb-2"><span class="font-medium">Running:</span> 
                        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium" 
                              [ngClass]="processorStatus?.is_running ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'">
                          {{ processorStatus?.is_running ? 'Yes' : 'No' }}
                        </span>
                      </p>
                      <p class="mb-2"><span class="font-medium">Schedule Enabled:</span> 
                        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium" 
                              [ngClass]="processorStatus?.schedule_enabled ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'">
                          {{ processorStatus?.schedule_enabled ? 'Yes' : 'No' }}
                        </span>
                      </p>
                    </div>
                    <div>
                      <p class="mb-2"><span class="font-medium">Interval:</span> {{ processorStatus?.interval_minutes }} minutes</p>
                      <p class="mb-2"><span class="font-medium">Started At:</span> {{ processorStatus?.started_at | date:'medium' }}</p>
                    </div>
                  </div>
                  <div class="mt-4 flex gap-2">
                    <button *ngIf="!processorStatus?.is_running" 
                            class="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed" 
                            (click)="startSchedule()"
                            [disabled]="scheduleControlLoading">
                      <i *ngIf="!scheduleControlLoading" class="fas fa-play mr-1"></i>
                      <i *ngIf="scheduleControlLoading" class="fas fa-spinner fa-spin mr-1"></i>
                      {{ scheduleControlLoading ? 'Starting...' : 'Start Schedule' }}
                    </button>
                    <button *ngIf="processorStatus?.is_running" 
                            class="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed" 
                            (click)="stopSchedule()"
                            [disabled]="scheduleControlLoading">
                      <i *ngIf="!scheduleControlLoading" class="fas fa-stop mr-1"></i>
                      <i *ngIf="scheduleControlLoading" class="fas fa-spinner fa-spin mr-1"></i>
                      {{ scheduleControlLoading ? 'Stopping...' : 'Stop Schedule' }}
                    </button>
                    <button class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors" 
                            (click)="refreshStatus()">
                      <i class="fas fa-refresh mr-1"></i> Refresh Status
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <!-- Test Message Input -->
            <div class="mb-6">
              <div class="bg-white rounded-lg border border-gray-200">
                <div class="px-4 py-3 border-b border-gray-200">
                  <h5 class="text-lg font-semibold text-gray-800">Test Message</h5>
                </div>
                <div class="p-4">
                  <div class="grid md:grid-cols-2 gap-4">
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-2">Message ID</label>
                      <input type="number" 
                             [(ngModel)]="testMessageId" 
                             class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                             placeholder="Enter message ID">
                      <button class="mt-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors" 
                              (click)="testByMessageId()" 
                              [disabled]="processing || !testMessageId">
                        <i class="fas fa-play mr-1"></i> Test by ID
                      </button>
                    </div>
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-2">Custom Message</label>
                      <textarea [(ngModel)]="testMessageContent" 
                                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                rows="3"
                                placeholder="Enter custom message content"></textarea>
                      <button class="mt-2 bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors" 
                              (click)="testByMessageContent()" 
                              [disabled]="processing || !testMessageContent.trim()">
                        <i class="fas fa-play mr-1"></i> Test Custom
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Messages -->
            <div class="mb-6">
              <div class="bg-white rounded-lg border border-gray-200">
                <div class="px-4 py-3 border-b border-gray-200 flex justify-between items-center">
                  <h5 class="text-lg font-semibold text-gray-800">
                    Messages ({{ totalMessages > 0 ? totalMessages : unprocessedMessages.length }})
                    <span class="text-sm font-normal text-gray-500 ml-2">
                      (Page {{ currentPage }}, showing {{ unprocessedMessages.length }})
                    </span>
                  </h5>
                  <div class="flex gap-2 items-center flex-wrap">
                    <select [(ngModel)]="messageWarehouseIdFilter" 
                            (change)="onWarehouseIdFilterChange()"
                            class="px-3 py-1 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
                      <option value="NULL">Chưa push vào Warehouse</option>
                      <option value="NOT_NULL">Đã push vào Warehouse</option>
                      <option value="ALL">Tất cả Messages</option>
                    </select>
                    <select [(ngModel)]="messageSort" 
                            (change)="onMessageSortChange()"
                            class="px-3 py-1 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                            title="Sắp xếp theo thời gian">
                      <option value="newest">Mới nhất trước</option>
                      <option value="oldest">Cũ nhất trước</option>
                    </select>
                  <button class="bg-gray-600 hover:bg-gray-700 text-white px-3 py-1 rounded text-sm font-medium transition-colors" 
                          (click)="loadUnprocessedMessages()">
                    <i class="fas fa-refresh mr-1"></i> Refresh
                  </button>
                    
                    <!-- Batch Processing Controls -->
                    <div *ngIf="selectedMessageIds.length > 0" class="flex gap-2 items-center ml-4 pl-4 border-l border-gray-300">
                      <span class="text-sm text-gray-600">{{ selectedMessageIds.length }} selected</span>
                      <button class="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded text-sm font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed" 
                              (click)="processSelectedMessages()"
                              [disabled]="batchProcessing">
                        <i *ngIf="!batchProcessing" class="fas fa-play mr-1"></i>
                        <i *ngIf="batchProcessing" class="fas fa-spinner fa-spin mr-1"></i>
                        {{ batchProcessing ? 'Processing...' : 'Process Selected' }}
                      </button>
                      <button class="bg-gray-500 hover:bg-gray-600 text-white px-3 py-1 rounded text-sm font-medium transition-colors" 
                              (click)="clearSelection()">
                        <i class="fas fa-times mr-1"></i> Clear
                      </button>
                    </div>
                  </div>
                </div>
                <div class="p-4">
                  <div *ngIf="unprocessedMessages.length > 0" class="overflow-x-auto">
                    <table class="min-w-full divide-y divide-gray-200">
                      <thead class="bg-gray-50">
                        <tr>
                          <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            <input type="checkbox" 
                                   [checked]="selectedMessageIds.length === unprocessedMessages.length && unprocessedMessages.length > 0"
                                   [indeterminate]="selectedMessageIds.length > 0 && selectedMessageIds.length < unprocessedMessages.length"
                                   (change)="selectedMessageIds.length === unprocessedMessages.length ? clearSelection() : selectAllMessages()"
                                   class="rounded border-gray-300 text-blue-600 focus:ring-blue-500">
                          </th>
                          <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
                          <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Content</th>
                          <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Created At</th>
                          <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                          <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Warehouse</th>
                          <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                        </tr>
                      </thead>
                      <tbody class="bg-white divide-y divide-gray-200">
                        <tr *ngFor="let message of unprocessedMessages" class="hover:bg-gray-50">
                          <td class="px-6 py-4 whitespace-nowrap">
                            <input type="checkbox" 
                                   [checked]="isMessageSelected(message.id)"
                                   (change)="toggleMessageSelection(message.id)"
                                   class="rounded border-gray-300 text-blue-600 focus:ring-blue-500">
                          </td>
                          <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{{ message.id }}</td>
                          <td class="px-6 py-4 text-sm text-gray-500 max-w-md">
                            <div class="max-h-20 overflow-y-auto" 
                                 [title]="message.content"
                                 [attr.data-tooltip]="message.content">
                              {{ message.content }}
                            </div>
                          </td>
                          <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ message.received_at | date:'short' }}</td>
                          <td class="px-6 py-4 whitespace-nowrap">
                            <span *ngIf="getMessageWarehouseIds(message).length" class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                              Warehouse IDs: {{ getMessageWarehouseIds(message).join(', ') }}
                            </span>
                            <span *ngIf="!getMessageWarehouseIds(message).length" class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                              Chưa push
                            </span>
                          </td>
                          <td class="px-6 py-4 text-sm text-gray-900">
                            <div *ngIf="getApartmentForMessage(message.id)" class="space-y-1">
                              <div class="text-xs">
                                <span class="font-medium">ID:</span> {{ getApartmentForMessage(message.id)?.id }}<br>
                                <span class="font-medium">Property:</span> {{ getApartmentForMessage(message.id)?.property_group_name || 'N/A' }}<br>
                                <span class="font-medium">Unit:</span> {{ getApartmentForMessage(message.id)?.unit_code || 'N/A' }}<br>
                                <span class="font-medium">Type:</span> {{ getApartmentForMessage(message.id)?.unit_type_name || 'N/A' }}<br>
                                <span class="font-medium">Area:</span> {{ formatArea(getApartmentForMessage(message.id)?.area_gross) }}<br>
                                <span class="font-medium">Price:</span> {{ formatPrice(getApartmentForMessage(message.id)?.price) }}
                                <span class="font-medium">Price rent:</span> {{ formatPrice(getApartmentForMessage(message.id)?.price_rent) }}
                              </div>
                            </div>
                            <div *ngIf="!getApartmentForMessage(message.id)" class="text-gray-400 text-xs">
                              <div>No apartment</div>
                              <div class="text-gray-300">Warehouse IDs: {{ getMessageWarehouseIds(message).length ? getMessageWarehouseIds(message).join(', ') : 'NULL' }}</div>
                            </div>
                          </td>
                          <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                            <div class="flex space-x-2">
                              <!-- Test Button -->
                              <button class="inline-flex items-center px-3 py-1.5 text-sm font-medium text-blue-600 hover:text-blue-900 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 rounded-md hover:bg-blue-50" 
                                      (click)="testByMessageIdFromTable(message.id)"
                                      [disabled]="processing || messageLoadingStates.get(message.id)">
                                <i *ngIf="!messageLoadingStates.get(message.id)" class="fas fa-play mr-1"></i>
                                <i *ngIf="messageLoadingStates.get(message.id)" class="fas fa-spinner fa-spin mr-1"></i>
                                {{ messageLoadingStates.get(message.id) ? 'Processing...' : 'Test' }}
                              </button>
                              
                              <!-- Detail Button (only show if has warehouse_ids) -->
                              <button *ngIf="getMessageWarehouseIds(message).length" 
                                      class="inline-flex items-center px-3 py-1.5 text-sm font-medium text-green-600 hover:text-green-900 transition-all duration-200 rounded-md hover:bg-green-50" 
                                      (click)="openDetailModal(message.id)">
                                <i class="fas fa-eye mr-1"></i>
                                Detail
                            </button>
                            </div>
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                  <div *ngIf="unprocessedMessages.length === 0" class="text-center py-8 text-gray-500">
                    <i class="fas fa-inbox text-4xl mb-2"></i>
                    <p>No unprocessed messages found.</p>
                  </div>
                  
                  <!-- Pagination Controls -->
                  <div *ngIf="unprocessedMessages.length > 0 || currentPage > 1" class="mt-4 flex items-center justify-between border-t border-gray-200 pt-4">
                    <div class="flex items-center gap-2">
                      <span class="text-sm text-gray-700">Items per page:</span>
                      <select [(ngModel)]="pageSize" 
                              (change)="onPageSizeChange()"
                              class="px-2 py-1 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
                        <option [value]="10">10</option>
                        <option [value]="20">20</option>
                        <option [value]="50">50</option>
                        <option [value]="100">100</option>
                      </select>
                    </div>
                    <div class="flex items-center gap-2">
                      <button class="px-3 py-1 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                              (click)="goToPage(1)"
                              [disabled]="currentPage === 1">
                        <i class="fas fa-angle-double-left"></i>
                      </button>
                      <button class="px-3 py-1 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                              (click)="goToPage(currentPage - 1)"
                              [disabled]="currentPage === 1">
                        <i class="fas fa-angle-left"></i>
                      </button>
                      <span class="px-3 py-1 text-sm text-gray-700">
                        Page {{ currentPage }} of {{ getTotalPages() }}
                      </span>
                      <button class="px-3 py-1 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                              (click)="goToPage(currentPage + 1)"
                              [disabled]="currentPage >= getTotalPages()">
                        <i class="fas fa-angle-right"></i>
                      </button>
                      <button class="px-3 py-1 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                              (click)="goToPage(getTotalPages())"
                              [disabled]="currentPage >= getTotalPages()">
                        <i class="fas fa-angle-double-right"></i>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Batch Processing Results -->
            <div *ngIf="batchProcessingResult" class="mb-6">
              <div class="bg-white rounded-lg border border-gray-200">
                <div class="px-4 py-3 border-b border-gray-200">
                  <h5 class="text-lg font-semibold text-gray-800">Batch Processing Results</h5>
                </div>
                <div class="p-4">
                  <div *ngIf="batchProcessingResult.success" class="space-y-4">
                    <div class="bg-green-50 border border-green-200 rounded-lg p-4">
                      <div class="flex items-center">
                        <i class="fas fa-check-circle text-green-500 mr-2"></i>
                        <span class="text-green-800 font-medium">Batch Processing Completed Successfully</span>
                      </div>
                      <p class="text-green-700 text-sm mt-1">{{ getBatchSummary() }}</p>
                    </div>
                    
                    <div *ngIf="batchProcessingResult.data?.insert_results" class="space-y-2">
                      <h6 class="font-medium text-gray-700">Individual Results:</h6>
                      <div *ngFor="let result of batchProcessingResult.data.insert_results" 
                           class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <div class="flex items-center">
                          <i *ngIf="result.warehouse_success" class="fas fa-check-circle text-green-500 mr-2"></i>
                          <i *ngIf="!result.warehouse_success" class="fas fa-times-circle text-red-500 mr-2"></i>
                          <span class="text-sm font-medium">Message ID: {{ result.message_id }}</span>
                        </div>
                        <div class="text-sm text-gray-600">
                          <span *ngIf="result.apartment_id">Apartment ID: {{ result.apartment_id }}</span>
                          <span *ngIf="result.replaced" class="text-orange-600 ml-2">(Replaced)</span>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <div *ngIf="!batchProcessingResult.success" class="bg-red-50 border border-red-200 rounded-lg p-4">
                    <div class="flex items-center">
                      <i class="fas fa-exclamation-circle text-red-500 mr-2"></i>
                      <span class="text-red-800 font-medium">Batch Processing Failed</span>
                    </div>
                    <p class="text-red-700 text-sm mt-1">{{ batchProcessingResult.error }}</p>
                  </div>
                </div>
              </div>
            </div>

          </div>
        </div>
      </div>
    </div>

    <!-- Apartment Details Modal -->
    <app-apartment-details-modal
      [visible]="showModal"
      [warehouseApartmentIds]="modalWarehouseApartmentIds"
      [warehouseApartments]="modalWarehouseApartments"
      [insertResults]="modalInsertResults"
      [zaloMessages]="modalZaloMessages"
      (close)="closeModal()"
      (apartmentUpdated)="onApartmentUpdated($event)">
    </app-apartment-details-modal>
  `,
  styles: [`
    .fa-spinner {
      animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
      from { transform: rotate(0deg); }
      to { transform: rotate(360deg); }
    }
    
    .max-h-20 {
      max-height: 5rem;
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
    
    /* Button loading animation */
    button:disabled {
      position: relative;
    }
    
    button:disabled::after {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(255, 255, 255, 0.1);
      border-radius: inherit;
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
export class ZaloTestComponent implements OnInit, OnDestroy {
  // Test data
  batchLimit: number = 20;
  rootId: number = 1;
  
  // State
  processing: boolean = false;
  processorStatus: ProcessorStatus | null = null;
  unprocessedMessages: UnprocessedMessage[] = [];
  propertyTree: string | null = null;
  testResult: any = null;
  batchResult: BatchProcessResult | null = null;
  
  // Test inputs
  testMessageId: number | null = null;
  testMessageContent: string = '';
  
  // Batch processing
  selectedMessageIds: number[] = [];
  batchProcessing: boolean = false;
  batchProcessingResult: any = null;
  
  // Message warehouse_id filter
  messageWarehouseIdFilter: string = 'NULL';
  
  // Message sort: newest | oldest
  messageSort: 'newest' | 'oldest' = 'newest';
  
  // Pagination
  currentPage: number = 1;
  pageSize: number = 20;
  totalMessages: number = 0;
  
  // Message-Apartment mapping - REMOVED: No longer caching, always call API
  
  // Loading states for individual messages
  messageLoadingStates: Map<number, boolean> = new Map();
  
  // Modal state
  showModal: boolean = false;
  modalWarehouseApartmentIds: number[] = [];
  modalWarehouseApartments: any[] = [];
  modalInsertResults: any[] = [];
  modalZaloMessages: UnprocessedMessage[] = [];

  // Schedule control
  scheduleControlLoading: boolean = false;
  autoRefreshEnabled: boolean = false;
  private autoRefreshInterval: any = null;

  private apiUrl = `${environment.apiBaseUrl}/api/zalo-test`;

  constructor(private http: HttpClient, private warehouseService: WarehouseService, private zaloTestService: ZaloTestService) {}

  ngOnInit() {
    this.refreshStatus();
    this.loadUnprocessedMessages();
    this.loadPropertyTree();
  }

  ngOnDestroy() {
    this.stopAutoRefresh();
  }

  refreshStatus() {
    this.http.get<ZaloTestResponse>(`${this.apiUrl}/processor-status`).subscribe({
      next: (response: ZaloTestResponse) => {
        if (response.success) {
          this.processorStatus = response.data;
        }
      },
      error: (error: any) => {
        console.error('Error loading processor status:', error);
      }
    });
  }

  startSchedule() {
    if (this.scheduleControlLoading) return;
    
    this.scheduleControlLoading = true;
    this.zaloTestService.startSchedule().subscribe({
      next: (response) => {
        this.scheduleControlLoading = false;
        if (response.success) {
          this.processorStatus = response.data;
          console.log('Schedule started successfully');
        } else {
          alert(response.error || 'Failed to start schedule');
        }
      },
      error: (error) => {
        this.scheduleControlLoading = false;
        console.error('Error starting schedule:', error);
        alert(error.error?.error || 'Failed to start schedule');
      }
    });
  }

  stopSchedule() {
    if (this.scheduleControlLoading) return;
    
    this.scheduleControlLoading = true;
    this.zaloTestService.stopSchedule().subscribe({
      next: (response) => {
        this.scheduleControlLoading = false;
        if (response.success) {
          this.processorStatus = response.data;
          console.log('Schedule stopped successfully');
        } else {
          alert(response.error || 'Failed to stop schedule');
        }
      },
      error: (error) => {
        this.scheduleControlLoading = false;
        console.error('Error stopping schedule:', error);
        alert(error.error?.error || 'Failed to stop schedule');
      }
    });
  }

  toggleAutoRefresh() {
    if (this.autoRefreshEnabled) {
      this.stopAutoRefresh();
    } else {
      this.startAutoRefresh();
    }
  }

  startAutoRefresh() {
    this.autoRefreshEnabled = true;
    // Refresh mỗi 5 giây
    this.autoRefreshInterval = setInterval(() => {
      this.refreshStatus();
    }, 5000);
  }

  stopAutoRefresh() {
    this.autoRefreshEnabled = false;
    if (this.autoRefreshInterval) {
      clearInterval(this.autoRefreshInterval);
      this.autoRefreshInterval = null;
    }
  }

  loadUnprocessedMessages() {
    const offset = (this.currentPage - 1) * this.pageSize;
    this.http.get<ZaloTestResponse & { data: UnprocessedMessage[]; count: number; total: number; limit: number; offset: number; warehouse_id_filter: string; sort: string }>(
      `${this.apiUrl}/messages?limit=${this.pageSize}&offset=${offset}&warehouse_id=${this.messageWarehouseIdFilter}&sort=${this.messageSort}`
    ).subscribe({
      next: (response) => {
        if (response.success) {
          this.unprocessedMessages = response.data;
          // Update total count from API response
          this.totalMessages = response.total || response.data.length;
          // Clear loading states khi load lại messages
          this.messageLoadingStates.clear();
          // Load apartment info sau khi load messages
          this.loadApartmentInfoForMessages();
        }
      },
      error: (error) => {
        console.error('Error loading unprocessed messages:', error);
      }
    });
  }

  loadPropertyTree() {
    this.http.get<ZaloTestResponse & { data: PropertyTreeData }>(`${this.apiUrl}/property-tree?root_id=${this.rootId}`).subscribe({
      next: (response) => {
        if (response.success) {
          this.propertyTree = response.data.property_tree;
        }
      },
      error: (error) => {
        console.error('Error loading property tree:', error);
      }
    });
  }

  /**
   * Xử lý message theo ID (method chung cho cả 2 use cases)
   */
  private processMessageById(messageId: number, options?: { useMessageLoadingState?: boolean, logDetails?: boolean }) {
    const useMessageLoadingState = options?.useMessageLoadingState ?? false;
    const logDetails = options?.logDetails ?? false;

    // Set loading state
    if (useMessageLoadingState) {
      this.messageLoadingStates.set(messageId, true);
    } else {
      this.processing = true;
    }
    this.testResult = null;

    this.zaloTestService.processMessagesBatch([messageId]).subscribe({
      next: (response) => {
        this.testResult = response;
        
        // Clear loading state
        if (useMessageLoadingState) {
          this.messageLoadingStates.set(messageId, false);
        } else {
          this.processing = false;
        }
        
        if (response.success) {
          // Refresh list để cập nhật warehouse_id
          this.loadUnprocessedMessages();
          
          // Xử lý batch mode response structure
          if (response.data?.insert_results && response.data.insert_results.length > 0) {
            const insertResults = response.data.insert_results;
            const successfulResults = insertResults.filter((r: any) => r.warehouse_success && r.apartment_id);
            
            if (successfulResults.length > 0) {
              // Log thông tin chi tiết nếu cần
              if (logDetails) {
                successfulResults.forEach((result: any) => {
                  const isReplaced = result.replaced;
                  const previousWarehouseId = result.previous_warehouse_id;
                  
                  if (isReplaced && previousWarehouseId) {
                    console.log(`🔄 Replaced apartment: ${previousWarehouseId} → ${result.apartment_id}`);
                  } else {
                    console.log(`🆕 Created new apartment: ${result.apartment_id}`);
                  }
                });
              }
              
              // Mở modal với apartment data từ response (nếu có) hoặc IDs
              const apartmentIds = successfulResults.map((r: any) => r.apartment_id);
              const messageIds = successfulResults.map((r: any) => r.message_id);
              const messages = this.unprocessedMessages.filter(msg => messageIds.includes(msg.id));
              
              // Lấy full apartment data từ response nếu có
              const warehouseApartments = response.data?.warehouse_apartments || [];
              
              this.openModalWithResults(apartmentIds, warehouseApartments, successfulResults, messages);
            }
          }
        }
      },
      error: (error) => {
        this.testResult = { success: false, error: error.message };
        
        // Clear loading state on error
        if (useMessageLoadingState) {
          this.messageLoadingStates.set(messageId, false);
        } else {
          this.processing = false;
        }
      }
    });
  }

  /**
   * Test message từ table - dùng messageLoadingState để track từng message riêng
   */
  testByMessageIdFromTable(messageId: number) {
    this.processMessageById(messageId, { 
      useMessageLoadingState: true, 
      logDetails: true 
    });
  }

  /**
   * Test message từ input form - dùng processing state chung
   */
  testByMessageId(messageId?: number) {
    const id = messageId || this.testMessageId;
    if (!id) return;
    
    this.processMessageById(id, { 
      useMessageLoadingState: false, 
      logDetails: false 
    });
  }

  testByMessageContent() {
    if (!this.testMessageContent.trim()) return;

    this.processing = true;
    this.testResult = null;

    this.http.post<ZaloTestResponse>(`${this.apiUrl}/process-message`, { message_content: this.testMessageContent }).subscribe({
      next: (response) => {
        this.testResult = response;
        this.processing = false;
      },
      error: (error) => {
        this.testResult = { success: false, error: error.message };
        this.processing = false;
      }
    });
  }

  batchProcess() {
    this.processing = true;
    this.batchResult = null;

    this.http.post<ZaloTestResponse & { data: BatchProcessResult }>(`${this.apiUrl}/batch-process`, { limit: this.batchLimit }).subscribe({
      next: (response) => {
        if (response.success) {
          this.batchResult = response.data;
        }
        this.processing = false;
        this.loadUnprocessedMessages(); // Refresh list
      },
      error: (error) => {
        console.error('Error in batch processing:', error);
        this.processing = false;
      }
    });
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

  onWarehouseIdFilterChange() {
    this.currentPage = 1; // Reset to first page when filter changes
    this.totalMessages = 0; // Reset total count
    this.loadUnprocessedMessages();
  }

  onMessageSortChange() {
    this.currentPage = 1; // Reset to first page when sort changes
    this.loadUnprocessedMessages();
  }

  onPageSizeChange() {
    this.currentPage = 1; // Reset to first page when page size changes
    this.totalMessages = 0; // Reset total count
    this.loadUnprocessedMessages();
  }

  goToPage(page: number) {
    if (page >= 1 && page <= this.getTotalPages()) {
      this.currentPage = page;
      this.loadUnprocessedMessages();
    }
  }

  getTotalPages(): number {
    if (this.totalMessages === 0) return 1;
    return Math.ceil(this.totalMessages / this.pageSize);
  }

  /** Chuẩn hóa warehouse_ids (API có thể trả về array hoặc chuỗi JSON) thành number[]. */
  getMessageWarehouseIds(message: UnprocessedMessage): number[] {
    const raw = message?.warehouse_ids;
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

  getApartmentForMessage(messageId: number): Apartment | null {
    // No longer using cache - return null, apartment info will be loaded on demand via API
    return null;
  }

  loadApartmentInfoForMessages() {
    // REMOVED: No longer pre-loading apartments, will load on demand via API
    console.log('Apartment info will be loaded on demand via API');
  }


  openModalWithResults(warehouseApartmentIds: number[], warehouseApartments: any[], insertResults: any[], zaloMessages: UnprocessedMessage[]) {
    this.modalWarehouseApartmentIds = warehouseApartmentIds;
    this.modalWarehouseApartments = warehouseApartments;
    this.modalInsertResults = insertResults;
    this.modalZaloMessages = zaloMessages;
    this.showModal = true;
    console.log(`🏠 Opening modal: ${warehouseApartmentIds.length} warehouse apartment IDs, ${warehouseApartments.length} warehouse records, ${insertResults.length} insert results, ${zaloMessages.length} Zalo messages`);
  }

  closeModal() {
    this.showModal = false;
    this.modalWarehouseApartmentIds = [];
    this.modalWarehouseApartments = [];
    this.modalInsertResults = [];
    this.modalZaloMessages = [];
  }

  onApartmentUpdated(event: { apartmentId: number; action: 'approved' | 'deleted' }): void {
    if (event.action === 'deleted') {
      this.loadUnprocessedMessages();
    }
  }

  openDetailModal(messageId: number) {
    const message = this.unprocessedMessages.find(msg => msg.id === messageId);
    const ids = message ? this.getMessageWarehouseIds(message) : [];
    if (message && ids.length) {
      this.openModalWithResults(
        ids,
        [],
        ids.map(apid => ({
          message_id: messageId,
          apartment_id: apid,
          warehouse_success: true
        })),
        [message]
      );
    } else {
      console.error('Message not found or no warehouse_ids:', messageId);
    }
  }

  reloadApartmentInfoForMessage(messageId: number, apartmentId: number) {
    // REMOVED: No longer caching apartment info, will load on demand via API
    console.log(`Apartment info for message ${messageId} will be loaded on demand via API`);
  }

  // Batch Processing Methods
  toggleMessageSelection(messageId: number) {
    const index = this.selectedMessageIds.indexOf(messageId);
    if (index > -1) {
      this.selectedMessageIds.splice(index, 1);
    } else {
      this.selectedMessageIds.push(messageId);
    }
  }

  isMessageSelected(messageId: number): boolean {
    return this.selectedMessageIds.includes(messageId);
  }

  selectAllMessages() {
    this.selectedMessageIds = this.unprocessedMessages.map(msg => msg.id);
  }

  clearSelection() {
    this.selectedMessageIds = [];
  }

  processSelectedMessages() {
    if (this.selectedMessageIds.length === 0) {
      alert('Vui lòng chọn ít nhất một message để xử lý');
      return;
    }

    this.batchProcessing = true;
    this.batchProcessingResult = null;

    this.zaloTestService.processMessagesBatch(this.selectedMessageIds).subscribe({
      next: (response: any) => {
        this.batchProcessing = false;
        this.batchProcessingResult = response;
        
        if (response.success) {
          console.log('Batch processing successful:', response.data);
          
          // Refresh messages list
          this.loadUnprocessedMessages();
          
          // Xử lý batch mode response structure
          if (response.data?.insert_results && response.data.insert_results.length > 0) {
            const insertResults = response.data.insert_results;
            const successfulResults = insertResults.filter((r: any) => r.warehouse_success && r.apartment_id);
            
            if (successfulResults.length > 0) {
              // Log thông tin về successful results
              successfulResults.forEach((result: any) => {
                const isReplaced = result.replaced;
                const previousWarehouseId = result.previous_warehouse_id;
                
                if (isReplaced && previousWarehouseId) {
                  console.log(`🔄 Replaced apartment: ${previousWarehouseId} → ${result.apartment_id}`);
                } else {
                  console.log(`🆕 Created new apartment: ${result.apartment_id}`);
                }
              });
              
              // Mở modal với apartment data từ response (nếu có) hoặc IDs
              const apartmentIds = successfulResults.map((r: any) => r.apartment_id);
              const messageIds = successfulResults.map((r: any) => r.message_id);
              const messages = this.unprocessedMessages.filter(msg => messageIds.includes(msg.id));
              
              // Lấy full apartment data từ response nếu có
              const warehouseApartments = response.data?.warehouse_apartments || [];
              
              console.log(`Opening modal with ${apartmentIds.length} warehouse apartment IDs, ${warehouseApartments.length} warehouse apartment records`);
              this.openModalWithResults(apartmentIds, warehouseApartments, successfulResults, messages);
            }
          }
          
          // Clear selection
          this.clearSelection();
        } else {
          console.error('Batch processing failed:', response.error);
        }
      },
      error: (error: any) => {
        this.batchProcessing = false;
        console.error('Batch processing error:', error);
      }
    });
  }

  getBatchSummary(): string {
    if (!this.batchProcessingResult?.data) return '';
    
    const batchInfo = this.batchProcessingResult.data.batch_info;
    return `Processed: ${batchInfo.processed_count} messages, ${batchInfo.apartment_count} apartments, ${batchInfo.successful_count} successful`;
  }
}