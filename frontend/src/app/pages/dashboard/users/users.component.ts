import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { NzTableModule } from 'ng-zorro-antd/table';
import { NzButtonModule } from 'ng-zorro-antd/button';
import { NzSpaceModule } from 'ng-zorro-antd/space';
import { NzTabsModule } from 'ng-zorro-antd/tabs';
import { NzInputModule } from 'ng-zorro-antd/input';
import { NzFormModule } from 'ng-zorro-antd/form';
import { NzModalModule } from 'ng-zorro-antd/modal';
import { NzMessageModule, NzMessageService } from 'ng-zorro-antd/message';
import { NzSpinModule } from 'ng-zorro-antd/spin';
import { NzCardModule } from 'ng-zorro-antd/card';
import { NzTagModule } from 'ng-zorro-antd/tag';
import { NzPopconfirmModule } from 'ng-zorro-antd/popconfirm';
import { NzSelectModule } from 'ng-zorro-antd/select';
import { NzInputNumberModule } from 'ng-zorro-antd/input-number';
import { ReactiveFormsModule, FormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { DocumentService, Document, CrawlRequest, SearchRequest, SearchResult } from '../../../services/document.service';

@Component({
  selector: 'app-users',
  standalone: true,
  imports: [
    CommonModule, 
    NzTableModule, 
    NzButtonModule, 
    NzSpaceModule,
    NzTabsModule,
    NzInputModule,
    NzFormModule,
    NzModalModule,
    NzMessageModule,
    NzSpinModule,
    NzCardModule,
    NzTagModule,
    NzPopconfirmModule,
    NzSelectModule,
    NzInputNumberModule,
    ReactiveFormsModule,
    FormsModule
  ],
  template: `
    <div class="p-6">
      <div class="bg-white p-6 rounded-lg shadow-sm">
        <div class="space-y-6">
          <div class="flex items-center justify-between">
            <h1 class="text-2xl font-semibold text-gray-800">Document & Crawl Management</h1>
          </div>
      
      <nz-tabset>
        <!-- Documents Tab -->
        <nz-tab nzTitle="Documents">
          <div class="space-y-4">
            <div class="flex justify-between items-center">
              <div class="flex space-x-2">
                <input 
                  nz-input 
                  placeholder="Search documents..." 
                  [(ngModel)]="documentSearchQuery"
                  (input)="searchDocuments()"
                  class="w-64"
                />
              </div>
                             <button nz-button nzType="primary" disabled>
                 Add Document
               </button>
            </div>
            
            <nz-spin [nzSpinning]="documentsLoading">
              <nz-table 
                #documentsTable 
                [nzData]="documents"
                [nzPageSize]="10"
                [nzShowSizeChanger]="true"
                [nzShowQuickJumper]="true"
                [nzShowTotal]="documentsTotalTemplate">
                
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Title</th>
                    <th>Source Type</th>
                    <th>Source Path</th>
                    <th>Created At</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr *ngFor="let doc of documentsTable.data">
                    <td>{{ doc.id }}</td>
                    <td>{{ doc.title }}</td>
                    <td>
                      <nz-tag [nzColor]="doc.source_type === 'web' ? 'blue' : 'green'">
                        {{ doc.source_type }}
                      </nz-tag>
                    </td>
                    <td>
                      <a [href]="doc.source_path" target="_blank" class="text-blue-600 hover:text-blue-800">
                        {{ doc.source_path }}
                      </a>
                    </td>
                    <td>{{ doc.created_at | date:'short' }}</td>
                    <td>
                      <nz-space>
                        <button nz-button nzType="link" nzSize="small" (click)="viewDocumentDetail(doc)">
                          View
                        </button>
                        <button nz-button nzType="link" nzSize="small" (click)="retryMilvus(doc.id)">
                          Retry Milvus
                        </button>
                        <button 
                          nz-button 
                          nzType="link" 
                          nzDanger 
                          nzSize="small"
                          nz-popconfirm
                          nzPopconfirmTitle="Are you sure you want to delete this document?"
                          (nzOnConfirm)="deleteDocument(doc.id)">
                          Delete
                        </button>
                      </nz-space>
                    </td>
                  </tr>
                </tbody>
              </nz-table>
            </nz-spin>
            
            <ng-template #documentsTotalTemplate let-total>Total {{ total }} documents</ng-template>
          </div>
        </nz-tab>

        <!-- Crawl Tab -->
        <nz-tab nzTitle="Crawl">
          <div class="space-y-4">
            <nz-card title="Create New Crawl">
              <form [formGroup]="crawlForm" (ngSubmit)="createCrawl()">
                <div class="space-y-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">URL to Crawl</label>
                    <input 
                      nz-input 
                      formControlName="link"
                      placeholder="https://example.com"
                      class="w-full"
                    />
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Crawl Tool</label>
                    <nz-select formControlName="crawl_tool" class="w-full">
                      <nz-option nzValue="firecrawl" nzLabel="Firecrawl"></nz-option>
                      <nz-option nzValue="watercrawl" nzLabel="Watercrawl"></nz-option>
                    </nz-select>
                  </div>
                  <button 
                    nz-button 
                    nzType="primary" 
                    type="submit"
                    [disabled]="crawlForm.invalid || crawlLoading"
                    [nzLoading]="crawlLoading">
                    Start Crawl
                  </button>
                </div>
              </form>
            </nz-card>

            <nz-spin [nzSpinning]="crawlsLoading">
              <nz-table 
                #crawlsTable 
                [nzData]="crawls"
                [nzPageSize]="10"
                [nzShowSizeChanger]="true"
                [nzShowQuickJumper]="true"
                [nzShowTotal]="crawlsTotalTemplate">
                
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Link</th>
                    <th>Tool</th>
                    <th>Started At</th>
                    <th>Done At</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr *ngFor="let crawl of crawlsTable.data">
                    <td>{{ crawl.id }}</td>
                    <td>
                      <a [href]="crawl.link" target="_blank" class="text-blue-600 hover:text-blue-800">
                        {{ crawl.link }}
                      </a>
                    </td>
                    <td>
                      <nz-tag [nzColor]="crawl.crawl_tool === 'firecrawl' ? 'red' : 'blue'">
                        {{ crawl.crawl_tool }}
                      </nz-tag>
                    </td>
                    <td>{{ crawl.started_at | date:'short' }}</td>
                    <td>{{ crawl.done_at | date:'short' }}</td>
                    <td>
                      <nz-space>
                        <button nz-button nzType="link" nzSize="small" (click)="viewCrawlDetail(crawl)">
                          View
                        </button>
                        <button nz-button nzType="link" nzSize="small" (click)="editCrawlContent(crawl)">
                          Edit
                        </button>
                        <button nz-button nzType="link" nzSize="small" (click)="recrawlContent(crawl.id)">
                          Recrawl
                        </button>
                      </nz-space>
                    </td>
                  </tr>
                </tbody>
              </nz-table>
            </nz-spin>
            
            <ng-template #crawlsTotalTemplate let-total>Total {{ total }} crawls</ng-template>
          </div>
        </nz-tab>

        <!-- Search Tab -->
        <nz-tab nzTitle="Search">
          <div class="space-y-4">
            <nz-card title="Vector Search">
              <form [formGroup]="searchForm" (ngSubmit)="performSearch()">
                <div class="space-y-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Search Query</label>
                    <input 
                      nz-input 
                      formControlName="query"
                      placeholder="Enter your search query..."
                      class="w-full"
                    />
                  </div>
                  <div class="grid grid-cols-2 gap-4">
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-2">Top K Results</label>
                      <nz-input-number 
                        formControlName="top_k"
                        [nzMin]="1"
                        [nzMax]="20"
                        class="w-full">
                      </nz-input-number>
                    </div>
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-2">Filter by Document IDs</label>
                      <input 
                        nz-input 
                        formControlName="document_ids"
                        placeholder="1,2,3 (comma separated)"
                        class="w-full"
                      />
                    </div>
                  </div>
                  <button 
                    nz-button 
                    nzType="primary" 
                    type="submit"
                    [disabled]="searchForm.invalid || searchLoading"
                    [nzLoading]="searchLoading">
                    Search
                  </button>
                </div>
              </form>
            </nz-card>

            <nz-spin [nzSpinning]="searchLoading">
              <div *ngIf="searchResults.length > 0" class="space-y-4">
                <h3 class="text-lg font-semibold">Search Results ({{ searchResults.length }})</h3>
                <div *ngFor="let result of searchResults" class="border rounded-lg p-4">
                  <div class="flex justify-between items-start mb-2">
                    <h4 class="font-medium text-blue-600">{{ result.document_title }}</h4>
                    <nz-tag [nzColor]="'green'">Score: {{ (result.similarity_score * 100).toFixed(1) }}%</nz-tag>
                  </div>
                  <p class="text-sm text-gray-600 mb-2">Chunk {{ result.chunk_index }} | Source: {{ result.source_path }}</p>
                  <p class="text-gray-800">{{ result.content }}</p>
                </div>
              </div>
            </nz-spin>
          </div>
        </nz-tab>
      </nz-tabset>
    </div>

    <!-- Document Detail Modal -->
    <nz-modal 
      [(nzVisible)]="documentDetailVisible" 
      nzTitle="Document Detail"
      [nzWidth]="800"
      (nzOnCancel)="documentDetailVisible = false">
      <div *nzModalContent>
        <div *ngIf="selectedDocument" class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="font-medium">Title:</label>
              <p>{{ selectedDocument.title }}</p>
            </div>
            <div>
              <label class="font-medium">Source Type:</label>
              <p>{{ selectedDocument.source_type }}</p>
            </div>
            <div>
              <label class="font-medium">Source Path:</label>
              <a [href]="selectedDocument.source_path" target="_blank" class="text-blue-600">
                {{ selectedDocument.source_path }}
              </a>
            </div>
            <div>
              <label class="font-medium">Created At:</label>
              <p>{{ selectedDocument.created_at | date:'full' }}</p>
            </div>
          </div>
          
          <div *ngIf="documentChunks.length > 0">
            <h4 class="font-medium mb-2">Chunks ({{ documentChunks.length }})</h4>
            <div class="max-h-96 overflow-y-auto space-y-2">
              <div *ngFor="let chunk of documentChunks" class="border rounded p-3">
                <div class="flex justify-between items-center mb-2">
                  <span class="text-sm font-medium">Chunk {{ chunk.chunk_index }}</span>
                  <nz-tag [nzColor]="chunk.milvus_id ? 'green' : 'red'" size="small">
                    {{ chunk.milvus_id ? 'In Milvus' : 'Not in Milvus' }}
                  </nz-tag>
                </div>
                <p class="text-sm text-gray-700">{{ chunk.content }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </nz-modal>

    <!-- Crawl Detail Modal -->
    <nz-modal 
      [(nzVisible)]="crawlDetailVisible" 
      nzTitle="Crawl Detail"
      [nzWidth]="800"
      (nzOnCancel)="crawlDetailVisible = false">
      <div *nzModalContent>
        <div *ngIf="selectedCrawl" class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="font-medium">Link:</label>
              <a [href]="selectedCrawl.link" target="_blank" class="text-blue-600">
                {{ selectedCrawl.link }}
              </a>
            </div>
            <div>
              <label class="font-medium">Tool:</label>
              <p>{{ selectedCrawl.crawl_tool }}</p>
            </div>
            <div>
              <label class="font-medium">Started At:</label>
              <p>{{ selectedCrawl.started_at | date:'full' }}</p>
            </div>
            <div>
              <label class="font-medium">Done At:</label>
              <p>{{ selectedCrawl.done_at | date:'full' }}</p>
            </div>
          </div>
          
          <div>
            <label class="font-medium">Content:</label>
            <div class="max-h-96 overflow-y-auto border rounded p-3 bg-gray-50">
              <pre class="text-sm whitespace-pre-wrap">{{ selectedCrawl.content }}</pre>
            </div>
          </div>
        </div>
      </div>
    </nz-modal>

    <!-- Edit Crawl Content Modal -->
    <nz-modal 
      [(nzVisible)]="editCrawlVisible" 
      nzTitle="Edit Crawl Content"
      [nzWidth]="1000"
      (nzOnCancel)="editCrawlVisible = false">
      <div *nzModalContent>
        <div *ngIf="selectedCrawl" class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="font-medium">Link:</label>
              <a [href]="selectedCrawl.link" target="_blank" class="text-blue-600">
                {{ selectedCrawl.link }}
              </a>
            </div>
            <div>
              <label class="font-medium">Tool:</label>
              <p>{{ selectedCrawl.crawl_tool }}</p>
            </div>
          </div>
          
          <div>
            <label class="font-medium">Content:</label>
            <textarea 
              nz-input 
              [(ngModel)]="editingContent"
              [nzAutosize]="{ minRows: 10, maxRows: 20 }"
              class="w-full"
              placeholder="Enter new content...">
            </textarea>
          </div>
          
          <div class="flex justify-end space-x-2">
            <button nz-button (click)="editCrawlVisible = false">
              Cancel
            </button>
            <button 
              nz-button 
              nzType="primary" 
              [nzLoading]="editCrawlLoading"
              (click)="saveCrawlContent()">
              Save Changes
            </button>
          </div>
        </div>
      </div>
    </nz-modal>
        </div>
      </div>
  `,
  styles: [`
    /* Custom styles */
    :host ::ng-deep .ant-table {
      border-radius: 8px;
      overflow: hidden;
    }
    
    :host ::ng-deep .ant-table-thead > tr > th {
      background: #fafafa;
      font-weight: 600;
    }

    :host ::ng-deep .ant-tabs-tab {
      font-weight: 500;
    }

    :host ::ng-deep .ant-card {
      border-radius: 8px;
    }
  `]
})
export class UsersComponent implements OnInit {
  // Documents
  documents: Document[] = [];
  documentsLoading = false;
  documentSearchQuery = '';

  // Crawls
  crawls: any[] = [];
  crawlsLoading = false;
  crawlLoading = false;

  // Search
  searchResults: SearchResult[] = [];
  searchLoading = false;

  // Forms
  crawlForm: FormGroup;
  searchForm: FormGroup;

  // Modals
  documentDetailVisible = false;
  crawlDetailVisible = false;
  editCrawlVisible = false;
  selectedDocument: Document | null = null;
  selectedCrawl: any = null;
  documentChunks: any[] = [];
  editingContent = '';
  editCrawlLoading = false;

  constructor(
    private documentService: DocumentService,
    private message: NzMessageService,
    private fb: FormBuilder
  ) {
    this.crawlForm = this.fb.group({
      link: ['', [Validators.required, Validators.pattern('https?://.+')]],
      crawl_tool: ['firecrawl', Validators.required]
    });

    this.searchForm = this.fb.group({
      query: ['', Validators.required],
      top_k: [5, [Validators.min(1), Validators.max(20)]],
      document_ids: ['']
    });
  }

  ngOnInit() {
    this.loadDocuments();
    this.loadCrawls();
  }

  // Documents
  loadDocuments() {
    this.documentsLoading = true;
    this.documentService.getDocuments().subscribe({
      next: (response) => {
        this.documents = response.documents;
        this.documentsLoading = false;
      },
      error: (error) => {
        this.message.error('Failed to load documents');
        this.documentsLoading = false;
        console.error('Error loading documents:', error);
      }
    });
  }

  searchDocuments() {
    // Implement local search if needed
  }

  viewDocumentDetail(document: Document) {
    this.selectedDocument = document;
    this.documentService.getDocumentDetail(document.id).subscribe({
      next: (response) => {
        this.documentChunks = response.chunks;
        this.documentDetailVisible = true;
      },
      error: (error) => {
        this.message.error('Failed to load document detail');
        console.error('Error loading document detail:', error);
      }
    });
  }

  deleteDocument(documentId: number) {
    this.documentService.deleteDocument(documentId).subscribe({
      next: (response) => {
        this.message.success('Document deleted successfully');
        this.loadDocuments();
      },
      error: (error) => {
        this.message.error('Failed to delete document');
        console.error('Error deleting document:', error);
      }
    });
  }

  retryMilvus(documentId: number) {
    this.documentService.retryMilvusInserts(documentId).subscribe({
      next: (response) => {
        this.message.success(`Retry completed: ${response.retry_results.successful} successful, ${response.retry_results.failed} failed`);
      },
      error: (error) => {
        this.message.error('Failed to retry Milvus inserts');
        console.error('Error retrying Milvus inserts:', error);
      }
    });
  }

  // Crawls
  loadCrawls() {
    this.crawlsLoading = true;
    this.documentService.getCrawls().subscribe({
      next: (response) => {
        this.crawls = response.crawls;
        this.crawlsLoading = false;
      },
      error: (error) => {
        this.message.error('Failed to load crawls');
        this.crawlsLoading = false;
        console.error('Error loading crawls:', error);
      }
    });
  }

  createCrawl() {
    if (this.crawlForm.invalid) {
      this.message.error('Please fill in all required fields');
      return;
    }

    this.crawlLoading = true;
    const crawlRequest: CrawlRequest = this.crawlForm.value;
    
    this.documentService.createCrawl(crawlRequest).subscribe({
      next: (response) => {
        this.message.success('Crawl started successfully');
        this.crawlForm.reset({ crawl_tool: 'firecrawl' });
        this.crawlLoading = false;
        this.loadCrawls();
        this.loadDocuments(); // Refresh documents as new document is created
      },
      error: (error) => {
        this.message.error('Failed to start crawl');
        this.crawlLoading = false;
        console.error('Error creating crawl:', error);
      }
    });
  }

  viewCrawlDetail(crawl: any) {
    this.selectedCrawl = crawl;
    this.crawlDetailVisible = true;
  }

  // Search
  performSearch() {
    if (this.searchForm.invalid) {
      this.message.error('Please enter a search query');
      return;
    }

    this.searchLoading = true;
    const searchRequest: SearchRequest = {
      query: this.searchForm.value.query,
      top_k: this.searchForm.value.top_k
    };

    // Parse document IDs if provided
    if (this.searchForm.value.document_ids) {
      const ids = this.searchForm.value.document_ids.split(',').map((id: string) => parseInt(id.trim())).filter((id: number) => !isNaN(id));
      if (ids.length > 0) {
        searchRequest.document_ids = ids;
      }
    }

    this.documentService.searchDocuments(searchRequest).subscribe({
      next: (response) => {
        this.searchResults = response.results;
        this.searchLoading = false;
      },
      error: (error) => {
        this.message.error('Search failed');
        this.searchLoading = false;
        console.error('Error performing search:', error);
      }
    });
  }

  // New methods for crawl management
  editCrawlContent(crawl: any) {
    this.selectedCrawl = crawl;
    this.editingContent = crawl.content;
    this.editCrawlVisible = true;
  }

  saveCrawlContent() {
    if (!this.selectedCrawl || !this.editingContent.trim()) {
      this.message.error('Please enter content');
      return;
    }

    this.editCrawlLoading = true;
    this.documentService.updateCrawlContent(this.selectedCrawl.id, this.editingContent).subscribe({
      next: (response) => {
        this.message.success('Crawl content updated successfully');
        this.editCrawlVisible = false;
        this.editCrawlLoading = false;
        this.loadCrawls();
        this.loadDocuments(); // Refresh documents as chunks were updated
      },
      error: (error) => {
        this.message.error('Failed to update crawl content');
        this.editCrawlLoading = false;
        console.error('Error updating crawl content:', error);
      }
    });
  }

  recrawlContent(crawlId: number) {
    this.message.info('Starting recrawl...');
    this.documentService.recrawlContent(crawlId).subscribe({
      next: (response) => {
        this.message.success('Recrawl completed successfully');
        this.loadCrawls();
        this.loadDocuments(); // Refresh documents as chunks were updated
      },
      error: (error) => {
        this.message.error('Recrawl failed');
        console.error('Error recrawling:', error);
      }
    });
  }
} 