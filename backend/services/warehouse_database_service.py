"""
Warehouse Database Service
Service xử lý tất cả các tương tác với database warehouse
"""

import os
import time
import logging
import json
from typing import Dict, Optional, List
from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from utils.property_service_sql import PropertyService

# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

# Setup logging
logger = logging.getLogger(__name__)

# Tạo Flask app cho warehouse database
warehouse_app = Flask(__name__)
warehouse_app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql://{os.getenv('DB_WAREHOUSE_USER', 'root')}:{os.getenv('DB_WAREHOUSE_PASSWORD', '')}@{os.getenv('DB_WAREHOUSE_HOST', '103.6.234.59')}:{os.getenv('DB_WAREHOUSE_PORT', '6033')}/{os.getenv('DB_WAREHOUSE_NAME', 'warehouse')}"
warehouse_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
warehouse_db = SQLAlchemy(warehouse_app)


class WarehouseDatabaseService:
    """Service xử lý tất cả các tương tác với database warehouse"""
    
    def __init__(self):
        """Khởi tạo service"""
        # Unit type mapping từ name sang id
        self.unit_type_mapping = {
            'Đơn lập': 1,
            'Song lập': 2,
            'Tứ lập': 3,
            'Tứ lập cạnh góc': 4,
            'Shophouse': 5,
            'Studio': 6,
            '1PN': 7,
            '1PN+': 8,
            '2PN1WC': 9,
            '2PN2WC': 10,
            '3PN': 11,
            'Đơn lập cạnh góc': 12
        }
        
        logger.info("WarehouseDatabaseService initialized")
    
    def get_warehouse_db_connection(self):
        """Tạo kết nối database warehouse với retry mechanism"""
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Attempting to connect to warehouse database... (attempt {attempt + 1}/{max_retries})")
                
                with warehouse_app.app_context():
                    # Sử dụng SQLAlchemy engine
                    connection = warehouse_db.engine.connect()
                    logger.info("✅ Warehouse database connection successful")
                    return connection
                    
            except Exception as e:
                logger.error(f"❌ Warehouse database connection error (attempt {attempt + 1}): {e}")
                logger.error(f"Error type: {type(e)}")
                
                if attempt < max_retries - 1:
                    logger.info(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    logger.error("❌ Failed to connect to warehouse database after all retries")
        
        return None
    
    def get_property_tree_for_prompt(self, root_id: int = 1) -> str:
        """
        Lấy property tree cho prompt
        
        Args:
            root_id (int): ID của root group (mặc định là 1)
            
        Returns:
            str: Property tree đã format cho prompt
        """
        try:
            # Lấy property tree từ database (đã bao gồm unit types)
            # Sử dụng raw SQL để tránh vấn đề với app context
            import pymysql
            
            # Tạo connection đến warehouse database
            connection = pymysql.connect(
                host=os.getenv('DB_WAREHOUSE_HOST', '103.6.234.59'),
                port=int(os.getenv('DB_WAREHOUSE_PORT', '6033')),
                user=os.getenv('DB_WAREHOUSE_USER', 'root'),
                password=os.getenv('DB_WAREHOUSE_PASSWORD', ''),
                database=os.getenv('DB_WAREHOUSE_NAME', 'warehouse'),
                charset='utf8mb4'
            )
            
            property_tree = PropertyService.get_property_tree_for_prompt_with_sql(root_id, connection)
            connection.close()

            return property_tree
            
        except Exception as e:
            logger.error(f"Lỗi khi lấy property tree: {str(e)}")
            # Fallback về hardcoded data nếu có lỗi
            return """Không có thông tin dự án"""
    
    def map_unit_type_to_id(self, unit_type_name) -> Optional[int]:
        """
        Map unit type name sang ID
        
        Args:
            unit_type_name: Tên loại căn hộ (có thể là string hoặc int)
            
        Returns:
            ID tương ứng hoặc None nếu không tìm thấy
        """
        if not unit_type_name:
            return None
        
        # Nếu đã là int thì return luôn
        if isinstance(unit_type_name, int):
            return unit_type_name
            
        # Convert to string nếu cần
        unit_type_str = str(unit_type_name)
            
        # Tìm exact match trước
        if unit_type_str in self.unit_type_mapping:
            return self.unit_type_mapping[unit_type_str]
        
        # Tìm partial match
        for name, id_val in self.unit_type_mapping.items():
            if unit_type_str.lower() in name.lower() or name.lower() in unit_type_str.lower():
                logger.info(f"Mapped '{unit_type_name}' to '{name}' (ID: {id_val})")
                return id_val
        
        logger.warning(f"Unit type '{unit_type_name}' not found in mapping")
        return None

    @staticmethod
    def format_phone_number(phone: Optional[str]) -> Optional[str]:
        """
        Chuẩn hóa số điện thoại: chỉ giữ chữ số.
        Ví dụ: 0979.468.357 -> 0979468357, 0979-468-357 -> 0979468357.
        Trả về None nếu input None hoặc chuỗi rỗng sau khi format.
        """
        if phone is None:
            return None
        digits = ''.join(c for c in str(phone).strip() if c.isdigit())
        return digits if digits else None

    def insert_apartment_via_api(self, apartment_data: Dict) -> bool:
        """
        Insert apartment vào warehouse database thông qua API
        
        Args:
            apartment_data: Dữ liệu căn hộ từ Groq
            
        Returns:
            True nếu thành công, False nếu lỗi
        """
        try:
            import requests
            
            # Map unit_type name sang ID
            unit_type_id = None
            if apartment_data.get('unit_type'):
                unit_type_id = self.map_unit_type_to_id(apartment_data['unit_type'])
            
            # Chuẩn bị dữ liệu để gửi tới API
            logger.info(f"🔍 Original apartment_data: {apartment_data}")
            logger.info(f"🔍 unit_type_id mapped: {unit_type_id}")
            
            apartment_record = {
                'property_group': apartment_data.get('property_group', 1),  # Default to 1
                'unit_type': unit_type_id,
                'unit_code': apartment_data.get('unit_code'),
                'unit_axis': apartment_data.get('unit_axis'),
                'unit_floor_number': apartment_data.get('unit_floor_number'),
                'area_land': apartment_data.get('area_land'),
                'area_construction': apartment_data.get('area_construction'),
                'area_net': apartment_data.get('area_net'),
                'area_gross': apartment_data.get('area_gross'),
                'num_bedrooms': apartment_data.get('num_bedrooms'),
                'num_bathrooms': apartment_data.get('num_bathrooms'),
                'type_view': apartment_data.get('type_view'),
                'direction_door': apartment_data.get('direction_door'),
                'direction_balcony': apartment_data.get('direction_balcony'),
                'price': apartment_data.get('price'),
                'price_early': apartment_data.get('price_early'),
                'price_schedule': apartment_data.get('price_schedule'),
                'price_loan': apartment_data.get('price_loan'),
                'notes': apartment_data.get('notes'),
                'status': apartment_data.get('status'),
                'data_status': apartment_data.get('data_status', 'PENDING'),  # Default to PENDING
                'listing_type': apartment_data.get('listing_type'),
                'phone_number': self.format_phone_number(apartment_data.get('phone_number')),
                'price_rent': apartment_data.get('price_rent'),
                'furnished_status': apartment_data.get('furnished_status'),
                'floor_level_category': apartment_data.get('floor_level_category'),
                'move_in_ready': apartment_data.get('move_in_ready'),
                'includes_transfer_fees': apartment_data.get('includes_transfer_fees'),
                'unit_allocation': 'QUY_CHEO'  # Luôn set mặc định
            }
            
            logger.info(f"🔍 Prepared apartment_record: {apartment_record}")
            
            # Gọi API warehouse để insert (dùng batch-insert với mảng 1 phần tử)
            api_url = f"http://localhost:5000/warehouse/api/warehouse/apartments/batch-insert"

            response = requests.post(api_url, json={'apartments': [apartment_record]}, timeout=30)

            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    apartment_ids = result.get('data', {}).get('apartment_ids', [])
                    apartment_id = apartment_ids[0] if apartment_ids else None
                    logger.info(f"✅ Successfully inserted apartment via API: {apartment_record.get('unit_code', 'N/A')} (ID: {apartment_id})")
                    return apartment_id
                else:
                    logger.error(f"❌ API returned error: {result.get('error')}")
                    return False
            else:
                logger.error(f"❌ API request failed with status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error calling warehouse API: {str(e)}")
            logger.error(f"❌ Error type: {type(e)}")
            logger.error(f"❌ Error details: {e}")
            import traceback
            logger.error(f"❌ Full traceback: {traceback.format_exc()}")
            return False
    
    def get_apartments_list(self, limit: int = 100, offset: int = 0, property_group_id: Optional[int] = None, property_group_slug: Optional[str] = None, unit_type_id: Optional[int] = None, unit_type_slug: Optional[str] = None, listing_type: Optional[str] = None, price_from: Optional[float] = None, price_to: Optional[float] = None, area_from: Optional[float] = None, area_to: Optional[float] = None) -> Dict:
        """
        Lấy danh sách apartments với thông tin property_group và unit_type

        Args:
            limit: Số lượng records tối đa (default: 100)
            offset: Vị trí bắt đầu (default: 0)
            property_group_id: Filter theo property_group_id (optional)
            property_group_slug: Filter theo property_group slug (optional)
            unit_type_id: Filter theo unit_type_id (optional)
            unit_type_slug: Filter theo unit_type slug (optional)
            listing_type: Filter theo listing_type (optional): CAN_THUE, CAN_CHO_THUE, CAN_BAN, CAN_MUA, KHAC
            price_from: Filter giá từ (optional)
            price_to: Filter giá đến (optional)
            area_from: Filter diện tích từ (optional)
            area_to: Filter diện tích đến (optional)

        Returns:
            Dict chứa danh sách apartments và metadata
        """
        connection = None
        try:
            with warehouse_app.app_context():
                connection = self.get_warehouse_db_connection()
                if not connection:
                    return {
                        'success': False,
                        'error': 'Cannot connect to warehouse database',
                        'data': [],
                        'total': 0
                    }
                
                from sqlalchemy import text
                
                # Base query với JOIN để lấy tên property_group và unit_type
                base_query = """
                SELECT
                    a.id,
                    a.property_group,
                    pg.name as property_group_name,
                    a.unit_type,
                    ut.name as unit_type_name,
                    a.unit_code,
                    a.unit_axis,
                    a.unit_floor_number,
                    a.area_land,
                    a.area_construction,
                    a.area_net,
                    a.area_gross,
                    a.num_bedrooms,
                    a.num_bathrooms,
                    a.type_view,
                    a.direction_door,
                    a.direction_balcony,
                    a.price,
                    a.price_early,
                    a.price_schedule,
                    a.price_loan,
                    a.price_rent,
                    a.notes,
                    a.status,
                    a.unit_allocation,
                    a.furnished_status,
                    a.floor_level_category,
                    a.move_in_ready,
                    a.includes_transfer_fees,
                    a.listing_type
                FROM apartments a
                LEFT JOIN property_groups pg ON a.property_group = pg.id
                LEFT JOIN types_unit ut ON a.unit_type = ut.id
                """
                
                # Điều kiện WHERE
                where_conditions = []
                params = {}
                
                if property_group_slug is not None:
                    # Filter theo slug - cần lấy tất cả property groups con (recursive)
                    # Sử dụng recursive CTE để lấy tất cả children và grandchildren
                    # First, get the root property group ID by slug
                    root_query = text("SELECT id FROM property_groups WHERE slug = :slug")
                    root_result = connection.execute(root_query, {'slug': property_group_slug})
                    root_row = root_result.fetchone()
                    
                    if root_row:
                        root_id = root_row[0]
                        # Use recursive CTE to get all descendant property group IDs
                        # MySQL 8.0+ supports recursive CTE
                        recursive_cte = text("""
                        WITH RECURSIVE property_group_tree AS (
                            -- Base case: start with the root property group
                            SELECT id FROM property_groups WHERE id = :root_id
                            UNION ALL
                            -- Recursive case: get all children
                            SELECT pg.id 
                            FROM property_groups pg
                            INNER JOIN property_group_tree pgt ON pg.parent_id = pgt.id
                        )
                        SELECT id FROM property_group_tree
                        """)
                        descendant_result = connection.execute(recursive_cte, {'root_id': root_id})
                        descendant_ids = [row[0] for row in descendant_result.fetchall()]
                        
                        if descendant_ids:
                            # Filter apartments by all descendant property group IDs
                            # Use SQLAlchemy text() with IN clause
                            placeholders = ','.join([f':id{i}' for i in range(len(descendant_ids))])
                            where_conditions.append(f"a.property_group IN ({placeholders})")
                            for i, pg_id in enumerate(descendant_ids):
                                params[f'id{i}'] = pg_id
                        else:
                            # Only the root group itself, no children
                            where_conditions.append("a.property_group = :root_property_group_id")
                            params['root_property_group_id'] = root_id
                    else:
                        # If slug not found, return empty result
                        where_conditions.append("1 = 0")  # Always false condition
                elif property_group_id is not None:
                    where_conditions.append("a.property_group = :property_group_id")
                    params['property_group_id'] = property_group_id
                
                if unit_type_slug is not None:
                    # Filter by unit_type slug - need to get unit_type ID first
                    unit_type_query = text("SELECT id FROM types_unit WHERE slug = :slug")
                    unit_type_result = connection.execute(unit_type_query, {'slug': unit_type_slug})
                    unit_type_row = unit_type_result.fetchone()

                    if unit_type_row:
                        unit_type_id_from_slug = unit_type_row[0]
                        where_conditions.append("a.unit_type = :unit_type_id_from_slug")
                        params['unit_type_id_from_slug'] = unit_type_id_from_slug
                    else:
                        # If slug not found, return empty result
                        where_conditions.append("1 = 0")  # Always false condition
                elif unit_type_id is not None:
                    where_conditions.append("a.unit_type = :unit_type_id")
                    params['unit_type_id'] = unit_type_id
                
                if listing_type is not None:
                    where_conditions.append("a.listing_type = :listing_type")
                    params['listing_type'] = listing_type
                
                if price_from is not None:
                    where_conditions.append("a.price >= :price_from")
                    params['price_from'] = price_from
                
                if price_to is not None:
                    where_conditions.append("a.price <= :price_to")
                    params['price_to'] = price_to
                
                if area_from is not None:
                    where_conditions.append("(a.area_net >= :area_from OR a.area_gross >= :area_from)")
                    params['area_from'] = area_from
                
                if area_to is not None:
                    where_conditions.append("(a.area_net <= :area_to OR a.area_gross <= :area_to)")
                    params['area_to'] = area_to
                
                where_clause = ""
                if where_conditions:
                    where_clause = "WHERE " + " AND ".join(where_conditions)
                
                # Query để đếm tổng số records
                count_query = f"""
                SELECT COUNT(*) as total
                FROM apartments a
                LEFT JOIN property_groups pg ON a.property_group = pg.id
                LEFT JOIN types_unit ut ON a.unit_type = ut.id
                {where_clause}
                """
                
                # Query để lấy data với pagination
                data_query = f"""
                {base_query}
                {where_clause}
                ORDER BY a.id DESC
                LIMIT :limit OFFSET :offset
                """
                
                # Thêm parameters cho pagination
                params['limit'] = limit
                params['offset'] = offset
                
                logger.info(f"Executing apartments list query with params: {params}")
                
                # Đếm tổng số records
                count_result = connection.execute(text(count_query), params)
                total_count = count_result.fetchone()[0]
                
                # Lấy data
                data_result = connection.execute(text(data_query), params)
                apartments = []
                
                for row in data_result:
                    apartment_data = dict(row._mapping)
                    apartments.append(apartment_data)
                
                logger.info(f"Retrieved {len(apartments)} apartments out of {total_count} total")
                
                return {
                    'success': True,
                    'data': apartments,
                    'total': total_count,
                    'limit': limit,
                    'offset': offset,
                    'has_more': (offset + len(apartments)) < total_count
                }
                
        except Exception as e:
            logger.error(f"Error getting apartments list: {e}")
            return {
                'success': False,
                'error': str(e),
                'data': [],
                'total': 0
            }
        finally:
            if connection:
                connection.close()
    
    def get_apartments_by_ids(self, apartment_ids: List[int]) -> Dict:
        """
        Lấy thông tin apartments theo danh sách ID với thông tin property_group và unit_type
        
        Args:
            apartment_ids: Danh sách ID của apartments
            
        Returns:
            Dict chứa danh sách apartments hoặc error
        """
        connection = None
        try:
            with warehouse_app.app_context():
                connection = self.get_warehouse_db_connection()
                if not connection:
                    return {
                        'success': False,
                        'error': 'Cannot connect to warehouse database',
                        'data': []
                    }
                
                if not apartment_ids:
                    return {
                        'success': True,
                        'data': [],
                        'message': 'No apartment IDs provided'
                    }
                
                from sqlalchemy import text
                
                # Tạo placeholder cho IN clause
                placeholders = ','.join([f':id_{i}' for i in range(len(apartment_ids))])
                
                query = f"""
                SELECT 
                    a.id,
                    a.property_group,
                    pg.name as property_group_name,
                    a.unit_type,
                    ut.name as unit_type_name,
                    a.unit_code,
                    a.unit_axis,
                    a.unit_floor_number,
                    a.area_land,
                    a.area_construction,
                    a.area_net,
                    a.area_gross,
                    a.num_bedrooms,
                    a.num_bathrooms,
                    a.type_view,
                    a.direction_door,
                    a.direction_balcony,
                    a.price,
                    a.price_early,
                    a.price_schedule,
                    a.price_loan,
                    a.price_rent,
                    a.notes,
                    a.status,
                    a.data_status,
                    a.unit_allocation,
                    a.listing_type,
                    a.phone_number,
                    a.furnished_status,
                    a.floor_level_category,
                    a.move_in_ready,
                    a.includes_transfer_fees
                FROM apartments a
                LEFT JOIN property_groups pg ON a.property_group = pg.id
                LEFT JOIN types_unit ut ON a.unit_type = ut.id
                WHERE a.id IN ({placeholders})
                ORDER BY a.id
                """
                
                # Tạo parameters dict
                params = {f'id_{i}': apartment_id for i, apartment_id in enumerate(apartment_ids)}
                
                logger.info(f"Getting apartments by IDs: {apartment_ids}")
                
                result = connection.execute(text(query), params)
                apartments = []
                
                for row in result:
                    apartment_data = dict(row._mapping)
                    apartments.append(apartment_data)
                
                logger.info(f"Found {len(apartments)} apartments out of {len(apartment_ids)} requested IDs")
                
                return {
                    'success': True,
                    'data': apartments,
                    'requested_count': len(apartment_ids),
                    'found_count': len(apartments),
                    'missing_ids': [aid for aid in apartment_ids if aid not in [apt['id'] for apt in apartments]]
                }
                    
        except Exception as e:
            logger.error(f"Error getting apartments by IDs: {e}")
            return {
                'success': False,
                'error': str(e),
                'data': []
            }
        finally:
            if connection:
                connection.close()
    
    def get_apartment_by_id(self, apartment_id: int) -> Dict:
        """
        Lấy thông tin apartment theo ID với thông tin property_group và unit_type
        (Wrapper method cho backward compatibility)
        
        Args:
            apartment_id: ID của apartment
            
        Returns:
            Dict chứa thông tin apartment hoặc error
        """
        result = self.get_apartments_by_ids([apartment_id])
        
        if result['success'] and result['data']:
            return {
                'success': True,
                'data': result['data'][0]
            }
        elif result['success'] and not result['data']:
            return {
                'success': False,
                'error': f'Apartment with ID {apartment_id} not found'
            }
        else:
            return result

    def update_apartment_data_status(self, apartment_id: int, data_status: str) -> Dict:
        """
        Cập nhật data_status của apartment (REVIEWING | PENDING | APPROVED).
        """
        if data_status not in ('REVIEWING', 'PENDING', 'APPROVED'):
            return {'success': False, 'error': 'data_status must be REVIEWING, PENDING or APPROVED'}
        connection = None
        try:
            with warehouse_app.app_context():
                connection = self.get_warehouse_db_connection()
                if not connection:
                    return {'success': False, 'error': 'Cannot connect to warehouse database'}
                from sqlalchemy import text
                q = text("UPDATE apartments SET data_status = :data_status WHERE id = :apartment_id")
                result = connection.execute(q, {"data_status": data_status, "apartment_id": apartment_id})
                connection.commit()
                if result.rowcount == 0:
                    return {'success': False, 'error': f'Apartment {apartment_id} not found'}
                logger.info(f"Updated apartment {apartment_id} data_status to {data_status}")
                return {'success': True, 'apartment_id': apartment_id, 'data_status': data_status}
        except Exception as e:
            if connection:
                connection.rollback()
            logger.error(f"Error updating apartment data_status: {e}")
            return {'success': False, 'error': str(e)}
        finally:
            if connection:
                connection.close()

    def delete_apartment(self, apartment_id: int) -> Dict:
        """
        Xóa apartment khỏi bảng apartments (hard delete).
        """
        connection = None
        try:
            with warehouse_app.app_context():
                connection = self.get_warehouse_db_connection()
                if not connection:
                    return {'success': False, 'error': 'Cannot connect to warehouse database'}
                from sqlalchemy import text
                q = text("DELETE FROM apartments WHERE id = :apartment_id")
                result = connection.execute(q, {"apartment_id": apartment_id})
                connection.commit()
                if result.rowcount == 0:
                    return {'success': False, 'error': f'Apartment {apartment_id} not found'}
                logger.info(f"Deleted apartment {apartment_id}")
                return {'success': True, 'apartment_id': apartment_id}
        except Exception as e:
            if connection:
                connection.rollback()
            logger.error(f"Error deleting apartment: {e}")
            return {'success': False, 'error': str(e)}
        finally:
            if connection:
                connection.close()

    def search_apartments(self, search_query: str, limit: int = 50, offset: int = 0) -> Dict:
        """
        Tìm kiếm apartments với từ khóa
        
        Args:
            search_query: Từ khóa tìm kiếm (unit_code, property_group_name, unit_type_name)
            limit: Số lượng records tối đa (default: 50)
            offset: Vị trí bắt đầu (default: 0)
            
        Returns:
            Dict chứa danh sách apartments và metadata
        """
        connection = None
        try:
            with warehouse_app.app_context():
                connection = self.get_warehouse_db_connection()
                if not connection:
                    return {
                        'success': False,
                        'error': 'Cannot connect to warehouse database',
                        'data': [],
                        'total': 0
                    }
                
                from sqlalchemy import text
                
                # Query với search conditions
                search_conditions = """
                WHERE (
                    a.unit_code LIKE :search_query OR
                    pg.name LIKE :search_query OR
                    ut.name LIKE :search_query OR
                    a.unit_axis LIKE :search_query OR
                    a.notes LIKE :search_query
                )
                """
                
                # Base query với JOIN để lấy tên property_group và unit_type
                base_query = """
                SELECT 
                    a.id,
                    a.property_group,
                    pg.name as property_group_name,
                    a.unit_type,
                    ut.name as unit_type_name,
                    a.unit_code,
                    a.unit_axis,
                    a.unit_floor_number,
                    a.area_land,
                    a.area_construction,
                    a.area_net,
                    a.area_gross,
                    a.num_bedrooms,
                    a.num_bathrooms,
                    a.type_view,
                    a.direction_door,
                    a.direction_balcony,
                    a.price,
                    a.price_early,
                    a.price_schedule,
                    a.price_loan,
                    a.price_rent,
                    a.notes,
                    a.status,
                    a.unit_allocation,
                    a.furnished_status,
                    a.floor_level_category,
                    a.move_in_ready,
                    a.includes_transfer_fees
                FROM apartments a
                LEFT JOIN property_groups pg ON a.property_group = pg.id
                LEFT JOIN types_unit ut ON a.unit_type = ut.id
                """
                
                # Query để đếm tổng số records
                count_query = f"""
                SELECT COUNT(*) as total
                FROM apartments a
                LEFT JOIN property_groups pg ON a.property_group = pg.id
                LEFT JOIN types_unit ut ON a.unit_type = ut.id
                {search_conditions}
                """
                
                # Query để lấy data với pagination
                data_query = f"""
                {base_query}
                {search_conditions}
                ORDER BY a.id DESC
                LIMIT :limit OFFSET :offset
                """
                
                # Parameters
                search_pattern = f"%{search_query}%"
                params = {
                    'search_query': search_pattern,
                    'limit': limit,
                    'offset': offset
                }
                
                logger.info(f"Executing apartments search query with params: {params}")
                
                # Đếm tổng số records
                count_result = connection.execute(text(count_query), params)
                total_count = count_result.fetchone()[0]
                
                # Lấy data
                data_result = connection.execute(text(data_query), params)
                apartments = []
                
                for row in data_result:
                    apartment_data = dict(row._mapping)
                    apartments.append(apartment_data)
                
                logger.info(f"Found {len(apartments)} apartments matching '{search_query}' out of {total_count} total")
                
                return {
                    'success': True,
                    'data': apartments,
                    'total': total_count,
                    'limit': limit,
                    'offset': offset,
                    'has_more': (offset + len(apartments)) < total_count,
                    'search_query': search_query
                }
                
        except Exception as e:
            logger.error(f"Error searching apartments: {e}")
            return {
                'success': False,
                'error': str(e),
                'data': [],
                'total': 0
            }
        finally:
            if connection:
                connection.close()


# Global instance
warehouse_service = WarehouseDatabaseService()
