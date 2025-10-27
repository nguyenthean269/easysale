import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ZaloChunksService, ZaloSession, ChunkStats, ProcessMessagesRequest, ProcessMessagesResponse } from '../../services/zalo-chunks.service';

// Interfaces are now imported from service

@Component({
  selector: 'app-zalo-chunks',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="container-fluid">
      <div class="row">
        <div class="col-12">
          <div class="card">
            <div class="card-header">
              <h3 class="card-title">
                <i class="fas fa-comments me-2"></i>
                Quản lý Chunk Tin nhắn Zalo
              </h3>
            </div>
            <div class="card-body">
              <!-- Session Selection -->
              <div class="row mb-4">
                <div class="col-md-6">
                  <label for="sessionSelect" class="form-label">Chọn Session Zalo:</label>
                  <select 
                    id="sessionSelect" 
                    class="form-select" 
                    [(ngModel)]="selectedSessionId"
                    (change)="onSessionChange()"
                    [disabled]="isProcessing">
                    <option value="">-- Chọn session --</option>
                    <option 
                      *ngFor="let session of sessions" 
                      [value]="session.session_id">
                      Session {{ session.session_id }} 
                      ({{ session.total_messages }} tin nhắn, 
                      {{ session.processing_percentage }}% đã xử lý)
                    </option>
                  </select>
                </div>
                <div class="col-md-6">
                  <label for="chunkSize" class="form-label">Kích thước chunk:</label>
                  <input 
                    type="number" 
                    id="chunkSize" 
                    class="form-control" 
                    [(ngModel)]="chunkSize"
                    min="10" 
                    max="100" 
                    [disabled]="isProcessing">
                </div>
              </div>

              <!-- Statistics -->
              <div class="row mb-4" *ngIf="stats">
                <div class="col-md-3">
                  <div class="card bg-primary text-white">
                    <div class="card-body">
                      <div class="d-flex justify-content-between">
                        <div>
                          <h4 class="mb-0">{{ stats.total_messages }}</h4>
                          <p class="mb-0">Tổng tin nhắn</p>
                        </div>
                        <div class="align-self-center">
                          <i class="fas fa-comments fa-2x"></i>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                <div class="col-md-3">
                  <div class="card bg-success text-white">
                    <div class="card-body">
                      <div class="d-flex justify-content-between">
                        <div>
                          <h4 class="mb-0">{{ stats.processed_messages }}</h4>
                          <p class="mb-0">Đã xử lý</p>
                        </div>
                        <div class="align-self-center">
                          <i class="fas fa-check-circle fa-2x"></i>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                <div class="col-md-3">
                  <div class="card bg-warning text-white">
                    <div class="card-body">
                      <div class="d-flex justify-content-between">
                        <div>
                          <h4 class="mb-0">{{ stats.unprocessed_messages }}</h4>
                          <p class="mb-0">Chưa xử lý</p>
                        </div>
                        <div class="align-self-center">
                          <i class="fas fa-clock fa-2x"></i>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                <div class="col-md-3">
                  <div class="card bg-info text-white">
                    <div class="card-body">
                      <div class="d-flex justify-content-between">
                        <div>
                          <h4 class="mb-0">{{ stats.total_chunks }}</h4>
                          <p class="mb-0">Chunks đã tạo</p>
                        </div>
                        <div class="align-self-center">
                          <i class="fas fa-cubes fa-2x"></i>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Progress Bar -->
              <div class="mb-4" *ngIf="stats">
                <label class="form-label">Tiến độ xử lý:</label>
                <div class="progress">
                  <div 
                    class="progress-bar" 
                    [class]="getProgressBarClass()"
                    [style.width.%]="stats.processing_percentage"
                    role="progressbar">
                    {{ stats.processing_percentage }}%
                  </div>
                </div>
              </div>

              <!-- Action Buttons -->
              <div class="row mb-4">
                <div class="col-12">
                  <button 
                    class="btn btn-primary me-2" 
                    (click)="processMessages()"
                    [disabled]="!selectedSessionId || isProcessing">
                    <i class="fas fa-play me-1" *ngIf="!isProcessing"></i>
                    <i class="fas fa-spinner fa-spin me-1" *ngIf="isProcessing"></i>
                    {{ isProcessing ? 'Đang xử lý...' : 'Xử lý Tin nhắn' }}
                  </button>
                  
                  <button 
                    class="btn btn-info me-2" 
                    (click)="refreshStats()"
                    [disabled]="isProcessing">
                    <i class="fas fa-sync-alt me-1"></i>
                    Làm mới
                  </button>
                  
                  <button 
                    class="btn btn-secondary" 
                    (click)="loadSessions()"
                    [disabled]="isProcessing">
                    <i class="fas fa-list me-1"></i>
                    Tải lại Sessions
                  </button>
                </div>
              </div>

              <!-- Results -->
              <div class="alert alert-success" *ngIf="lastResult">
                <h5><i class="fas fa-check-circle me-2"></i>Kết quả xử lý</h5>
                <p><strong>Tin nhắn đã xử lý:</strong> {{ lastResult.processed_count }}</p>
                <p><strong>Chunks đã tạo:</strong> {{ lastResult.chunks_created }}</p>
                <p><strong>Tổng tin nhắn:</strong> {{ lastResult.total_messages }}</p>
              </div>

              <!-- Error Messages -->
              <div class="alert alert-danger" *ngIf="errorMessage">
                <h5><i class="fas fa-exclamation-triangle me-2"></i>Lỗi</h5>
                <p>{{ errorMessage }}</p>
              </div>

              <!-- Sessions List -->
              <div class="card mt-4" *ngIf="sessions.length > 0">
                <div class="card-header">
                  <h5 class="card-title">Danh sách Sessions</h5>
                </div>
                <div class="card-body">
                  <div class="table-responsive">
                    <table class="table table-striped">
                      <thead>
                        <tr>
                          <th>Session ID</th>
                          <th>Tổng tin nhắn</th>
                          <th>Đã xử lý</th>
                          <th>Chưa xử lý</th>
                          <th>Tiến độ</th>
                          <th>Thao tác</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr *ngFor="let session of sessions">
                          <td>{{ session.session_id }}</td>
                          <td>{{ session.total_messages }}</td>
                          <td>{{ session.processed_messages }}</td>
                          <td>{{ session.unprocessed_messages }}</td>
                          <td>
                            <div class="progress" style="height: 20px;">
                              <div 
                                class="progress-bar" 
                                [class]="getProgressBarClass(session.processing_percentage)"
                                [style.width.%]="session.processing_percentage">
                                {{ session.processing_percentage }}%
                              </div>
                            </div>
                          </td>
                          <td>
                            <button 
                              class="btn btn-sm btn-primary"
                              (click)="selectSession(session.session_id)"
                              [disabled]="isProcessing">
                              Chọn
                            </button>
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .card {
      box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
      border: 1px solid rgba(0, 0, 0, 0.125);
    }
    
    .progress {
      height: 1.5rem;
    }
    
    .table th {
      background-color: #f8f9fa;
      border-top: none;
    }
    
    .btn {
      border-radius: 0.375rem;
    }
    
    .alert {
      border-radius: 0.5rem;
    }
  `]
})
export class ZaloChunksComponent implements OnInit {
  sessions: ZaloSession[] = [];
  selectedSessionId: number | null = null;
  chunkSize: number = 50;
  stats: ChunkStats | null = null;
  lastResult: ProcessMessagesResponse | null = null;
  errorMessage: string = '';
  isProcessing: boolean = false;

  constructor(private zaloChunksService: ZaloChunksService) {}

  ngOnInit(): void {
    this.loadSessions();
  }

  loadSessions(): void {
    this.zaloChunksService.getSessions().subscribe({
      next: (response) => {
        this.sessions = response.sessions;
        this.errorMessage = '';
      },
      error: (error) => {
        this.errorMessage = 'Lỗi khi tải danh sách sessions: ' + (error.error?.error || error.message);
        console.error('Error loading sessions:', error);
      }
    });
  }

  onSessionChange(): void {
    if (this.selectedSessionId) {
      this.refreshStats();
    } else {
      this.stats = null;
    }
  }

  selectSession(sessionId: number): void {
    this.selectedSessionId = sessionId;
    this.refreshStats();
  }

  refreshStats(): void {
    if (!this.selectedSessionId) return;

    this.zaloChunksService.getStats(this.selectedSessionId).subscribe({
      next: (response) => {
        this.stats = response;
        this.errorMessage = '';
      },
      error: (error) => {
        this.errorMessage = 'Lỗi khi tải thống kê: ' + (error.error?.error || error.message);
        console.error('Error loading stats:', error);
      }
    });
  }

  processMessages(): void {
    if (!this.selectedSessionId || this.isProcessing) return;

    this.isProcessing = true;
    this.errorMessage = '';
    this.lastResult = null;

    const requestData: ProcessMessagesRequest = {
      session_id: this.selectedSessionId,
      chunk_size: this.chunkSize
    };

    this.zaloChunksService.processMessages(requestData).subscribe({
      next: (response) => {
        this.lastResult = response;
        this.isProcessing = false;
        this.refreshStats(); // Refresh stats after processing
        this.loadSessions(); // Refresh sessions list
      },
      error: (error) => {
        this.errorMessage = 'Lỗi khi xử lý tin nhắn: ' + (error.error?.error || error.message);
        this.isProcessing = false;
        console.error('Error processing messages:', error);
      }
    });
  }

  getProgressBarClass(percentage?: number): string {
    const pct = percentage || this.stats?.processing_percentage || 0;
    if (pct === 100) return 'bg-success';
    if (pct >= 75) return 'bg-info';
    if (pct >= 50) return 'bg-warning';
    return 'bg-danger';
  }

  // Headers are now handled by the service
}
