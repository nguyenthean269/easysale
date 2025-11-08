import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { WarehouseService, Apartment } from '../../services/warehouse.service';
import { ZaloTestService } from '../../services/zalo-test.service';

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
  warehouse_id?: number;
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
  imports: [CommonModule, FormsModule],
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
                  <h5 class="text-lg font-semibold text-gray-800 mb-4">Processor Status</h5>
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
                  <button class="mt-4 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors" 
                          (click)="refreshStatus()">
                    <i class="fas fa-refresh mr-1"></i> Refresh Status
                  </button>
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
                      <div class="mt-2 flex items-center">
                        <input type="checkbox" 
                               [(ngModel)]="realInsert" 
                               id="realInsert"
                               class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded">
                        <label for="realInsert" class="ml-2 text-sm text-gray-700">
                          Real Insert (update warehouse_id to database)
                        </label>
                      </div>
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
                  <h5 class="text-lg font-semibold text-gray-800">Messages ({{ unprocessedMessages.length }})</h5>
                  <div class="flex gap-2 items-center">
                    <select [(ngModel)]="messageWarehouseIdFilter" 
                            (change)="onWarehouseIdFilterChange()"
                            class="px-3 py-1 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
                      <option value="NULL">Chưa push vào Warehouse</option>
                      <option value="NOT_NULL">Đã push vào Warehouse</option>
                      <option value="ALL">Tất cả Messages</option>
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
                            <span *ngIf="message.warehouse_id" class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                              Warehouse ID: {{ message.warehouse_id }}
                            </span>
                            <span *ngIf="!message.warehouse_id" class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
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
                              <div class="text-gray-300">Debug: {{ messageApartmentMap.size }} mapped</div>
                              <div class="text-gray-300">Warehouse ID: {{ message.warehouse_id || 'NULL' }}</div>
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
                              
                              <!-- Detail Button (only show if has warehouse_id) -->
                              <button *ngIf="message.warehouse_id" 
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
                    
                    <div *ngIf="batchProcessingResult.data?.results" class="space-y-2">
                      <h6 class="font-medium text-gray-700">Individual Results:</h6>
                      <div *ngFor="let result of batchProcessingResult.data.results" 
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
    <div *ngIf="showModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50 modal-backdrop" (click)="closeModal()">
      <div class="relative top-10 mx-auto p-5 border w-11/12 md:w-5/6 lg:w-4/5 xl:w-3/4 shadow-lg rounded-md bg-white modal-content" (click)="$event.stopPropagation()">
        <!-- Modal Header -->
        <div class="flex justify-between items-center pb-3 border-b">
          <h3 class="text-lg font-semibold text-gray-900">
            🏠 Apartment Details {{ modalApartments.length > 1 ? '(' + modalApartments.length + ')' : '' }}
          </h3>
          <button (click)="closeModal()" class="text-gray-400 hover:text-gray-600">
            <i class="fas fa-times text-xl"></i>
          </button>
        </div>

        <!-- Modal Body -->
        <!-- Multiple Apartments Mode (always use this mode) -->
        <div *ngIf="modalApartments.length > 0 && modalMessages.length > 0" class="mt-4">
          <div class="space-y-6">
            <div *ngFor="let apartment of modalApartments; let i = index" class="border border-gray-200 rounded-lg p-4">
              <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                
                <!-- Column 1: Zalo Message Details -->
                <div class="space-y-4">
                  <h4 class="text-lg font-semibold text-blue-900 border-b-2 border-blue-200 pb-2">
                    📱 Message {{ i + 1 }} (ID: {{ getMessageForApartment(apartment)?.id || 'N/A' }})
                  </h4>
                  
                  <div *ngIf="getMessageForApartment(apartment) as message" class="space-y-3">
                    <div class="flex justify-between">
                      <span class="font-medium text-gray-600">Message ID:</span>
                      <span class="text-gray-900 font-mono">{{ message.id }}</span>
                    </div>
                    
                    <div class="flex justify-between">
                      <span class="font-medium text-gray-600">Warehouse ID:</span>
                      <span class="text-green-600 font-semibold">{{ message.warehouse_id || 'NULL' }}</span>
                    </div>
                    
                    <div class="flex justify-between">
                      <span class="font-medium text-gray-600">Received At:</span>
                      <span class="text-gray-900">{{ message.received_at | date:'short' }}</span>
                    </div>
                    
                    <!-- Message Content -->
                    <div class="mt-4">
                      <h5 class="font-medium text-gray-700 mb-2">📝 Message Content:</h5>
                      <div class="bg-gray-50 p-3 rounded-lg max-h-40 overflow-y-auto">
                        <p class="text-sm text-gray-800 whitespace-pre-wrap">{{ message.content }}</p>
                      </div>
                    </div>
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
          <button (click)="closeModal()" 
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
export class ZaloTestComponent implements OnInit {
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
  realInsert: boolean = false;
  
  // Batch processing
  selectedMessageIds: number[] = [];
  batchProcessing: boolean = false;
  batchProcessingResult: any = null;
  
  // Message warehouse_id filter
  messageWarehouseIdFilter: string = 'NULL';
  
  // Message-Apartment mapping
  messageApartmentMap: Map<number, Apartment> = new Map();
  
  // Loading states for individual messages
  messageLoadingStates: Map<number, boolean> = new Map();
  
  // Modal state
  showModal: boolean = false;
  modalApartment: Apartment | null = null;
  modalApartments: Apartment[] = []; // List apartments for batch mode
  modalMessageId: number | null = null;
  modalMessage: UnprocessedMessage | null = null;
  modalMessages: UnprocessedMessage[] = []; // List messages for batch mode

  private apiUrl = `${environment.apiBaseUrl}/api/zalo-test`;

  constructor(private http: HttpClient, private warehouseService: WarehouseService, private zaloTestService: ZaloTestService) {}

  ngOnInit() {
    this.refreshStatus();
    this.loadUnprocessedMessages();
    this.loadPropertyTree();
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

  loadUnprocessedMessages() {
    this.http.get<ZaloTestResponse & { data: UnprocessedMessage[]; count: number; warehouse_id_filter: string }>(`${this.apiUrl}/unprocessed-messages?limit=50&warehouse_id=${this.messageWarehouseIdFilter}`).subscribe({
      next: (response) => {
        if (response.success) {
          this.unprocessedMessages = response.data;
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

  testByMessageIdFromTable(messageId: number) {
    // Test từ table - luôn sử dụng real_insert = true để cập nhật warehouse_id
    this.messageLoadingStates.set(messageId, true);
    this.testResult = null;

    this.http.post<ZaloTestResponse>(`${this.apiUrl}/process-message`, { 
      message_ids: [messageId], 
      real_insert: true 
    }).subscribe({
      next: (response) => {
        this.testResult = response;
        this.messageLoadingStates.set(messageId, false);
        
        if (response.success) {
          // Refresh list để cập nhật warehouse_id
          this.loadUnprocessedMessages();
          
          // Xử lý batch mode response structure (vì dùng message_ids array)
          if (response.data?.results && response.data.results.length > 0) {
            const results = response.data.results;
            const successfulResults = results.filter((r: any) => r.warehouse_success && r.apartment_id);
            
            if (successfulResults.length > 0) {
              // Cập nhật mappings cho tất cả successful results
              successfulResults.forEach((result: any) => {
                const isReplaced = result.replaced;
                const previousWarehouseId = result.previous_warehouse_id;
                
                if (isReplaced && previousWarehouseId) {
                  console.log(`🔄 Replaced apartment: ${previousWarehouseId} → ${result.apartment_id}`);
                  this.messageApartmentMap.delete(result.message_id);
                } else {
                  console.log(`🆕 Created new apartment: ${result.apartment_id}`);
                }
              });
              
              // Load tất cả apartments và mở modal
              const apartmentIds = successfulResults.map((r: any) => r.apartment_id);
              this.warehouseService.getApartmentsByIds(apartmentIds).subscribe({
                next: (apartmentResponse) => {
                  if (apartmentResponse.success && apartmentResponse.data.length > 0) {
                    // Cập nhật mappings
                    apartmentResponse.data.forEach(apartment => {
                      const result = successfulResults.find((r: any) => r.apartment_id === apartment.id);
                      if (result) {
                        this.messageApartmentMap.set(result.message_id, apartment);
                      }
                    });
                    
                    // Lấy messages tương ứng
                    const messageIds = successfulResults.map((r: any) => r.message_id);
                    const messages = this.unprocessedMessages.filter(msg => messageIds.includes(msg.id));
                    
                    // Mở modal với tất cả apartments và messages
                    this.openBatchModal(successfulResults, apartmentResponse.data, messages);
                  }
                },
                error: (error) => {
                  console.error('Error loading apartments for modal:', error);
                  // Fallback: mở modal với apartment đầu tiên
                  if (successfulResults.length > 0) {
                    this.updateApartmentMapping(successfulResults[0].message_id, successfulResults[0].apartment_id);
                  }
                }
              });
            }
          } else if (response.data?.apartment_id) {
            // Fallback: xử lý single mode response structure (nếu backend trả về single mode)
            const isReplaced = response.data.replaced;
            const previousWarehouseId = response.data.previous_warehouse_id;
            
            if (isReplaced && previousWarehouseId) {
              console.log(`🔄 Replaced apartment: ${previousWarehouseId} → ${response.data.apartment_id}`);
              // Xóa mapping cũ nếu có
              this.messageApartmentMap.delete(messageId);
            } else {
              console.log(`🆕 Created new apartment: ${response.data.apartment_id}`);
            }
            
            // Cập nhật mapping cho message này (sẽ tự động mở popup)
            this.updateApartmentMapping(messageId, response.data.apartment_id);
          }
        }
      },
      error: (error) => {
        this.testResult = { success: false, error: error.message };
        this.messageLoadingStates.set(messageId, false);
      }
    });
  }

  testByMessageId(messageId?: number) {
    const id = messageId || this.testMessageId;
    if (!id) return;

    this.processing = true;
    this.testResult = null;

    this.http.post<ZaloTestResponse>(`${this.apiUrl}/process-message`, { 
      message_id: id, 
      real_insert: this.realInsert 
    }).subscribe({
      next: (response) => {
        this.testResult = response;
        this.processing = false;
        
        if (response.success) {
          // Refresh list để cập nhật warehouse_id
          this.loadUnprocessedMessages();
          
          // Nếu có apartment_id từ warehouse insert, cập nhật mapping
          if (response.data?.apartment_id) {
            console.log(`Processing successful for message ${id}, apartment_id: ${response.data.apartment_id}`);
            
            // Cập nhật mapping cho message này
            this.updateApartmentMapping(id, response.data.apartment_id);
            
            // Sau khi cập nhật mapping, reload apartment info cho message này
            setTimeout(() => {
              this.reloadApartmentInfoForMessage(id, response.data.apartment_id);
            }, 500);
          }
        }
      },
      error: (error) => {
        this.testResult = { success: false, error: error.message };
        this.processing = false;
      }
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
    this.loadUnprocessedMessages();
  }

  getApartmentForMessage(messageId: number): Apartment | null {
    // Chỉ tìm từ mapping
    const apartment = this.messageApartmentMap.get(messageId) || null;
    console.log(`Getting apartment for message ${messageId}:`, apartment);
    return apartment;
  }

  loadApartmentInfoForMessages() {
    console.log('Loading apartment info for messages...');
    console.log('Current messages:', this.unprocessedMessages.length);
    
    // Lấy các messages đã có warehouse_id
    const messagesWithWarehouseId = this.unprocessedMessages.filter(msg => 
      msg.warehouse_id !== null && msg.warehouse_id !== undefined
    );
    console.log('Messages with warehouse_id:', messagesWithWarehouseId.length);
    
    if (messagesWithWarehouseId.length === 0) {
      console.log('No messages with warehouse_id to load apartments for');
      return;
    }
    
    // Lấy danh sách warehouse_id để gọi API
    const warehouseIds = messagesWithWarehouseId.map(msg => msg.warehouse_id).filter(id => id !== null && id !== undefined);
    console.log('Warehouse IDs to load:', warehouseIds);
    
    if (warehouseIds.length > 0) {
      // Gọi API warehouse để lấy thông tin apartments
      this.warehouseService.getApartmentsByIds(warehouseIds).subscribe({
        next: (response) => {
          if (response.success && response.data.length > 0) {
            console.log('Loaded apartments:', response.data.length);
            
            // Tạo mapping từ warehouse_id sang apartment
            const apartmentMap = new Map();
            response.data.forEach(apartment => {
              apartmentMap.set(apartment.id, apartment);
            });
            
            // Cập nhật messageApartmentMap
            messagesWithWarehouseId.forEach(message => {
              if (message.warehouse_id && apartmentMap.has(message.warehouse_id)) {
                this.messageApartmentMap.set(message.id, apartmentMap.get(message.warehouse_id));
                console.log(`Mapped message ${message.id} -> apartment ${message.warehouse_id}`);
              }
            });
            
            console.log('Total mappings created:', this.messageApartmentMap.size);
          } else {
            console.log('No apartments found for warehouse IDs');
          }
        },
        error: (error) => {
          console.error('Error loading apartments:', error);
        }
      });
    }
  }


  updateApartmentMapping(messageId: number, apartmentId: number) {
    // Load apartment từ API và cập nhật mapping
    this.warehouseService.getApartmentsByIds([apartmentId]).subscribe({
      next: (response) => {
        if (response.success && response.data.length > 0) {
          const apartment = response.data[0];
          this.messageApartmentMap.set(messageId, apartment);
          console.log(`Updated mapping: message ${messageId} -> apartment ${apartmentId}`);
          
          // Luôn mở modal ở batch mode (ngay cả với 1 apartment)
          const message = this.unprocessedMessages.find(msg => msg.id === messageId) || null;
          this.openBatchModal([{ message_id: messageId, apartment_id: apartmentId }], [apartment], message ? [message] : []);
        }
      },
      error: (error) => {
        console.error('Error loading apartment for mapping:', error);
      }
    });
  }

  openApartmentModal(messageId: number, apartment: Apartment) {
    this.modalMessageId = messageId;
    this.modalApartment = apartment;
    this.modalApartments = []; // Clear batch mode
    this.modalMessage = this.unprocessedMessages.find(msg => msg.id === messageId) || null;
    this.modalMessages = []; // Clear batch mode
    this.showModal = true;
    console.log(`🏠 Opening modal for message ${messageId}, apartment ${apartment.id}`);
  }

  openBatchModal(results: any[], apartments: Apartment[], messages: UnprocessedMessage[]) {
    this.modalMessageId = null;
    this.modalApartment = null;
    this.modalApartments = apartments;
    this.modalMessage = null;
    this.modalMessages = messages;
    this.showModal = true;
    console.log(`🏠 Opening batch modal with ${apartments.length} apartments, ${messages.length} messages`);
  }

  getMessageForApartment(apartment: Apartment): UnprocessedMessage | null {
    // Tìm message từ modalMessages dựa trên apartment.id
    for (const message of this.modalMessages) {
      if (message.warehouse_id === apartment.id) {
        return message;
      }
    }
    // Fallback: tìm từ messageApartmentMap
    for (const [messageId, mappedApartment] of this.messageApartmentMap.entries()) {
      if (mappedApartment.id === apartment.id) {
        return this.modalMessages.find(msg => msg.id === messageId) || 
               this.unprocessedMessages.find(msg => msg.id === messageId) || null;
      }
    }
    return null;
  }

  closeModal() {
    this.showModal = false;
    this.modalApartment = null;
    this.modalApartments = [];
    this.modalMessageId = null;
    this.modalMessage = null;
    this.modalMessages = [];
  }

  openDetailModal(messageId: number) {
    // Tìm apartment từ mapping hoặc load từ API
    const existingApartment = this.messageApartmentMap.get(messageId);
    
    if (existingApartment) {
      // Nếu đã có trong mapping, mở modal ngay ở batch mode
      const message = this.unprocessedMessages.find(msg => msg.id === messageId) || null;
      this.openBatchModal([{ message_id: messageId, apartment_id: existingApartment.id }], [existingApartment], message ? [message] : []);
    } else {
      // Nếu chưa có trong mapping, load từ API
      const message = this.unprocessedMessages.find(msg => msg.id === messageId);
      if (message && message.warehouse_id) {
        this.warehouseService.getApartmentsByIds([message.warehouse_id]).subscribe({
          next: (response) => {
            if (response.success && response.data.length > 0) {
              const apartment = response.data[0];
              // Cập nhật mapping và mở modal ở batch mode
              this.messageApartmentMap.set(messageId, apartment);
              this.openBatchModal([{ message_id: messageId, apartment_id: apartment.id }], [apartment], message ? [message] : []);
            } else {
              console.error('No apartment found for warehouse_id:', message.warehouse_id);
            }
          },
          error: (error) => {
            console.error('Error loading apartment for detail modal:', error);
          }
        });
      }
    }
  }

  reloadApartmentInfoForMessage(messageId: number, apartmentId: number) {
    console.log(`Reloading apartment info for message ${messageId}, apartment ${apartmentId}`);
    
    // Gọi API warehouse để lấy thông tin apartment mới
    this.warehouseService.getApartmentsByIds([apartmentId]).subscribe({
      next: (response) => {
        if (response.success && response.data.length > 0) {
          const apartment = response.data[0];
          
          // Cập nhật mapping
          this.messageApartmentMap.set(messageId, apartment);
          
          console.log(`Updated apartment mapping for message ${messageId}:`, apartment);
          
          // Trigger change detection để UI cập nhật
          // Angular sẽ tự động detect thay đổi trong Map
        } else {
          console.log(`No apartment found for ID ${apartmentId}`);
        }
      },
      error: (error) => {
        console.error('Error reloading apartment info:', error);
      }
    });
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

    this.zaloTestService.processMessagesBatch(this.selectedMessageIds, this.realInsert).subscribe({
      next: (response: any) => {
        this.batchProcessing = false;
        this.batchProcessingResult = response;
        
        if (response.success) {
          console.log('Batch processing successful:', response.data);
          
          // Refresh messages list
          this.loadUnprocessedMessages();
          
          // Xử lý batch mode response structure
          if (response.data?.results && response.data.results.length > 0) {
            const results = response.data.results;
            const successfulResults = results.filter((r: any) => r.warehouse_success && r.apartment_id);
            
            if (successfulResults.length > 0) {
              // Cập nhật mappings cho tất cả successful results
              successfulResults.forEach((result: any) => {
                const isReplaced = result.replaced;
                const previousWarehouseId = result.previous_warehouse_id;
                
                if (isReplaced && previousWarehouseId) {
                  console.log(`🔄 Replaced apartment: ${previousWarehouseId} → ${result.apartment_id}`);
                  this.messageApartmentMap.delete(result.message_id);
                } else {
                  console.log(`🆕 Created new apartment: ${result.apartment_id}`);
                }
              });
              
              // Gom tất cả apartment_id và gọi API một lần
              const apartmentIds = successfulResults.map((r: any) => r.apartment_id);
              console.log(`Loading ${apartmentIds.length} apartments with IDs:`, apartmentIds);
              
              this.warehouseService.getApartmentsByIds(apartmentIds).subscribe({
                next: (apartmentResponse) => {
                  if (apartmentResponse.success && apartmentResponse.data.length > 0) {
                    // Cập nhật mappings
                    apartmentResponse.data.forEach(apartment => {
                      const result = successfulResults.find((r: any) => r.apartment_id === apartment.id);
                      if (result) {
                        this.messageApartmentMap.set(result.message_id, apartment);
                      }
                    });
                    
                    // Lấy messages tương ứng
                    const messageIds = successfulResults.map((r: any) => r.message_id);
                    const messages = this.unprocessedMessages.filter(msg => messageIds.includes(msg.id));
                    
                    // Mở modal với tất cả apartments và messages
                    this.openBatchModal(successfulResults, apartmentResponse.data, messages);
                  }
                },
                error: (error) => {
                  console.error('Error loading apartments for modal:', error);
                  // Fallback: mở modal với apartment đầu tiên
                  if (successfulResults.length > 0) {
                    this.updateApartmentMapping(successfulResults[0].message_id, successfulResults[0].apartment_id);
                  }
                }
              });
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