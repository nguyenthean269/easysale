import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { NzCardModule } from 'ng-zorro-antd/card';
import { NzButtonModule } from 'ng-zorro-antd/button';
import { NzGridModule } from 'ng-zorro-antd/grid';
import { NzTagModule } from 'ng-zorro-antd/tag';

@Component({
  selector: 'app-products',
  standalone: true,
  imports: [CommonModule, NzCardModule, NzButtonModule, NzGridModule, NzTagModule],
  templateUrl: './products.component.html',
  styleUrls: ['./products.component.css']
})
export class ProductsComponent {
  products = [
    {
      name: 'Product 1',
      description: 'High-quality product with amazing features',
      category: 'Premium',
      price: 99.99
    },
    {
      name: 'Product 2',
      description: 'Essential product for everyday use',
      category: 'Standard',
      price: 49.99
    },
    {
      name: 'Product 3',
      description: 'Advanced product with cutting-edge technology',
      category: 'Premium',
      price: 199.99
    }
  ];
} 