import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface CrawlRequest {
  link: string;
  crawl_tool?: 'firecrawl' | 'watercrawl';
}

export interface CrawlResponse {
  message: string;
  crawl_id: number;
  document_id: number;
  link: string;
  crawl_tool: string;
  started_at: string;
  done_at: string;
  content_length: number;
  chunks_processed: number;
  milvus_inserts: {
    successful: number;
    failed: number;
    total: number;
  };
}

export interface Document {
  id: number;
  user_id: number;
  category_id: number;
  title: string;
  source_type: string;
  source_path: string;
  created_at: string;
  updated_at: string;
}

export interface DocumentChunk {
  id: number;
  document_id: number;
  chunk_index: number;
  content: string;
  milvus_id: string | null;
  created_at: string;
}

export interface SearchRequest {
  query: string;
  top_k?: number;
  document_ids?: number[];
}

export interface SearchResult {
  chunk_id: number;
  document_id: number;
  document_title: string;
  chunk_index: number;
  content: string;
  similarity_score: number;
  source_path: string;
}

@Injectable({
  providedIn: 'root'
})
export class DocumentService {
  private apiUrl = environment.apiBaseUrl;

  constructor(private http: HttpClient) {}

  // Crawl API
  createCrawl(crawlRequest: CrawlRequest): Observable<CrawlResponse> {
    return this.http.post<CrawlResponse>(`${this.apiUrl}/user/crawls`, crawlRequest);
  }

  getCrawls(): Observable<{ message: string; crawls: any[] }> {
    return this.http.get<{ message: string; crawls: any[] }>(`${this.apiUrl}/user/crawls`);
  }

  getCrawlDetail(crawlId: number): Observable<{ message: string; crawl: any }> {
    return this.http.get<{ message: string; crawl: any }>(`${this.apiUrl}/user/crawls/${crawlId}`);
  }

  // Document API
  getDocuments(): Observable<{ message: string; documents: Document[] }> {
    return this.http.get<{ message: string; documents: Document[] }>(`${this.apiUrl}/user/documents`);
  }

  getDocumentDetail(documentId: number): Observable<{
    message: string;
    document: Document;
    chunks_count: number;
    chunks: DocumentChunk[];
  }> {
    return this.http.get<{
      message: string;
      document: Document;
      chunks_count: number;
      chunks: DocumentChunk[];
    }>(`${this.apiUrl}/user/documents/${documentId}`);
  }

  deleteDocument(documentId: number): Observable<{
    message: string;
    document_id: number;
    chunks_deleted: number;
    milvus_deletion: {
      successful: number;
      failed: number;
      total: number;
    };
  }> {
    return this.http.delete<{
      message: string;
      document_id: number;
      chunks_deleted: number;
      milvus_deletion: {
        successful: number;
        failed: number;
        total: number;
      };
    }>(`${this.apiUrl}/user/documents/${documentId}`);
  }

  retryMilvusInserts(documentId: number): Observable<{
    message: string;
    document_id: number;
    retry_results: {
      successful: number;
      failed: number;
    };
  }> {
    return this.http.post<{
      message: string;
      document_id: number;
      retry_results: {
        successful: number;
        failed: number;
      };
    }>(`${this.apiUrl}/user/documents/${documentId}/retry-milvus`, {});
  }

  // Search API
  searchDocuments(searchRequest: SearchRequest): Observable<{
    message: string;
    query: string;
    total_results: number;
    results: SearchResult[];
  }> {
    return this.http.post<{
      message: string;
      query: string;
      total_results: number;
      results: SearchResult[];
    }>(`${this.apiUrl}/user/search`, searchRequest);
  }
} 