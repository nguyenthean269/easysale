import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface Post {
  id: number;
  title: string;
  content: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface PostsResponse {
  success: boolean;
  data: {
    posts: Post[];
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

@Injectable({
  providedIn: 'root'
})
export class PostService {
  private apiUrl = `${environment.apiBaseUrl}/posts`;

  constructor(private http: HttpClient) { }

  getPosts(page: number = 1, perPage: number = 10): Observable<PostsResponse> {
    return this.http.get<PostsResponse>(`${this.apiUrl}?page=${page}&per_page=${perPage}`);
  }

  getPost(id: number): Observable<{ success: boolean; data: Post }> {
    return this.http.get<{ success: boolean; data: Post }>(`${this.apiUrl}/${id}`);
  }

  createPost(post: { title: string; content: string; status?: string }): Observable<{ success: boolean; data: Post }> {
    return this.http.post<{ success: boolean; data: Post }>(`${this.apiUrl}`, post);
  }

  updatePost(id: number, post: { title?: string; content?: string; status?: string }): Observable<{ success: boolean; data: Post }> {
    return this.http.put<{ success: boolean; data: Post }>(`${this.apiUrl}/${id}`, post);
  }

  deletePost(id: number): Observable<{ success: boolean; message: string }> {
    return this.http.delete<{ success: boolean; message: string }>(`${this.apiUrl}/${id}`);
  }
}

