import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { PropertyGroup } from '../../../services/warehouse.service';

@Component({
  selector: 'app-du-an-item',
  standalone: true,
  imports: [CommonModule, RouterModule],
  template: `
    <div class="bg-white rounded-lg border border-gray-200 p-3 mb-3 transition-all duration-300 hover:shadow-md hover:-translate-y-0.5 hover:border-blue-300">
      <div class="flex gap-3 items-start">
        <!-- Thumbnail -->
        <div class="flex-shrink-0 w-24 h-24 rounded-md overflow-hidden bg-gradient-to-br from-gray-50 to-gray-100 flex items-center justify-center group">
          <img *ngIf="project.thumbnail"
               [src]="project.thumbnail"
               [alt]="project.name"
               class="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105" />
          <div *ngIf="!project.thumbnail" class="w-full h-full bg-gradient-to-br from-gray-100 to-gray-200 flex items-center justify-center">
            <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round" class="text-gray-400 transition-all duration-300 group-hover:text-gray-500 group-hover:scale-110">
              <rect width="18" height="18" x="3" y="3" rx="2" ry="2"/>
              <circle cx="9" cy="9" r="2"/>
              <path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21"/>
            </svg>
          </div>
        </div>

        <!-- Content -->
        <div class="flex-1 min-w-0 flex flex-col gap-1.5">
          <h3 class="text-base font-semibold text-gray-800 leading-tight line-clamp-2">
            <a *ngIf="project.slug"
               [routerLink]="getProjectRoute()"
               class="hover:text-blue-600 transition-colors duration-200">
              {{ project.name }}
            </a>
            <span *ngIf="!project.slug">{{ project.name }}</span>
          </h3>

          <p *ngIf="project.description"
             class="text-sm text-gray-600 leading-relaxed line-clamp-2">
            {{ project.description }}
          </p>

          <div *ngIf="project.group_type_name" class="flex items-center gap-2 mt-1">
            <span class="inline-flex items-center px-2.5 py-1 bg-gradient-to-r from-blue-50 to-blue-100 text-blue-700 text-xs font-medium rounded border border-blue-200 transition-all duration-200 hover:from-blue-100 hover:to-blue-200 hover:border-blue-300">
              {{ project.group_type_name }}
            </span>
          </div>
        </div>
      </div>
    </div>
  `
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

