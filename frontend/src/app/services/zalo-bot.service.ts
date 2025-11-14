import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface ZaloConfig {
  id: number;
  name: string;
  imei: string;
  is_default: boolean;
  created_at?: string;
  status: string;
  running: boolean;
}

export interface BotStatus {
  config_id: number;
  running: boolean;
  status: string;
  stats: {
    start_time?: string;
    messages_received: number;
    messages_sent: number;
    last_message_time?: string;
  };
}

export interface Message {
  type: string;
  sender: string;
  content: string;
  time: string;
}

export interface SentMessage {
  id: number;
  recipient_id: string;
  recipient_name: string;
  content: string;
  status: string;
  sent_at?: string;
  media_url?: string;
  media_type?: string;
}

export interface ApiResponse<T = any> {
  success: boolean;
  message?: string;
  data?: T;
  error?: string;
}

export interface ConfigsResponse extends ApiResponse {
  configs?: ZaloConfig[];
}

export interface ConfigResponse extends ApiResponse {
  config?: ZaloConfig;
}

export interface BotStatusResponse extends ApiResponse {
  data?: BotStatus;
}

export interface MessagesResponse extends ApiResponse {
  messages?: Message[];
}

export interface SentMessagesResponse extends ApiResponse {
  messages?: SentMessage[];
  total?: number;
}

export interface AllStatusResponse extends ApiResponse {
  data?: { [key: number]: BotStatus };
}

@Injectable({
  providedIn: 'root'
})
export class ZaloBotService {
  private apiUrl = `${environment.apiBaseUrl}/api/zalo-bot`;

  constructor(private http: HttpClient) {}

  private getHeaders(): HttpHeaders {
    const token = localStorage.getItem('access_token');
    return new HttpHeaders({
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    });
  }

  /**
   * Lấy danh sách tất cả configs
   */
  getConfigs(): Observable<ConfigsResponse> {
    return this.http.get<ConfigsResponse>(`${this.apiUrl}/configs`, {
      headers: this.getHeaders()
    });
  }

  /**
   * Lấy thông tin config cụ thể
   */
  getConfig(configId: number): Observable<ConfigResponse> {
    return this.http.get<ConfigResponse>(`${this.apiUrl}/config/${configId}`, {
      headers: this.getHeaders()
    });
  }

  /**
   * Khởi động bot cho config_id cụ thể
   */
  startBot(configId: number): Observable<ApiResponse> {
    return this.http.post<ApiResponse>(`${this.apiUrl}/start/${configId}`, {}, {
      headers: this.getHeaders()
    });
  }

  /**
   * Dừng bot cho config_id cụ thể
   */
  stopBot(configId: number): Observable<ApiResponse> {
    return this.http.post<ApiResponse>(`${this.apiUrl}/stop/${configId}`, {}, {
      headers: this.getHeaders()
    });
  }

  /**
   * Cleanup bot cho config_id cụ thể
   */
  cleanupBot(configId: number): Observable<ApiResponse> {
    return this.http.post<ApiResponse>(`${this.apiUrl}/cleanup/${configId}`, {}, {
      headers: this.getHeaders()
    });
  }

  /**
   * Lấy trạng thái bot cho config_id cụ thể
   */
  getBotStatus(configId: number): Observable<BotStatusResponse> {
    return this.http.get<BotStatusResponse>(`${this.apiUrl}/status/${configId}`, {
      headers: this.getHeaders()
    });
  }

  /**
   * Lấy tin nhắn gần đây cho config_id cụ thể
   */
  getBotMessages(configId: number): Observable<MessagesResponse> {
    return this.http.get<MessagesResponse>(`${this.apiUrl}/messages/${configId}`, {
      headers: this.getHeaders()
    });
  }

  /**
   * Khởi động tất cả bots
   */
  startAllBots(): Observable<ApiResponse> {
    return this.http.post<ApiResponse>(`${this.apiUrl}/start`, {}, {
      headers: this.getHeaders()
    });
  }

  /**
   * Dừng tất cả bots
   */
  stopAllBots(): Observable<ApiResponse> {
    return this.http.post<ApiResponse>(`${this.apiUrl}/stop`, {}, {
      headers: this.getHeaders()
    });
  }

  /**
   * Lấy trạng thái tất cả bots
   */
  getAllStatus(): Observable<AllStatusResponse> {
    return this.http.get<AllStatusResponse>(`${this.apiUrl}/status`, {
      headers: this.getHeaders()
    });
  }

  /**
   * Gửi tin nhắn từ bot config_id
   */
  sendMessage(configId: number, recipientId: string, content: string, threadType: 'USER' | 'GROUP' = 'USER'): Observable<ApiResponse> {
    return this.http.post<ApiResponse>(`${this.apiUrl}/send/${configId}`, {
      recipient_id: recipientId,
      content: content,
      thread_type: threadType
    }, {
      headers: this.getHeaders()
    });
  }

  /**
   * Gửi nhiều tin nhắn cùng lúc
   */
  sendBulkMessages(configId: number, messages: Array<{ recipient_id: string; content: string; thread_type?: 'USER' | 'GROUP' }>): Observable<ApiResponse> {
    return this.http.post<ApiResponse>(`${this.apiUrl}/send_bulk/${configId}`, {
      messages: messages
    }, {
      headers: this.getHeaders()
    });
  }

  /**
   * Lấy danh sách tin nhắn đã gửi của config_id
   */
  getSentMessages(configId: number): Observable<SentMessagesResponse> {
    return this.http.get<SentMessagesResponse>(`${this.apiUrl}/messages_sent/${configId}`, {
      headers: this.getHeaders()
    });
  }
}

