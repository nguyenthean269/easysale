"""
Warehouse API Routes - Insert multiple apartment items
"""

from flask import Blueprint, request, jsonify
import logging
import pymysql
import os
from typing import List, Dict, Any

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
        'notes': 'str',
        'status': 'str',
        'unit_allocation': 'str'
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
    
    if cleaned_item.get('unit_allocation') not in ['QUY_CHEO', 'QUY_DOI', None]:
        cleaned_item['unit_allocation'] = 'QUY_CHEO'  # Default value
    
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
                price, price_early, price_schedule, price_loan,
                notes, status, unit_allocation
            ) VALUES (
                %(property_group)s, %(unit_type)s, %(unit_code)s, %(unit_axis)s, %(unit_floor_number)s,
                %(area_land)s, %(area_construction)s, %(area_net)s, %(area_gross)s,
                %(num_bedrooms)s, %(num_bathrooms)s, %(type_view)s,
                %(direction_door)s, %(direction_balcony)s,
                %(price)s, %(price_early)s, %(price_schedule)s, %(price_loan)s,
                %(notes)s, %(status)s, %(unit_allocation)s
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
                price, price_early, price_schedule, price_loan,
                notes, status, unit_allocation
            ) VALUES (
                %(property_group)s, %(unit_type)s, %(unit_code)s, %(unit_axis)s, %(unit_floor_number)s,
                %(area_land)s, %(area_construction)s, %(area_net)s, %(area_gross)s,
                %(num_bedrooms)s, %(num_bathrooms)s, %(type_view)s,
                %(direction_door)s, %(direction_balcony)s,
                %(price)s, %(price_early)s, %(price_schedule)s, %(price_loan)s,
                %(notes)s, %(status)s, %(unit_allocation)s
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
