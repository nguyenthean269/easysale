import { Component, Input, OnInit, OnChanges, SimpleChanges, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router, NavigationEnd } from '@angular/router';
import { Subject, takeUntil, filter } from 'rxjs';
import { NzSpinModule } from 'ng-zorro-antd/spin';
import { NzGridModule } from 'ng-zorro-antd/grid';
import { WarehouseService, PropertyGroup } from '../../../services/warehouse.service';
import { DuAnItemComponent } from '../du-an-item/du-an-item.component';

@Component({
  selector: 'app-danh-sach-du-an',
  standalone: true,
  imports: [
    CommonModule,
    NzSpinModule,
    NzGridModule,
    DuAnItemComponent
  ],
  template: `
    <div class="project-list-container">
      <nz-spin [nzSpinning]="loading">
        <div *ngIf="!loading && projects.length === 0" class="empty-state">
          <p>Không có dự án nào</p>
        </div>
        <div *ngIf="!loading && projects.length > 0" class="project-list">
          <nz-row [nzGutter]="[16, 16]">
            <nz-col [nzXs]="24" [nzSm]="12" [nzMd]="8" [nzLg]="6" *ngFor="let project of projects">
              <app-du-an-item [project]="project" [routePath]="routePath"></app-du-an-item>
            </nz-col>
          </nz-row>
        </div>
      </nz-spin>
    </div>
  `,
  styles: [`
    .project-list-container {
      padding: 16px 0;
    }

    .project-list {
      min-height: 200px;
    }

    .empty-state {
      text-align: center;
      padding: 40px;
      color: #999;
    }
  `]
})
export class DanhSachDuAnComponent implements OnInit, OnChanges, OnDestroy {
  @Input() parentId?: number;
  @Input() propertyGroupSlug?: string; // Property group slug to get children
  @Input() routePath?: string; // Route path prefix to pass to du-an-item
  
  projects: PropertyGroup[] = [];
  loading = false;
  private destroy$ = new Subject<void>();
  private previousSlug?: string;

  constructor(
    private warehouseService: WarehouseService,
    private router: Router,
    private route: ActivatedRoute
  ) {}

  ngOnInit() {
    this.loadProjects();
    
    // Listen to route changes to reload when navigating
    this.router.events
      .pipe(
        filter(event => event instanceof NavigationEnd),
        takeUntil(this.destroy$)
      )
      .subscribe(() => {
        // Check if slug changed by comparing with previous value
        const currentSlug = this.propertyGroupSlug;
        if (this.previousSlug !== currentSlug) {
          this.previousSlug = currentSlug;
          this.loadProjects();
        }
      });
  }

  ngOnDestroy() {
    this.destroy$.next();
    this.destroy$.complete();
  }

  ngOnChanges(changes: SimpleChanges) {
    // Reload when parentId or propertyGroupSlug changes
    // Check if propertyGroupSlug actually changed (including from string to undefined)
    const slugChanged = changes['propertyGroupSlug'];
    const parentIdChanged = changes['parentId'];
    
    if (slugChanged) {
      // Track previous value to detect changes from string to undefined
      const previousSlug = slugChanged.previousValue;
      const currentSlug = slugChanged.currentValue;
      
      // Reload if slug actually changed (including undefined → string or string → undefined)
      if (previousSlug !== currentSlug) {
        this.previousSlug = currentSlug;
        this.loadProjects();
      }
    } else if (parentIdChanged) {
      this.loadProjects();
    }
  }

  loadProjects() {
    this.loading = true;
    // If propertyGroupSlug is undefined, pass undefined (not null) to get root groups
    const slug = this.propertyGroupSlug || undefined;
    this.warehouseService.getPropertyGroups(this.parentId, slug).subscribe({
      next: (response) => {
        if (response.success) {
          this.projects = response.data;
        } else {
          console.error('Error loading projects:', response.error);
          this.projects = [];
        }
        this.loading = false;
      },
      error: (error) => {
        console.error('Error loading projects:', error);
        this.projects = [];
        this.loading = false;
      }
    });
  }
}

