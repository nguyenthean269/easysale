"""
Warehouse API Routes - Insert multiple apartment items
"""

from flask import Blueprint, request, jsonify
import logging
import pymysql
import os
from typing import List, Dict, Any
from services.warehouse_database_service import warehouse_service

logger = logging.getLogger(__name__)

# Tạo blueprint
warehouse_bp = Blueprint('warehouse', __name__)

def get_warehouse_connection():
    """Tạo kết nối database warehouse"""
    try:
        connection = pymysql.connect(
            host=os.getenv('DB_WAREHOUSE_HOST', '103.6.234.59'),
            port=int(os.getenv('DB_WAREHOUSE_PORT', '6033')),
            user=os.getenv('DB_WAREHOUSE_USER', 'root'),
            password=os.getenv('DB_WAREHOUSE_PASSWORD', ''),
            database=os.getenv('DB_WAREHOUSE_NAME', 'warehouse'),
            charset='utf8mb4',
            autocommit=False
        )
        return connection
    except Exception as e:
        logger.error(f"Error connecting to warehouse database: {e}")
        return None

def validate_apartment_item(item: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate và clean apartment item data
    Thiếu trường để NULL, thừa trường bỏ qua
    """
    # Danh sách các trường hợp lệ trong bảng apartments
    valid_fields = {
        'property_group': 'int',
        'unit_type': 'int', 
        'unit_code': 'str',
        'unit_axis': 'str',
        'unit_floor_number': 'int',
        'area_land': 'float',
        'area_construction': 'float',
        'area_net': 'float',
        'area_gross': 'float',
        'num_bedrooms': 'int',
        'num_bathrooms': 'int',
        'type_view': 'str',
        'direction_door': 'str',
        'direction_balcony': 'str',
        'price': 'float',
        'price_early': 'float',
        'price_schedule': 'float',
        'price_loan': 'float',
        'price_rent': 'float',
        'notes': 'str',
        'status': 'str',
        'data_status': 'str',
        'unit_allocation': 'str',
        'listing_type': 'str',
        'phone_number': 'str'
    }
    
    cleaned_item = {}
    
    for field, field_type in valid_fields.items():
        if field in item:
            value = item[field]
            
            # Convert và validate theo type
            if value is None or value == '' or value == 'null':
                cleaned_item[field] = None
            elif field_type == 'int':
                try:
                    cleaned_item[field] = int(float(str(value).replace('m2', '').replace('tỷ', '').replace('triệu', '').strip()))
                except (ValueError, TypeError):
                    cleaned_item[field] = None
            elif field_type == 'float':
                try:
                    cleaned_item[field] = float(str(value).replace('m2', '').replace('tỷ', '').replace('triệu', '').strip())
                except (ValueError, TypeError):
                    cleaned_item[field] = None
            elif field_type == 'str':
                cleaned_item[field] = str(value) if value else None
            else:
                cleaned_item[field] = value
        else:
            # Thiếu trường thì để NULL
            cleaned_item[field] = None
    
    # Validate enum values
    if cleaned_item.get('direction_door') not in ['D', 'T', 'N', 'B', 'DB', 'DN', 'TB', 'TN', None]:
        cleaned_item['direction_door'] = None
    
    if cleaned_item.get('direction_balcony') not in ['D', 'T', 'N', 'B', 'DB', 'DN', 'TB', 'TN', None]:
        cleaned_item['direction_balcony'] = None
    
    if cleaned_item.get('status') not in ['CHUA_BAN', 'DA_LOCK', 'DA_COC', 'DA_BAN', None]:
        cleaned_item['status'] = None
    
    if cleaned_item.get('data_status') not in ['REVIEWING', 'PENDING', 'APPROVED', None]:
        cleaned_item['data_status'] = 'PENDING'  # Default value
    
    if cleaned_item.get('unit_allocation') not in ['QUY_CHEO', 'QUY_DOI', None]:
        cleaned_item['unit_allocation'] = 'QUY_CHEO'  # Default value
    
    # Validate listing_type enum values
    if cleaned_item.get('listing_type') not in ['CAN_THUE', 'CAN_CHO_THUE', 'CAN_BAN', 'CAN_MUA', 'KHAC', None]:
        cleaned_item['listing_type'] = None
    
    return cleaned_item

@warehouse_bp.route('/api/warehouse/apartments/batch-insert', methods=['POST'])
def batch_insert_apartments():
    """
    Insert mảng các apartment items vào warehouse
    Thiếu trường để NULL, thừa trường bỏ qua
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided'
            }), 400
        
        apartments = data.get('apartments', [])
        
        if not isinstance(apartments, list):
            return jsonify({
                'success': False,
                'error': 'apartments must be an array'
            }), 400
        
        if not apartments:
            return jsonify({
                'success': False,
                'error': 'apartments array is empty'
            }), 400
        
        logger.info(f"Processing batch insert for {len(apartments)} apartments")
        
        # Validate và clean data
        cleaned_apartments = []
        for i, apartment in enumerate(apartments):
            try:
                cleaned_item = validate_apartment_item(apartment)
                cleaned_apartments.append(cleaned_item)
                logger.info(f"Validated apartment {i+1}: {cleaned_item.get('unit_code', 'N/A')}")
            except Exception as e:
                logger.error(f"Error validating apartment {i+1}: {e}")
                return jsonify({
                    'success': False,
                    'error': f'Error validating apartment {i+1}: {str(e)}'
                }), 400
        
        # Insert vào database
        connection = get_warehouse_connection()
        if not connection:
            return jsonify({
                'success': False,
                'error': 'Failed to connect to warehouse database'
            }), 500
        
        try:
            cursor = connection.cursor()
            
            # Prepare INSERT statement
            insert_sql = """
            INSERT INTO apartments (
                property_group, unit_type, unit_code, unit_axis, unit_floor_number,
                area_land, area_construction, area_net, area_gross,
                num_bedrooms, num_bathrooms, type_view,
                direction_door, direction_balcony,
                price, price_early, price_schedule, price_loan, price_rent,
                notes, status, unit_allocation, listing_type, phone_number
            ) VALUES (
                %(property_group)s, %(unit_type)s, %(unit_code)s, %(unit_axis)s, %(unit_floor_number)s,
                %(area_land)s, %(area_construction)s, %(area_net)s, %(area_gross)s,
                %(num_bedrooms)s, %(num_bathrooms)s, %(type_view)s,
                %(direction_door)s, %(direction_balcony)s,
                %(price)s, %(price_early)s, %(price_schedule)s, %(price_loan)s, %(price_rent)s,
                %(notes)s, %(status)s, %(unit_allocation)s, %(listing_type)s, %(phone_number)s
            )
            """
            
            # Execute batch insert
            inserted_count = 0
            errors = []
            
            for i, apartment in enumerate(cleaned_apartments):
                try:
                    cursor.execute(insert_sql, apartment)
                    inserted_count += 1
                    logger.info(f"Inserted apartment {i+1}: {apartment.get('unit_code', 'N/A')}")
                except Exception as e:
                    error_msg = f"Error inserting apartment {i+1} ({apartment.get('unit_code', 'N/A')}): {str(e)}"
                    logger.error(error_msg)
                    errors.append(error_msg)
            
            # Commit transaction
            connection.commit()
            
            logger.info(f"Batch insert completed: {inserted_count} inserted, {len(errors)} errors")
            
            return jsonify({
                'success': True,
                'data': {
                    'total_items': len(apartments),
                    'inserted_count': inserted_count,
                    'error_count': len(errors),
                    'errors': errors
                },
                'message': f'Successfully inserted {inserted_count}/{len(apartments)} apartments'
            })
            
        except Exception as e:
            connection.rollback()
            logger.error(f"Database error during batch insert: {e}")
            return jsonify({
                'success': False,
                'error': f'Database error: {str(e)}'
            }), 500
            
        finally:
            cursor.close()
            connection.close()
        
    except Exception as e:
        logger.error(f"Error in batch_insert_apartments: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@warehouse_bp.route('/api/warehouse/apartments/single-insert', methods=['POST'])
def single_insert_apartment():
    """
    Insert một apartment item vào warehouse
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided'
            }), 400
        
        # Validate và clean data
        cleaned_apartment = validate_apartment_item(data)
        
        logger.info(f"Processing single insert for apartment: {cleaned_apartment.get('unit_code', 'N/A')}")
        
        # Insert vào database
        connection = get_warehouse_connection()
        if not connection:
            return jsonify({
                'success': False,
                'error': 'Failed to connect to warehouse database'
            }), 500
        
        try:
            cursor = connection.cursor()
            
            # Prepare INSERT statement
            insert_sql = """
            INSERT INTO apartments (
                property_group, unit_type, unit_code, unit_axis, unit_floor_number,
                area_land, area_construction, area_net, area_gross,
                num_bedrooms, num_bathrooms, type_view,
                direction_door, direction_balcony,
                price, price_early, price_schedule, price_loan, price_rent,
                notes, status, unit_allocation, listing_type, phone_number
            ) VALUES (
                %(property_group)s, %(unit_type)s, %(unit_code)s, %(unit_axis)s, %(unit_floor_number)s,
                %(area_land)s, %(area_construction)s, %(area_net)s, %(area_gross)s,
                %(num_bedrooms)s, %(num_bathrooms)s, %(type_view)s,
                %(direction_door)s, %(direction_balcony)s,
                %(price)s, %(price_early)s, %(price_schedule)s, %(price_loan)s, %(price_rent)s,
                %(notes)s, %(status)s, %(unit_allocation)s, %(listing_type)s, %(phone_number)s
            )
            """
            
            cursor.execute(insert_sql, cleaned_apartment)
            connection.commit()
            
            apartment_id = cursor.lastrowid
            
            logger.info(f"Successfully inserted apartment: {cleaned_apartment.get('unit_code', 'N/A')} (ID: {apartment_id})")
            
            return jsonify({
                'success': True,
                'data': {
                    'apartment_id': apartment_id,
                    'apartment_data': cleaned_apartment
                },
                'message': f'Successfully inserted apartment: {cleaned_apartment.get("unit_code", "N/A")}'
            })
            
        except Exception as e:
            connection.rollback()
            logger.error(f"Database error during single insert: {e}")
            return jsonify({
                'success': False,
                'error': f'Database error: {str(e)}'
            }), 500
            
        finally:
            cursor.close()
            connection.close()
        
    except Exception as e:
        logger.error(f"Error in single_insert_apartment: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@warehouse_bp.route('/api/warehouse/apartments/test', methods=['GET'])
def test_warehouse_connection():
    """Test warehouse database connection"""
    try:
        connection = get_warehouse_connection()
        if not connection:
            return jsonify({
                'success': False,
                'error': 'Failed to connect to warehouse database'
            }), 500
        
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM apartments")
        count = cursor.fetchone()[0]
        
        cursor.close()
        connection.close()
        
        return jsonify({
            'success': True,
            'data': {
                'connection_status': 'OK',
                'apartments_count': count
            },
            'message': 'Warehouse database connection successful'
        })
        
    except Exception as e:
        logger.error(f"Error testing warehouse connection: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@warehouse_bp.route('/api/warehouse/apartments/list', methods=['GET'])
def get_apartments_list():
    """
    Lấy danh sách apartments với thông tin property_group và unit_type
    Query parameters:
    - limit: Số lượng records tối đa (default: 100)
    - offset: Vị trí bắt đầu (default: 0)
    - property_group_id: Filter theo property_group_id (optional)
    - unit_type_id: Filter theo unit_type_id (optional)
    """
    try:
        # Lấy query parameters
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)
        property_group_id = request.args.get('property_group_id', type=int)
        unit_type_id = request.args.get('unit_type_id', type=int)
        
        # Validate parameters
        if limit <= 0 or limit > 1000:
            return jsonify({
                'success': False,
                'error': 'limit must be between 1 and 1000'
            }), 400
        
        if offset < 0:
            return jsonify({
                'success': False,
                'error': 'offset must be >= 0'
            }), 400
        
        logger.info(f"Getting apartments list: limit={limit}, offset={offset}, property_group_id={property_group_id}, unit_type_id={unit_type_id}")
        
        # Gọi service method
        result = warehouse_service.get_apartments_list(
            limit=limit,
            offset=offset,
            property_group_id=property_group_id,
            unit_type_id=unit_type_id
        )
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 500
            
    except Exception as e:
        logger.error(f"Error in get_apartments_list: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@warehouse_bp.route('/api/warehouse/apartments/by-ids', methods=['POST'])
def get_apartments_by_ids():
    """
    Lấy thông tin apartments theo danh sách ID với thông tin property_group và unit_type
    Body: {"ids": [1, 2, 3, ...]}
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided'
            }), 400
        
        apartment_ids = data.get('ids', [])
        
        if not isinstance(apartment_ids, list):
            return jsonify({
                'success': False,
                'error': 'ids must be an array'
            }), 400
        
        if not apartment_ids:
            return jsonify({
                'success': False,
                'error': 'ids array cannot be empty'
            }), 400
        
        # Validate that all IDs are integers
        try:
            apartment_ids = [int(id) for id in apartment_ids]
        except (ValueError, TypeError):
            return jsonify({
                'success': False,
                'error': 'All IDs must be integers'
            }), 400
        
        logger.info(f"Getting apartments by IDs: {apartment_ids}")
        
        # Gọi service method
        result = warehouse_service.get_apartments_by_ids(apartment_ids)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 500
            
    except Exception as e:
        logger.error(f"Error in get_apartments_by_ids: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@warehouse_bp.route('/api/warehouse/apartments/<int:apartment_id>', methods=['GET'])
def get_apartment_by_id(apartment_id):
    """
    Lấy thông tin apartment theo ID với thông tin property_group và unit_type
    """
    try:
        logger.info(f"Getting apartment by ID: {apartment_id}")
        
        # Gọi service method
        result = warehouse_service.get_apartment_by_id(apartment_id)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 404
            
    except Exception as e:
        logger.error(f"Error in get_apartment_by_id: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@warehouse_bp.route('/api/warehouse/apartments/search', methods=['GET'])
def search_apartments():
    """
    Tìm kiếm apartments với các điều kiện
    Query parameters:
    - q: Từ khóa tìm kiếm (unit_code, property_group_name, unit_type_name)
    - limit: Số lượng records tối đa (default: 50)
    - offset: Vị trí bắt đầu (default: 0)
    """
    try:
        # Lấy query parameters
        search_query = request.args.get('q', '').strip()
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Validate parameters
        if limit <= 0 or limit > 500:
            return jsonify({
                'success': False,
                'error': 'limit must be between 1 and 500'
            }), 400
        
        if offset < 0:
            return jsonify({
                'success': False,
                'error': 'offset must be >= 0'
            }), 400
        
        if not search_query:
            return jsonify({
                'success': False,
                'error': 'search query parameter "q" is required'
            }), 400
        
        logger.info(f"Searching apartments: query='{search_query}', limit={limit}, offset={offset}")
        
        # Gọi service method với search
        result = warehouse_service.search_apartments(
            search_query=search_query,
            limit=limit,
            offset=offset
        )
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 500
            
    except Exception as e:
        logger.error(f"Error in search_apartments: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
