import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface ZaloTestMessage {
  message_ids?: number[];  // Array of message IDs (required for batch processing)
  message_content?: string;  // Optional: for testing content directly
}

export interface ZaloTestResponse {
  success: boolean;
  data?: any;
  error?: string;
  message?: string;
}

export interface UnprocessedMessage {
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

export interface ProcessorStatus {
  is_running: boolean;
  thread_alive: boolean;
  interval: number;
  interval_minutes: number;
  schedule_enabled: boolean;
  started_at?: string;
}

export interface PropertyTreeData {
  root_id: number;
  property_tree: string;
}

export interface BatchProcessResult {
  processed_count: number;
  error_count: number;
  total_processed: number;
}

@Injectable({
  providedIn: 'root'
})
export class ZaloTestService {
  private apiUrl = `${environment.apiBaseUrl}/api/zalo-test`;

  constructor(private http: HttpClient) {}

  /**
   * Test xử lý batch tin nhắn (chỉ hỗ trợ message_ids array)
   * @deprecated Sử dụng processMessagesBatch() thay thế
   */
  testProcessMessage(data: ZaloTestMessage): Observable<ZaloTestResponse> {
    return this.http.post<ZaloTestResponse>(`${this.apiUrl}/process-message`, data);
  }

  /**
   * Lấy danh sách messages unique theo content_hash với pagination và filter warehouse_id
   */
  getMessages(limit: number = 20, offset: number = 0, warehouse_id: string = 'NULL'): Observable<ZaloTestResponse & { data: UnprocessedMessage[]; count: number; total: number; limit: number; offset: number; warehouse_id_filter: string }> {
    return this.http.get<ZaloTestResponse & { data: UnprocessedMessage[]; count: number; total: number; limit: number; offset: number; warehouse_id_filter: string }>(`${this.apiUrl}/messages?limit=${limit}&offset=${offset}&warehouse_id=${warehouse_id}`);
  }

  /**
   * @deprecated Sử dụng getMessages() thay thế
   * Lấy danh sách tin nhắn theo warehouse_id (backward compatibility)
   */
  getUnprocessedMessages(limit: number = 20, warehouse_id: string = 'NULL'): Observable<ZaloTestResponse & { data: UnprocessedMessage[]; count: number; warehouse_id_filter: string }> {
    return this.http.get<ZaloTestResponse & { data: UnprocessedMessage[]; count: number; warehouse_id_filter: string }>(`${this.apiUrl}/messages?limit=${limit}&offset=0&warehouse_id=${warehouse_id}`);
  }

  /**
   * Lấy trạng thái của Zalo Message Processor
   */
  getProcessorStatus(): Observable<ZaloTestResponse & { data: ProcessorStatus }> {
    return this.http.get<ZaloTestResponse & { data: ProcessorStatus }>(`${this.apiUrl}/processor-status`);
  }

  /**
   * Lấy property tree cho prompt
   */
  getPropertyTree(rootId: number = 1): Observable<ZaloTestResponse & { data: PropertyTreeData }> {
    return this.http.get<ZaloTestResponse & { data: PropertyTreeData }>(`${this.apiUrl}/property-tree?root_id=${rootId}`);
  }

  /**
   * Xử lý batch tin nhắn
   */
  batchProcessMessages(limit: number = 20): Observable<ZaloTestResponse & { data: BatchProcessResult }> {
    return this.http.post<ZaloTestResponse & { data: BatchProcessResult }>(`${this.apiUrl}/batch-process`, { limit });
  }

  /**
   * Xử lý nhiều messages cùng lúc với array message_ids
   * Luôn insert vào warehouse với data_status='REVIEWING' và cập nhật warehouse_id
   */
  processMessagesBatch(messageIds: number[]): Observable<ZaloTestResponse> {
    return this.http.post<ZaloTestResponse>(`${this.apiUrl}/process-message`, { 
      message_ids: messageIds
    });
  }

  /**
   * Bắt đầu schedule
   */
  startSchedule(): Observable<ZaloTestResponse & { data: ProcessorStatus }> {
    return this.http.post<ZaloTestResponse & { data: ProcessorStatus }>(`${this.apiUrl}/schedule/start`, {});
  }

  /**
   * Dừng schedule
   */
  stopSchedule(): Observable<ZaloTestResponse & { data: ProcessorStatus }> {
    return this.http.post<ZaloTestResponse & { data: ProcessorStatus }>(`${this.apiUrl}/schedule/stop`, {});
  }
}
