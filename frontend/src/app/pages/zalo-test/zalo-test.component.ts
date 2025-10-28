import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { WarehouseService, Apartment } from '../../services/warehouse.service';

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
                  <div class="flex gap-2">
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
                  </div>
                </div>
                <div class="p-4">
                  <div *ngIf="unprocessedMessages.length > 0" class="overflow-x-auto">
                    <table class="min-w-full divide-y divide-gray-200">
                      <thead class="bg-gray-50">
                        <tr>
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
            🏠 Apartment Details
          </h3>
          <button (click)="closeModal()" class="text-gray-400 hover:text-gray-600">
            <i class="fas fa-times text-xl"></i>
          </button>
        </div>

        <!-- Modal Body -->
        <div *ngIf="modalApartment && modalMessage" class="mt-4">
          <!-- Two Column Layout -->
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            
            <!-- Column 1: Zalo Message Details -->
            <div class="space-y-4">
              <h4 class="text-lg font-semibold text-blue-900 border-b-2 border-blue-200 pb-2">
                📱 Zalo Message Details
              </h4>
              
              <div class="space-y-3">
                <div class="flex justify-between">
                  <span class="font-medium text-gray-600">Message ID:</span>
                  <span class="text-gray-900 font-mono">{{ modalMessage.id }}</span>
                </div>
                
                <div class="flex justify-between">
                  <span class="font-medium text-gray-600">Session ID:</span>
                  <span class="text-gray-900 font-mono">{{ modalMessage.session_id || 'N/A' }}</span>
                </div>
                
                <div class="flex justify-between">
                  <span class="font-medium text-gray-600">Config ID:</span>
                  <span class="text-gray-900 font-mono">{{ modalMessage.config_id || 'N/A' }}</span>
                </div>
                
                <div class="flex justify-between">
                  <span class="font-medium text-gray-600">Sender ID:</span>
                  <span class="text-gray-900 font-mono">{{ modalMessage.sender_id || 'N/A' }}</span>
                </div>
                
                <div class="flex justify-between">
                  <span class="font-medium text-gray-600">Sender Name:</span>
                  <span class="text-gray-900">{{ modalMessage.sender_name || 'N/A' }}</span>
                </div>
                
                <div class="flex justify-between">
                  <span class="font-medium text-gray-600">Thread ID:</span>
                  <span class="text-gray-900 font-mono">{{ modalMessage.thread_id || 'N/A' }}</span>
                </div>
                
                <div class="flex justify-between">
                  <span class="font-medium text-gray-600">Thread Type:</span>
                  <span class="text-gray-900">{{ modalMessage.thread_type || 'N/A' }}</span>
                </div>
                
                <div class="flex justify-between">
                  <span class="font-medium text-gray-600">Received At:</span>
                  <span class="text-gray-900">{{ modalMessage.received_at | date:'short' }}</span>
                </div>
                
                <div class="flex justify-between">
                  <span class="font-medium text-gray-600">Kafka Status:</span>
                  <span class="px-2 py-1 rounded-full text-xs font-medium"
                        [class]="modalMessage.status_push_kafka === 1 ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'">
                    {{ modalMessage.status_push_kafka === 1 ? 'Pushed' : 'Not Pushed' }}
                  </span>
                </div>
                
                <div class="flex justify-between">
                  <span class="font-medium text-gray-600">Warehouse ID:</span>
                  <span class="text-green-600 font-semibold">{{ modalMessage.warehouse_id || 'NULL' }}</span>
                </div>
              </div>
              
              <!-- Message Content -->
              <div class="mt-4">
                <h5 class="font-medium text-gray-700 mb-2">📝 Message Content:</h5>
                <div class="bg-gray-50 p-3 rounded-lg max-h-40 overflow-y-auto">
                  <p class="text-sm text-gray-800 whitespace-pre-wrap">{{ modalMessage.content }}</p>
                </div>
              </div>
              
              <!-- Additional Message Fields -->
              <div *ngIf="modalMessage.reply_quote || modalMessage.content_hash" class="mt-4 space-y-2">
                <div *ngIf="modalMessage.reply_quote" class="flex justify-between">
                  <span class="font-medium text-gray-600">Reply Quote:</span>
                  <span class="text-gray-900 text-sm">{{ modalMessage.reply_quote }}</span>
                </div>
                
                <div *ngIf="modalMessage.content_hash" class="flex justify-between">
                  <span class="font-medium text-gray-600">Content Hash:</span>
                  <span class="text-gray-900 font-mono text-xs">{{ modalMessage.content_hash }}</span>
                </div>
                
                <div class="flex justify-between">
                  <span class="font-medium text-gray-600">Document Chunks:</span>
                  <span class="px-2 py-1 rounded-full text-xs font-medium"
                        [class]="modalMessage.added_document_chunks ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'">
                    {{ modalMessage.added_document_chunks ? 'Added' : 'Not Added' }}
                  </span>
                </div>
              </div>
            </div>
            
            <!-- Column 2: Warehouse Apartment Details -->
            <div class="space-y-4">
              <h4 class="text-lg font-semibold text-green-900 border-b-2 border-green-200 pb-2">
                🏠 Warehouse Apartment Details
              </h4>
              
              <!-- Basic Information -->
              <div class="space-y-3">
                <h5 class="font-medium text-gray-700 border-b pb-1">Basic Information</h5>
                
                <div class="flex justify-between">
                  <span class="font-medium text-gray-600">Apartment ID:</span>
                  <span class="text-gray-900 font-mono">{{ modalApartment.id }}</span>
                </div>
                
                <div class="flex justify-between">
                  <span class="font-medium text-gray-600">Property Group:</span>
                  <span class="text-gray-900">{{ modalApartment.property_group_name || 'N/A' }}</span>
                </div>
                
                <div class="flex justify-between">
                  <span class="font-medium text-gray-600">Unit Code:</span>
                  <span class="text-gray-900 font-mono">{{ modalApartment.unit_code || 'N/A' }}</span>
                </div>
                
                <div class="flex justify-between">
                  <span class="font-medium text-gray-600">Unit Type:</span>
                  <span class="text-gray-900">{{ modalApartment.unit_type_name || 'N/A' }}</span>
                </div>
                
                <div class="flex justify-between">
                  <span class="font-medium text-gray-600">Floor:</span>
                  <span class="text-gray-900">{{ modalApartment.unit_floor_number || 'N/A' }}</span>
                </div>
                
                <div class="flex justify-between">
                  <span class="font-medium text-gray-600">Unit Axis:</span>
                  <span class="text-gray-900">{{ modalApartment.unit_axis || 'N/A' }}</span>
                </div>
              </div>
              
              <!-- Area Information -->
              <div class="space-y-3">
                <h5 class="font-medium text-gray-700 border-b pb-1">Area Information</h5>
                
                <div class="flex justify-between">
                  <span class="font-medium text-gray-600">Gross Area:</span>
                  <span class="text-gray-900">{{ formatArea(modalApartment.area_gross) }}</span>
                </div>
                
                <div class="flex justify-between">
                  <span class="font-medium text-gray-600">Net Area:</span>
                  <span class="text-gray-900">{{ formatArea(modalApartment.area_net) }}</span>
                </div>
                
                <div class="flex justify-between">
                  <span class="font-medium text-gray-600">Construction Area:</span>
                  <span class="text-gray-900">{{ formatArea(modalApartment.area_construction) }}</span>
                </div>
                
                <div class="flex justify-between">
                  <span class="font-medium text-gray-600">Land Area:</span>
                  <span class="text-gray-900">{{ formatArea(modalApartment.area_land) }}</span>
                </div>
              </div>
              
              <!-- Pricing Information -->
              <div class="space-y-3">
                <h5 class="font-medium text-gray-700 border-b pb-1">Pricing Information</h5>
                
                <div class="flex justify-between">
                  <span class="font-medium text-gray-600">Price:</span>
                  <span class="text-green-600 font-semibold">{{ formatPrice(modalApartment.price) }}</span>
                </div>
                
                <div class="flex justify-between">
                  <span class="font-medium text-gray-600">Early Price:</span>
                  <span class="text-blue-600">{{ formatPrice(modalApartment.price_early) }}</span>
                </div>
                
                <div class="flex justify-between">
                  <span class="font-medium text-gray-600">Schedule Price:</span>
                  <span class="text-purple-600">{{ formatPrice(modalApartment.price_schedule) }}</span>
                </div>
                
                <div class="flex justify-between">
                  <span class="font-medium text-gray-600">Loan Price:</span>
                  <span class="text-orange-600">{{ formatPrice(modalApartment.price_loan) }}</span>
                </div>
                
                <div class="flex justify-between">
                  <span class="font-medium text-gray-600">Rent Price:</span>
                  <span class="text-red-600">{{ formatPrice(modalApartment.price_rent) }}</span>
                </div>
              </div>
              
              <!-- Room & Features -->
              <div class="space-y-3">
                <h5 class="font-medium text-gray-700 border-b pb-1">Rooms & Features</h5>
                
                <div class="flex justify-between">
                  <span class="font-medium text-gray-600">Bedrooms:</span>
                  <span class="text-gray-900">{{ modalApartment.num_bedrooms || 'N/A' }}</span>
                </div>
                
                <div class="flex justify-between">
                  <span class="font-medium text-gray-600">Bathrooms:</span>
                  <span class="text-gray-900">{{ modalApartment.num_bathrooms || 'N/A' }}</span>
                </div>
                
                <div class="flex justify-between">
                  <span class="font-medium text-gray-600">View Type:</span>
                  <span class="text-gray-900">{{ modalApartment.type_view || 'N/A' }}</span>
                </div>
                
                <div class="flex justify-between">
                  <span class="font-medium text-gray-600">Door Direction:</span>
                  <span class="text-gray-900">{{ modalApartment.direction_door || 'N/A' }}</span>
                </div>
                
                <div class="flex justify-between">
                  <span class="font-medium text-gray-600">Balcony Direction:</span>
                  <span class="text-gray-900">{{ modalApartment.direction_balcony || 'N/A' }}</span>
                </div>
              </div>
              
              <!-- Status & Notes -->
              <div class="space-y-3">
                <h5 class="font-medium text-gray-700 border-b pb-1">Status & Notes</h5>
                
                <div class="flex justify-between">
                  <span class="font-medium text-gray-600">Status:</span>
                  <span class="px-2 py-1 rounded-full text-xs font-medium"
                        [class]="modalApartment.status === 'available' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'">
                    {{ modalApartment.status || 'N/A' }}
                  </span>
                </div>
                
                <div class="flex justify-between">
                  <span class="font-medium text-gray-600">Allocation:</span>
                  <span class="text-gray-900">{{ modalApartment.unit_allocation || 'N/A' }}</span>
                </div>
                
                <div *ngIf="modalApartment.notes" class="mt-3">
                  <span class="font-medium text-gray-600 block mb-1">Notes:</span>
                  <p class="text-sm text-gray-700 bg-gray-50 p-2 rounded">{{ modalApartment.notes }}</p>
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
  
  // Message warehouse_id filter
  messageWarehouseIdFilter: string = 'NULL';
  
  // Message-Apartment mapping
  messageApartmentMap: Map<number, Apartment> = new Map();
  
  // Loading states for individual messages
  messageLoadingStates: Map<number, boolean> = new Map();
  
  // Modal state
  showModal: boolean = false;
  modalApartment: Apartment | null = null;
  modalMessageId: number | null = null;
  modalMessage: UnprocessedMessage | null = null;

  private apiUrl = `${environment.apiBaseUrl}/api/zalo-test`;

  constructor(private http: HttpClient, private warehouseService: WarehouseService) {}

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
      message_id: messageId, 
      real_insert: true 
    }).subscribe({
      next: (response) => {
        this.testResult = response;
        this.messageLoadingStates.set(messageId, false);
        
        if (response.success) {
          // Refresh list để cập nhật warehouse_id
          this.loadUnprocessedMessages();
          
          // Nếu có apartment_id từ warehouse insert, cập nhật mapping
          if (response.data?.apartment_id) {
            const isReplaced = response.data.replaced;
            const previousWarehouseId = response.data.previous_warehouse_id;
            
            if (isReplaced && previousWarehouseId) {
              console.log(`🔄 Replaced apartment: ${previousWarehouseId} → ${response.data.apartment_id}`);
              // Xóa mapping cũ nếu có
              this.messageApartmentMap.delete(messageId);
            } else {
              console.log(`🆕 Created new apartment: ${response.data.apartment_id}`);
            }
            
            // Cập nhật mapping cho message này
            this.updateApartmentMapping(messageId, response.data.apartment_id);
            
            // Sau khi cập nhật mapping, reload apartment info cho message này
            setTimeout(() => {
              this.reloadApartmentInfoForMessage(messageId, response.data.apartment_id);
            }, 500);
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
          
          // Mở modal để hiển thị apartment vừa được map
          this.openApartmentModal(messageId, apartment);
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
    this.modalMessage = this.unprocessedMessages.find(msg => msg.id === messageId) || null;
    this.showModal = true;
    console.log(`🏠 Opening modal for message ${messageId}, apartment ${apartment.id}`);
  }

  closeModal() {
    this.showModal = false;
    this.modalApartment = null;
    this.modalMessageId = null;
    this.modalMessage = null;
  }

  openDetailModal(messageId: number) {
    // Tìm apartment từ mapping hoặc load từ API
    const existingApartment = this.messageApartmentMap.get(messageId);
    
    if (existingApartment) {
      // Nếu đã có trong mapping, mở modal ngay
      this.openApartmentModal(messageId, existingApartment);
    } else {
      // Nếu chưa có trong mapping, load từ API
      const message = this.unprocessedMessages.find(msg => msg.id === messageId);
      if (message && message.warehouse_id) {
        this.warehouseService.getApartmentsByIds([message.warehouse_id]).subscribe({
          next: (response) => {
            if (response.success && response.data.length > 0) {
              const apartment = response.data[0];
              // Cập nhật mapping và mở modal
              this.messageApartmentMap.set(messageId, apartment);
              this.openApartmentModal(messageId, apartment);
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
}