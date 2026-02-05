import {
  Component,
  Input,
  Output,
  EventEmitter,
  HostListener,
  ElementRef,
  ViewChild,
  forwardRef,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { ControlValueAccessor, NG_VALUE_ACCESSOR, FormsModule } from '@angular/forms';

export interface SearchableSelectOption {
  id: number;
  name: string;
}

@Component({
  selector: 'app-searchable-select',
  standalone: true,
  imports: [CommonModule, FormsModule],
  providers: [
    {
      provide: NG_VALUE_ACCESSOR,
      useExisting: forwardRef(() => SearchableSelectComponent),
      multi: true,
    },
  ],
  template: `
    <div class="searchable-select" #container [class.open]="isOpen" [class.disabled]="disabled">
      <div class="select-input-wrapper" (click)="onInputWrapperClick()">
        <input
          #searchInput
          type="text"
          class="select-input"
          [placeholder]="placeholder"
          [value]="displayText"
          (input)="onSearchInput($event)"
          (focus)="onFocus()"
          (keydown)="onKeydown($event)"
          [readonly]="!isOpen"
          [disabled]="disabled"
        />
        @if (allowClear && value != null && !disabled) {
          <button type="button" class="select-clear" (click)="clear($event)" aria-label="Xóa">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-x-icon lucide-x"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
          </button>
        } @else {
          <span class="select-search-icon" aria-hidden="true">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-search-icon lucide-search"><path d="m21 21-4.34-4.34"/><circle cx="11" cy="11" r="8"/></svg>
          </span>
        }
      </div>

      @if (isOpen) {
        <div class="select-dropdown">
          <div class="select-dropdown-list">
            @for (opt of filteredOptions; track opt.id) {
              <div
                class="select-option"
                [class.highlighted]="highlightedId === opt.id"
                (click)="selectOption(opt)"
                (mouseenter)="highlightedId = opt.id"
              >
                {{ opt.name }}
              </div>
            }
            @if (filteredOptions.length === 0) {
              <div class="select-option empty">Không có kết quả</div>
            }
          </div>
        </div>
      }
    </div>
  `,
  styles: [`
    .searchable-select {
      position: relative;
      width: 100%;
    }

    .select-input-wrapper {
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

    .searchable-select.open .select-input-wrapper {
      border-color: #d0d0d0;
      box-shadow: 0 0 0 1px rgba(0, 0, 0, 0.06);
    }

    .searchable-select:hover:not(.disabled) .select-input-wrapper {
      border-color: #d0d0d0;
    }

    .select-input {
      flex: 1;
      border: none;
      outline: none;
      background: transparent;
      font-size: 14px;
      color: #333333;
      min-width: 0;
      padding: 8px 8px 8px 0;
    }

    .select-input::placeholder {
      color: #a0a0a0;
    }

    .select-input:disabled {
      cursor: not-allowed;
      color: #999;
    }

    .select-search-icon,
    .select-clear {
      display: flex;
      align-items: center;
      justify-content: center;
      color: #999;
      flex-shrink: 0;
    }

    .select-clear {
      background: none;
      border: none;
      cursor: pointer;
      padding: 4px;
      border-radius: 4px;
      color: #666;
    }

    .select-clear:hover {
      color: #333;
      background: #f0f0f0;
    }

    .select-dropdown {
      position: absolute;
      top: calc(100% + 4px);
      left: 0;
      right: 0;
      background: #ffffff;
      border: 1px solid #e8e8e8;
      border-radius: 8px;
      box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
      z-index: 1000;
      max-height: 280px;
      overflow: hidden;
    }

    .select-dropdown-list {
      max-height: 268px;
      overflow-y: auto;
      padding: 6px 0;
    }

    .select-dropdown-list::-webkit-scrollbar {
      width: 6px;
    }

    .select-dropdown-list::-webkit-scrollbar-track {
      background: transparent;
    }

    .select-dropdown-list::-webkit-scrollbar-thumb {
      background: #c0c0c0;
      border-radius: 3px;
    }

    .select-option {
      padding: 10px 14px;
      font-size: 14px;
      color: #333333;
      cursor: pointer;
      transition: background 0.15s;
      margin: 0 6px;
      border-radius: 6px;
    }

    .select-option:hover,
    .select-option.highlighted {
      background: #f0f0f0;
    }

    .select-option.empty {
      color: #999;
      cursor: default;
    }

    .searchable-select.disabled .select-input-wrapper {
      background: #f5f5f5;
      cursor: not-allowed;
    }
  `],
})
export class SearchableSelectComponent implements ControlValueAccessor {
  @Input() options: SearchableSelectOption[] = [];
  @Input() placeholder = 'Chọn...';
  @Input() allowClear = true;
  @Output() valueChange = new EventEmitter<number | null>();

  @ViewChild('container') container!: ElementRef<HTMLElement>;
  @ViewChild('searchInput') searchInput!: ElementRef<HTMLInputElement>;

  isOpen = false;
  searchQuery = '';
  highlightedId: number | null = null;
  value: number | null = null;
  disabled = false;

  private onChange: (value: number | null) => void = () => {};
  private onTouched: () => void = () => {};

  get selectedOption(): SearchableSelectOption | undefined {
    return this.value != null ? this.options.find((o) => o.id === this.value) : undefined;
  }

  get displayText(): string {
    if (this.isOpen) {
      return this.searchQuery;
    }
    return this.selectedOption?.name ?? '';
  }

  get filteredOptions(): SearchableSelectOption[] {
    const q = (this.searchQuery || '').trim().toLowerCase();
    if (!q) return this.options;
    return this.options.filter((o) => o.name.toLowerCase().includes(q));
  }

  @HostListener('document:click', ['$event'])
  onDocumentClick(event: MouseEvent): void {
    const el = this.container?.nativeElement;
    if (el && !el.contains(event.target as Node)) {
      this.close();
    }
  }

  onInputWrapperClick(): void {
    if (this.disabled) return;
    if (!this.isOpen) {
      this.open();
    }
  }

  onFocus(): void {
    if (this.disabled) return;
    this.open();
    this.onTouched();
  }

  onSearchInput(event: Event): void {
    const input = event.target as HTMLInputElement;
    this.searchQuery = input.value;
    const list = this.filteredOptions;
    this.highlightedId = list.length > 0 ? list[0].id : null;
  }

  onKeydown(event: KeyboardEvent): void {
    if (!this.isOpen) {
      if (event.key === 'Enter' || event.key === ' ' || event.key === 'ArrowDown') {
        event.preventDefault();
        this.open();
      }
      return;
    }

    const list = this.filteredOptions;
    const idx = list.findIndex((o) => o.id === this.highlightedId);

    switch (event.key) {
      case 'ArrowDown':
        event.preventDefault();
        this.highlightedId = list.length ? list[Math.min(idx + 1, list.length - 1)].id : null;
        break;
      case 'ArrowUp':
        event.preventDefault();
        this.highlightedId = list.length ? list[Math.max(idx - 1, 0)].id : null;
        break;
      case 'Enter':
        event.preventDefault();
        if (this.highlightedId != null) {
          const opt = list.find((o) => o.id === this.highlightedId);
          if (opt) this.selectOption(opt);
        }
        break;
      case 'Escape':
        event.preventDefault();
        this.close();
        break;
      default:
        break;
    }
  }

  open(): void {
    if (this.disabled) return;
    this.isOpen = true;
    this.searchQuery = '';
    this.highlightedId = this.value ?? this.filteredOptions[0]?.id ?? null;
    setTimeout(() => {
      this.searchInput?.nativeElement?.focus();
      this.searchInput?.nativeElement?.select?.();
    }, 0);
  }

  close(): void {
    this.isOpen = false;
    this.searchQuery = '';
    this.highlightedId = null;
  }

  selectOption(opt: SearchableSelectOption): void {
    this.value = opt.id;
    this.onChange(this.value);
    this.valueChange.emit(this.value);
    this.close();
  }

  clear(event: Event): void {
    event.stopPropagation();
    event.preventDefault();
    if (this.disabled) return;
    this.value = null;
    this.onChange(null);
    this.valueChange.emit(null);
  }

  writeValue(v: number | null): void {
    this.value = v ?? null;
  }

  registerOnChange(fn: (value: number | null) => void): void {
    this.onChange = fn;
  }

  registerOnTouched(fn: () => void): void {
    this.onTouched = fn;
  }

  setDisabledState(isDisabled: boolean): void {
    this.disabled = isDisabled;
    if (isDisabled) this.close();
  }
}
