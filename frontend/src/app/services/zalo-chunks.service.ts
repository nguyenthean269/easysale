import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface ZaloSession {
  session_id: number;
  total_messages: number;
  processed_messages: number;
  unprocessed_messages: number;
  processing_percentage: number;
}

export interface ChunkStats {
  session_id: number;
  total_messages: number;
  processed_messages: number;
  unprocessed_messages: number;
  total_chunks: number;
  processing_percentage: number;
}

export interface ProcessMessagesRequest {
  session_id: number;
  chunk_size?: number;
}

export interface ProcessMessagesResponse {
  message: string;
  processed_count: number;
  chunks_created: number;
  total_messages: number;
}

export interface SessionsResponse {
  sessions: ZaloSession[];
  total_sessions: number;
}

@Injectable({
  providedIn: 'root'
})
export class ZaloChunksService {
  private apiUrl = environment.apiBaseUrl;

  constructor(private http: HttpClient) {}

  private getHeaders(): HttpHeaders {
    const token = localStorage.getItem('access_token');
    return new HttpHeaders({
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    });
  }

  /**
   * Lấy danh sách các session Zalo có tin nhắn
   */
  getSessions(): Observable<SessionsResponse> {
    return this.http.get<SessionsResponse>(`${this.apiUrl}/zalo-chunks/sessions`, {
      headers: this.getHeaders()
    });
  }

  /**
   * Lấy thống kê về tin nhắn đã xử lý và chưa xử lý
   */
  getStats(sessionId: number): Observable<ChunkStats> {
    return this.http.get<ChunkStats>(`${this.apiUrl}/zalo-chunks/stats?session_id=${sessionId}`, {
      headers: this.getHeaders()
    });
  }

  /**
   * Xử lý chunk nhóm tin nhắn từ zalo_received_messages
   */
  processMessages(request: ProcessMessagesRequest): Observable<ProcessMessagesResponse> {
    return this.http.post<ProcessMessagesResponse>(`${this.apiUrl}/zalo-chunks/process-messages`, request, {
      headers: this.getHeaders()
    });
  }
}
