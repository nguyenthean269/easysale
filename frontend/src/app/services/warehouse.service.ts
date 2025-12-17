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
  data_status: 'REVIEWING' | 'PENDING' | 'APPROVED';
  unit_allocation: string;
  listing_type?: 'CAN_THUE' | 'CAN_CHO_THUE' | 'CAN_BAN' | 'CAN_MUA' | 'KHAC';
  phone_number?: string;
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
    property_group_slug?: string;
    unit_type_id?: number;
    unit_type_slug?: string;
    listing_type?: 'CAN_THUE' | 'CAN_CHO_THUE' | 'CAN_BAN' | 'CAN_MUA' | 'KHAC';
    price_from?: number;
    price_to?: number;
    area_from?: number;
    area_to?: number;
  } = {}): Observable<ApartmentsListResponse> {
    const queryParams = new URLSearchParams();

    if (params.limit !== undefined) queryParams.set('limit', params.limit.toString());
    if (params.offset !== undefined) queryParams.set('offset', params.offset.toString());
    if (params.property_group_id !== undefined) queryParams.set('property_group_id', params.property_group_id.toString());
    if (params.property_group_slug !== undefined) queryParams.set('property_group_slug', params.property_group_slug);
    if (params.unit_type_id !== undefined) queryParams.set('unit_type_id', params.unit_type_id.toString());
    if (params.unit_type_slug !== undefined) queryParams.set('unit_type_slug', params.unit_type_slug);
    if (params.listing_type !== undefined) queryParams.set('listing_type', params.listing_type);
    if (params.price_from !== undefined) queryParams.set('price_from', params.price_from.toString());
    if (params.price_to !== undefined) queryParams.set('price_to', params.price_to.toString());
    if (params.area_from !== undefined) queryParams.set('area_from', params.area_from.toString());
    if (params.area_to !== undefined) queryParams.set('area_to', params.area_to.toString());

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

  /**
   * Lấy danh sách property groups theo parent_id hoặc slug
   */
  getPropertyGroups(parentId?: number, slug?: string): Observable<PropertyGroupsResponse> {
    const queryParams = new URLSearchParams();
    if (parentId !== undefined) {
      queryParams.set('parent_id', parentId.toString());
    }
    if (slug !== undefined) {
      queryParams.set('slug', slug);
    }
    const url = `${this.apiUrl}/property-groups${queryParams.toString() ? '?' + queryParams.toString() : ''}`;
    return this.http.get<PropertyGroupsResponse>(url);
  }

  /**
   * Lấy danh sách unit types
   */
  getUnitTypes(): Observable<UnitTypesResponse> {
    return this.http.get<UnitTypesResponse>(`${this.apiUrl}/unit-types`);
  }
}

export interface PropertyGroup {
  id: number;
  name: string;
  description?: string;
  thumbnail?: string;
  slug?: string;
  parent_id?: number;
  group_type?: number;
  group_type_name?: string;
}

export interface PropertyGroupsResponse {
  success: boolean;
  data: PropertyGroup[];
  count: number;
  error?: string;
}

export interface UnitType {
  id: number;
  name: string;
  slug?: string;
  description?: string;
}

export interface UnitTypesResponse {
  success: boolean;
  data: UnitType[];
  count: number;
  error?: string;
}
