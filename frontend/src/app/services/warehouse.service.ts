import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface Apartment {
  id: number;
  property_group: number;
  property_group_name: string;
  unit_type: number;
  unit_type_name: string;
  unit_code: string;
  unit_axis: string;
  unit_floor_number: number;
  area_land: number;
  area_construction: number;
  area_net: number;
  area_gross: number;
  num_bedrooms: number;
  num_bathrooms: number;
  type_view: number;
  direction_door: string;
  direction_balcony: string;
  price: number;
  price_early: number;
  price_schedule: number;
  price_loan: number;
  price_rent: number;
  notes: string;
  status: string;
  unit_allocation: string;
}

export interface ApartmentsListResponse {
  success: boolean;
  data: Apartment[];
  total: number;
  limit: number;
  offset: number;
  has_more: boolean;
  error?: string;
}

export interface ApartmentByIdsRequest {
  ids: number[];
}

export interface ApartmentByIdsResponse {
  success: boolean;
  data: Apartment[];
  requested_count: number;
  found_count: number;
  missing_ids: number[];
  error?: string;
}

@Injectable({
  providedIn: 'root'
})
export class WarehouseService {
  private apiUrl = `${environment.apiBaseUrl}/warehouse/api/warehouse`;

  constructor(private http: HttpClient) {}

  /**
   * Lấy danh sách apartments với pagination và filters
   */
  getApartmentsList(params: {
    limit?: number;
    offset?: number;
    property_group_id?: number;
    unit_type_id?: number;
  } = {}): Observable<ApartmentsListResponse> {
    const queryParams = new URLSearchParams();
    
    if (params.limit !== undefined) queryParams.set('limit', params.limit.toString());
    if (params.offset !== undefined) queryParams.set('offset', params.offset.toString());
    if (params.property_group_id !== undefined) queryParams.set('property_group_id', params.property_group_id.toString());
    if (params.unit_type_id !== undefined) queryParams.set('unit_type_id', params.unit_type_id.toString());

    const url = `${this.apiUrl}/apartments/list${queryParams.toString() ? '?' + queryParams.toString() : ''}`;
    return this.http.get<ApartmentsListResponse>(url);
  }

  /**
   * Lấy apartments theo danh sách IDs
   */
  getApartmentsByIds(ids: number[]): Observable<ApartmentByIdsResponse> {
    return this.http.post<ApartmentByIdsResponse>(`${this.apiUrl}/apartments/by-ids`, { ids });
  }

  /**
   * Lấy apartment theo ID
   */
  getApartmentById(id: number): Observable<{ success: boolean; data: Apartment; error?: string }> {
    return this.http.get<{ success: boolean; data: Apartment; error?: string }>(`${this.apiUrl}/apartments/${id}`);
  }

  /**
   * Tìm kiếm apartments
   */
  searchApartments(params: {
    q: string;
    limit?: number;
    offset?: number;
  }): Observable<ApartmentsListResponse> {
    const queryParams = new URLSearchParams();
    queryParams.set('q', params.q);
    if (params.limit !== undefined) queryParams.set('limit', params.limit.toString());
    if (params.offset !== undefined) queryParams.set('offset', params.offset.toString());

    return this.http.get<ApartmentsListResponse>(`${this.apiUrl}/apartments/search?${queryParams.toString()}`);
  }
}
