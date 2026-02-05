import { Component, Input, Output, EventEmitter, HostListener, ElementRef, ViewChild, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';

export type DropdownPlacement = 'bottomLeft' | 'bottomRight' | 'topLeft' | 'topRight' | 'bottom' | 'top';

@Component({
  selector: 'app-custom-dropdown',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="custom-dropdown" [class.open]="isOpen" #dropdownContainer>
      <div 
        class="custom-dropdown-trigger" 
        (click)="toggle()"
        [class.active]="isOpen">
        <ng-content select="[trigger]"></ng-content>
      </div>
      <div 
        *ngIf="isOpen"
        class="custom-dropdown-menu"
        [class.bottom-left]="placement === 'bottomLeft'"
        [class.bottom-right]="placement === 'bottomRight'"
        [class.top-left]="placement === 'topLeft'"
        [class.top-right]="placement === 'topRight'"
        [class.bottom]="placement === 'bottom'"
        [class.top]="placement === 'top'"
        #menuContainer>
        <ng-content select="[menu]"></ng-content>
      </div>
    </div>
  `,
  styles: [`
    .custom-dropdown {
      position: relative;
      display: inline-block;
      width: 100%;
    }

    .custom-dropdown-trigger {
      cursor: pointer;
      user-select: none;
      width: 100%;
      position: relative;
      display: flex;
      align-items: center;
      background: #ffffff;
      border: 1px solid #e0e0e0;
      border-radius: 8px;
      padding: 0 12px;
      min-height: 40px;
      transition: border-color 0.2s, box-shadow 0.2s;
    }

    .custom-dropdown:hover .custom-dropdown-trigger {
      border-color: #d0d0d0;
    }

    .custom-dropdown.open .custom-dropdown-trigger {
      border-color: #d0d0d0;
      box-shadow: 0 0 0 1px rgba(0, 0, 0, 0.06);
    }

    .custom-dropdown-trigger.active {
      border-color: #d0d0d0;
      box-shadow: 0 0 0 1px rgba(0, 0, 0, 0.06);
    }

    /* Nội dung trigger (button) bên trong dùng style của wrapper */
    :host ::ng-deep .custom-dropdown-trigger > * {
      border: none !important;
      background: transparent !important;
      box-shadow: none !important;
      min-height: 38px;
      padding: 0 0 0 0 !important;
      width: 100%;
      display: flex !important;
      align-items: center;
      justify-content: space-between;
      text-align: left;
      font-size: 14px;
      color: #333333;
      cursor: pointer;
      outline: none;
    }

    .custom-dropdown-menu {
      position: absolute;
      z-index: 1000;
      background: #ffffff;
      border: 1px solid #e8e8e8;
      border-radius: 8px;
      box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
      margin-top: 4px;
      min-width: 100%;
    }

    .custom-dropdown-menu.bottom-left {
      top: 100%;
      left: 0;
      margin-top: 4px;
    }

    .custom-dropdown-menu.bottom-right {
      top: 100%;
      right: 0;
      margin-top: 4px;
    }

    .custom-dropdown-menu.top-left {
      bottom: 100%;
      left: 0;
      margin-bottom: 4px;
    }

    .custom-dropdown-menu.top-right {
      bottom: 100%;
      right: 0;
      margin-bottom: 4px;
    }

    .custom-dropdown-menu.bottom {
      top: 100%;
      left: 50%;
      transform: translateX(-50%);
      margin-top: 4px;
    }

    .custom-dropdown-menu.top {
      bottom: 100%;
      left: 50%;
      transform: translateX(-50%);
      margin-bottom: 4px;
    }
  `]
})
export class CustomDropdownComponent implements OnInit, OnDestroy {
  @Input() placement: DropdownPlacement = 'bottomLeft';
  @Input() closeOnClickOutside: boolean = true;
  @Output() openChange = new EventEmitter<boolean>();

  @ViewChild('dropdownContainer', { static: false }) dropdownContainer!: ElementRef;
  @ViewChild('menuContainer', { static: false }) menuContainer!: ElementRef;

  isOpen = false;

  @HostListener('document:click', ['$event'])
  onDocumentClick(event: MouseEvent): void {
    if (!this.isOpen || !this.closeOnClickOutside) {
      return;
    }

    const target = event.target as HTMLElement;
    const container = this.dropdownContainer?.nativeElement;

    if (container && !container.contains(target)) {
      this.close();
    }
  }

  @HostListener('document:keydown.escape', ['$event'])
  onEscapeKey(event: KeyboardEvent): void {
    if (this.isOpen) {
      this.close();
    }
  }

  ngOnInit(): void {
    // Component initialization
  }

  ngOnDestroy(): void {
    // Cleanup if needed
  }

  toggle(): void {
    if (this.isOpen) {
      this.close();
    } else {
      this.open();
    }
  }

  open(): void {
    if (!this.isOpen) {
      this.isOpen = true;
      this.openChange.emit(true);
    }
  }

  close(): void {
    if (this.isOpen) {
      this.isOpen = false;
      this.openChange.emit(false);
    }
  }
}

