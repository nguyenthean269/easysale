import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { NzCardModule } from 'ng-zorro-antd/card';
import { PropertyGroup } from '../../../services/warehouse.service';

@Component({
  selector: 'app-du-an-item',
  standalone: true,
  imports: [CommonModule, NzCardModule, RouterModule],
  template: `
    <nz-card [nzHoverable]="true" class="project-item-card">
      <div class="project-item-content">
        <div class="project-thumbnail" *ngIf="project.thumbnail">
          <img [src]="project.thumbnail" [alt]="project.name" />
        </div>
        <div class="project-info">
          <h3 class="project-name">
            <a *ngIf="project.slug" [routerLink]="getProjectRoute()" class="project-name-link">
              {{ project.name }}
            </a>
            <span *ngIf="!project.slug">{{ project.name }}</span>
          </h3>
          <p class="project-description" *ngIf="project.description">
            {{ project.description }}
          </p>
          <div class="project-meta" *ngIf="project.group_type_name">
            <span class="project-type">{{ project.group_type_name }}</span>
          </div>
        </div>
      </div>
    </nz-card>
  `,
  styles: [`
    .project-item-card {
      margin-bottom: 16px;
      border-radius: 8px;
      transition: all 0.3s;
    }

    .project-item-card:hover {
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
      transform: translateY(-2px);
    }

    .project-item-content {
      display: flex;
      gap: 16px;
    }

    .project-thumbnail {
      flex-shrink: 0;
      width: 120px;
      height: 120px;
      border-radius: 8px;
      overflow: hidden;
      background: #f5f5f5;
    }

    .project-thumbnail img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }

    .project-info {
      flex: 1;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }

    .project-name {
      margin: 0;
      font-size: 18px;
      font-weight: 600;
      color: #1a1a1a;
    }

    .project-name-link {
      color: #1a1a1a;
      text-decoration: none;
      transition: color 0.3s;
    }

    .project-name-link:hover {
      color: #1890ff;
      text-decoration: underline;
    }

    .project-description {
      margin: 0;
      color: #666;
      font-size: 14px;
      line-height: 1.5;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }

    .project-meta {
      margin-top: auto;
    }

    .project-type {
      display: inline-block;
      padding: 4px 12px;
      background: #f0f0f0;
      border-radius: 4px;
      font-size: 12px;
      color: #666;
    }
  `]
})
export class DuAnItemComponent {
  @Input() project!: PropertyGroup;
  @Input() routePath?: string; // Route path prefix (e.g., 'can-ho-chung-cu-cho-thue' or 'can-ho-chung-cu-ban')

  getProjectRoute(): string {
    // Navigate to listing page with property group filter using slug
    // Format: /can-ho-chung-cu-cho-thue,du-an-{slug} or /can-ho-chung-cu-ban,du-an-{slug}
    if (this.project.slug) {
      const prefix = this.routePath || 'can-ho-chung-cu-cho-thue'; // Default to cho-thue
      return `/${prefix},du-an-${this.project.slug}`;
    }
    return '#';
  }
}

