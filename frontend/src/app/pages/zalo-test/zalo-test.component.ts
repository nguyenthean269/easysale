import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

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
  content: string;
  created_at: string;
  status: string;
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

interface TestResult {
  message_id: number;
  message_content: string;
  parsed_data?: ParsedApartmentData;
  warehouse_success?: boolean;
  error?: string;
  timestamp: string;
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

            <!-- Unprocessed Messages -->
            <div class="mb-6">
              <div class="bg-white rounded-lg border border-gray-200">
                <div class="px-4 py-3 border-b border-gray-200 flex justify-between items-center">
                  <h5 class="text-lg font-semibold text-gray-800">Unprocessed Messages ({{ unprocessedMessages.length }})</h5>
                  <button class="bg-gray-600 hover:bg-gray-700 text-white px-3 py-1 rounded text-sm font-medium transition-colors" 
                          (click)="loadUnprocessedMessages()">
                    <i class="fas fa-refresh mr-1"></i> Refresh
                  </button>
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
                          <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                        </tr>
                      </thead>
                      <tbody class="bg-white divide-y divide-gray-200">
                        <tr *ngFor="let message of unprocessedMessages" class="hover:bg-gray-50">
                          <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{{ message.id }}</td>
                          <td class="px-6 py-4 text-sm text-gray-500 max-w-xs truncate">{{ message.content }}</td>
                          <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ message.created_at | date:'short' }}</td>
                          <td class="px-6 py-4 whitespace-nowrap">
                            <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                              {{ message.status }}
                            </span>
                          </td>
                          <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                            <button class="text-blue-600 hover:text-blue-900 mr-3" (click)="testByMessageId(message.id)">
                              <i class="fas fa-play"></i> Test
                            </button>
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

            <!-- Test Results History -->
            <div class="mb-6">
              <div class="bg-white rounded-lg border border-gray-200">
                <div class="px-4 py-3 border-b border-gray-200 flex justify-between items-center">
                  <h5 class="text-lg font-semibold text-gray-800">
                    <i class="fas fa-history mr-2 text-blue-600"></i>
                    Test Results History ({{ testResults.length }})
                  </h5>
                  <button class="bg-red-600 hover:bg-red-700 text-white px-3 py-1 rounded text-sm font-medium transition-colors" 
                          (click)="clearTestResults()" 
                          [disabled]="testResults.length === 0">
                    <i class="fas fa-trash mr-1"></i> Clear All
                  </button>
                </div>
                <div class="p-4">
                  <div *ngIf="testResults.length > 0" class="overflow-x-auto">
                    <table class="min-w-full divide-y divide-gray-200">
                      <thead class="bg-gray-50">
                        <tr>
                          <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Time</th>
                          <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Message</th>
                          <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Parsed Data</th>
                          <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Warehouse</th>
                          <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                        </tr>
                      </thead>
                      <tbody class="bg-white divide-y divide-gray-200">
                        <tr *ngFor="let result of testResults" class="hover:bg-gray-50">
                          <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {{ result.timestamp | date:'short' }}
                          </td>
                          <td class="px-6 py-4 text-sm text-gray-900">
                            <div>
                              <span class="font-medium">ID:</span> {{ result.message_id || 'Custom' }}<br>
                              <span class="text-gray-500">{{ result.message_content | slice:0:80 }}{{ result.message_content.length > 80 ? '...' : '' }}</span>
                            </div>
                          </td>
                          <td class="px-6 py-4 text-sm text-gray-900">
                            <div *ngIf="result.parsed_data" class="space-y-1">
                              <div class="grid grid-cols-2 gap-2 text-xs">
                                <div>
                                  <span class="font-medium">Property:</span> {{ result.parsed_data.property_group || 'N/A' }}<br>
                                  <span class="font-medium">Unit:</span> {{ result.parsed_data.unit_code || 'N/A' }}<br>
                                  <span class="font-medium">Floor:</span> {{ result.parsed_data.unit_floor_number || 'N/A' }}<br>
                                  <span class="font-medium">Area:</span> {{ formatArea(result.parsed_data.area_gross) }}
                                </div>
                                <div>
                                  <span class="font-medium">Bedrooms:</span> {{ result.parsed_data.num_bedrooms || 'N/A' }}<br>
                                  <span class="font-medium">Type:</span> {{ result.parsed_data.unit_type || 'N/A' }}<br>
                                  <span class="font-medium">Direction:</span> {{ result.parsed_data.direction_door || 'N/A' }}<br>
                                  <span class="font-medium">Price:</span> {{ formatPrice(result.parsed_data.price) }}
                                </div>
                              </div>
                              <div *ngIf="result.parsed_data.notes" class="mt-2">
                                <span class="text-blue-600 font-medium">Notes:</span> {{ result.parsed_data.notes }}
                              </div>
                            </div>
                            <div *ngIf="!result.parsed_data" class="text-gray-500 text-xs">
                              No parsed data
                            </div>
                          </td>
                          <td class="px-6 py-4 whitespace-nowrap">
                            <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium" 
                                  [ngClass]="result.warehouse_success ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'">
                              {{ result.warehouse_success ? 'Success' : 'Failed' }}
                            </span>
                          </td>
                          <td class="px-6 py-4 whitespace-nowrap">
                            <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium" 
                                  [ngClass]="result.error ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'">
                              {{ result.error ? 'Error' : 'Success' }}
                            </span>
                            <div *ngIf="result.error" class="mt-1">
                              <span class="text-red-600 text-xs">{{ result.error }}</span>
                            </div>
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                  <div *ngIf="testResults.length === 0" class="text-center py-8 text-gray-500">
                    <i class="fas fa-inbox text-4xl mb-2"></i>
                    <p>No test results yet. Start testing messages to see results here.</p>
                  </div>
                </div>
              </div>
            </div>

            <!-- Current Test Result -->
            <div *ngIf="testResult" class="mb-6">
              <div class="bg-white rounded-lg border border-gray-200">
                <div class="px-4 py-3 border-b border-gray-200">
                  <h5 class="text-lg font-semibold text-gray-800">Current Test Result</h5>
                </div>
                <div class="p-4">
                  <div class="mb-4">
                    <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium" 
                          [ngClass]="testResult.success ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'">
                      {{ testResult.success ? 'Success' : 'Error' }}
                    </span>
                  </div>
                  <pre *ngIf="testResult.data" class="bg-gray-50 p-4 rounded-lg text-sm overflow-x-auto">{{ testResult.data | json }}</pre>
                </div>
              </div>
            </div>

          </div>
        </div>
      </div>
    </div>
  `,
  styles: []
})
export class ZaloTestComponent implements OnInit {
  // Test data
  testMessageId: number | null = null;
  testMessageContent: string = '';
  batchLimit: number = 20;
  rootId: number = 1;
  
  // State
  processing: boolean = false;
  processorStatus: ProcessorStatus | null = null;
  unprocessedMessages: UnprocessedMessage[] = [];
  propertyTree: string | null = null;
  testResult: any = null;
  batchResult: BatchProcessResult | null = null;
  testResults: TestResult[] = []; // Lưu lịch sử test results

  private apiUrl = `${environment.apiBaseUrl}/api/zalo-test`;

  constructor(private http: HttpClient) {}

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
    this.http.get<ZaloTestResponse & { data: UnprocessedMessage[]; count: number }>(`${this.apiUrl}/unprocessed-messages?limit=50`).subscribe({
      next: (response) => {
        if (response.success) {
          this.unprocessedMessages = response.data;
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

  testByMessageId(messageId?: number) {
    const id = messageId || this.testMessageId;
    if (!id) return;

    this.processing = true;
    this.testResult = null;

    this.http.post<ZaloTestResponse>(`${this.apiUrl}/process-message`, { message_id: id }).subscribe({
      next: (response) => {
        this.testResult = response;
        this.processing = false;
        
        // Lưu kết quả vào testResults
        const testResult: TestResult = {
          message_id: id,
          message_content: this.unprocessedMessages.find(m => m.id === id)?.content || 'Unknown',
          parsed_data: response.data?.parsed_data,
          warehouse_success: response.data?.warehouse_success,
          error: response.error,
          timestamp: new Date().toISOString()
        };
        this.testResults.unshift(testResult); // Thêm vào đầu array
        
        if (response.success) {
          this.loadUnprocessedMessages(); // Refresh list
        }
      },
      error: (error) => {
        this.testResult = { success: false, error: error.message };
        this.processing = false;
        
        // Lưu lỗi vào testResults
        const testResult: TestResult = {
          message_id: id,
          message_content: this.unprocessedMessages.find(m => m.id === id)?.content || 'Unknown',
          error: error.message,
          timestamp: new Date().toISOString()
        };
        this.testResults.unshift(testResult);
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
        
        // Lưu kết quả vào testResults
        const testResult: TestResult = {
          message_id: 0, // Custom message không có ID
          message_content: this.testMessageContent,
          parsed_data: response.data?.parsed_data,
          warehouse_success: response.data?.warehouse_success,
          error: response.error,
          timestamp: new Date().toISOString()
        };
        this.testResults.unshift(testResult);
      },
      error: (error) => {
        this.testResult = { success: false, error: error.message };
        this.processing = false;
        
        // Lưu lỗi vào testResults
        const testResult: TestResult = {
          message_id: 0,
          message_content: this.testMessageContent,
          error: error.message,
          timestamp: new Date().toISOString()
        };
        this.testResults.unshift(testResult);
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

  clearTestResults() {
    this.testResults = [];
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