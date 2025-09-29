import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface FacebookPage {
  id: number;
  page_id: string;
  page_name: string;
  page_access_token: string;
  status: boolean;
  created_at: string;
  updated_at: string;
}

export interface FacebookPagesResponse {
  success: boolean;
  data: {
    facebook_pages: FacebookPage[];
    pagination: {
      page: number;
      per_page: number;
      total: number;
      pages: number;
      has_next: boolean;
      has_prev: boolean;
    };
  };
}

export interface FacebookPageDetailResponse {
  success: boolean;
  data: FacebookPage;
}

export interface FacebookPostRequest {
  message: string;
  link?: string;
  image_url?: string;
}

export interface FacebookPostResponse {
  success: boolean;
  message: string;
  data: {
    post_id: string;
    facebook_page_id: string;
    facebook_page_name: string;
    message: string;
    link?: string;
    image_url?: string;
    facebook_response: any;
  };
}

@Injectable({
  providedIn: 'root'
})
export class FacebookService {
  private apiUrl = `${environment.apiBaseUrl}/facebook`;

  constructor(private http: HttpClient) { }

  getFacebookPages(page: number = 1, perPage: number = 10, status?: string): Observable<FacebookPagesResponse> {
    let url = `${this.apiUrl}/pages-advanced?page=${page}&per_page=${perPage}`;
    if (status) {
      url += `&status=${status}`;
    }
    return this.http.get<FacebookPagesResponse>(url);
  }

  getFacebookPage(id: number): Observable<FacebookPageDetailResponse> {
    return this.http.get<FacebookPageDetailResponse>(`${this.apiUrl}/pages/${id}`);
  }

  createFacebookPage(page: { page_id: string; page_name: string; page_access_token: string; status?: boolean }): Observable<any> {
    return this.http.post(`${this.apiUrl}/pages`, page);
  }

  updateFacebookPage(id: number, page: { page_id?: string; page_name?: string; page_access_token?: string; status?: boolean }): Observable<any> {
    return this.http.put(`${this.apiUrl}/pages/${id}`, page);
  }

  deleteFacebookPage(id: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/pages/${id}`);
  }

  toggleFacebookPageStatus(id: number): Observable<any> {
    return this.http.put(`${this.apiUrl}/pages/${id}/toggle-status`, {});
  }

  createFacebookPost(pageId: number, postData: FacebookPostRequest): Observable<FacebookPostResponse> {
    return this.http.post<FacebookPostResponse>(`${this.apiUrl}/pages/${pageId}/post`, postData);
  }

  scheduleFacebookPost(pageId: number, postData: FacebookPostRequest & { scheduled_time: string }): Observable<any> {
    return this.http.post(`${this.apiUrl}/pages/${pageId}/post-schedule`, postData);
  }
} 