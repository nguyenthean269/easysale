import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { NzTableModule } from 'ng-zorro-antd/table';
import { NzButtonModule } from 'ng-zorro-antd/button';
import { NzSpaceModule } from 'ng-zorro-antd/space';

@Component({
  selector: 'app-users',
  standalone: true,
  imports: [CommonModule, NzTableModule, NzButtonModule, NzSpaceModule],
  template: `
    <div class="space-y-6">
      <div class="flex items-center justify-between">
        <h1 class="text-2xl font-semibold text-gray-800">Users Management</h1>
        <button nz-button nzType="primary" class="bg-blue-600 hover:bg-blue-700">
          Add New User
        </button>
      </div>
      
      <nz-table 
        #basicTable 
        [nzData]="listOfData"
        [nzPageSize]="10"
        [nzShowSizeChanger]="true"
        [nzShowQuickJumper]="true"
        [nzShowTotal]="totalTemplate">
        
        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Email</th>
            <th>Role</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr *ngFor="let data of basicTable.data">
            <td>{{ data.id }}</td>
            <td>{{ data.name }}</td>
            <td>{{ data.email }}</td>
            <td>
              <span [class]="data.role === 'Admin' ? 'bg-red-100 text-red-800' : 'bg-blue-100 text-blue-800'" 
                    class="px-2 py-1 rounded-full text-xs font-medium">
                {{ data.role }}
              </span>
            </td>
            <td>
              <span [class]="data.status === 'Active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'" 
                    class="px-2 py-1 rounded-full text-xs font-medium">
                {{ data.status }}
              </span>
            </td>
            <td>
              <nz-space>
                <button nz-button nzType="link" nzSize="small">Edit</button>
                <button nz-button nzType="link" nzDanger nzSize="small">Delete</button>
              </nz-space>
            </td>
          </tr>
        </tbody>
      </nz-table>
      
      <ng-template #totalTemplate let-total>Total {{ total }} items</ng-template>
    </div>
  `,
  styles: [`
    /* Custom styles for users table */
    :host ::ng-deep .ant-table {
      border-radius: 8px;
      overflow: hidden;
    }
    
    :host ::ng-deep .ant-table-thead > tr > th {
      background: #fafafa;
      font-weight: 600;
    }
  `]
})
export class UsersComponent {
  listOfData = [
    {
      id: 1,
      name: 'John Doe',
      email: 'john@example.com',
      role: 'Admin',
      status: 'Active'
    },
    {
      id: 2,
      name: 'Jane Smith',
      email: 'jane@example.com',
      role: 'User',
      status: 'Active'
    },
    {
      id: 3,
      name: 'Bob Johnson',
      email: 'bob@example.com',
      role: 'User',
      status: 'Inactive'
    },
    {
      id: 4,
      name: 'Alice Brown',
      email: 'alice@example.com',
      role: 'Admin',
      status: 'Active'
    }
  ];
} 