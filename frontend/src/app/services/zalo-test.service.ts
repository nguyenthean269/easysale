import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface ZaloTestMessage {
  message_id?: number;
  message_content?: string;
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
   * Test xử lý một tin nhắn cụ thể
   */
  testProcessMessage(data: ZaloTestMessage): Observable<ZaloTestResponse> {
    return this.http.post<ZaloTestResponse>(`${this.apiUrl}/process-message`, data);
  }

  /**
   * Lấy danh sách tin nhắn theo warehouse_id
   */
  getUnprocessedMessages(limit: number = 20, warehouse_id: string = 'NULL'): Observable<ZaloTestResponse & { data: UnprocessedMessage[]; count: number; warehouse_id_filter: string }> {
    return this.http.get<ZaloTestResponse & { data: UnprocessedMessage[]; count: number; warehouse_id_filter: string }>(`${this.apiUrl}/unprocessed-messages?limit=${limit}&warehouse_id=${warehouse_id}`);
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
   */
  processMessagesBatch(messageIds: number[], realInsert: boolean = false): Observable<ZaloTestResponse> {
    return this.http.post<ZaloTestResponse>(`${this.apiUrl}/process-message`, { 
      message_ids: messageIds, 
      real_insert: realInsert 
    });
  }
}
