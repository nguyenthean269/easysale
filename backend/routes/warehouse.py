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
    # Danh sách các trường hợp lệ trong bảng apartments (khớp với DB schema)
    valid_fields = {
        'property_group': 'int',
        'unit_type': 'int',
        'unit_code': 'str',
        'unit_axis': 'str',
        'unit_floor_number': 'str',       # char(255) trong DB
        'area_land': 'float',
        'area_construction': 'float',
        'area_net': 'float',
        'area_gross': 'float',
        'num_bedrooms': 'int',
        'num_bathrooms': 'int',
        'type_view': 'int',               # int FK to types_view trong DB
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
        'phone_number': 'str',
        'furnished_status': 'str',
        'floor_level_category': 'str',
        'move_in_ready': 'bool',
        'includes_transfer_fees': 'bool',
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
            elif field_type == 'bool':
                if isinstance(value, bool):
                    cleaned_item[field] = int(value)
                elif isinstance(value, int):
                    cleaned_item[field] = 1 if value else 0
                else:
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
    
    # unit_allocation là SET type, validate từng giá trị
    valid_allocations = {'QUY_DOC_QUYEN', 'QUY_AN', 'QUY_CHEO', 'QUY_THUONG'}
    if cleaned_item.get('unit_allocation'):
        parts = [p.strip() for p in cleaned_item['unit_allocation'].split(',')]
        valid_parts = [p for p in parts if p in valid_allocations]
        cleaned_item['unit_allocation'] = ','.join(valid_parts) if valid_parts else 'QUY_CHEO'

    # Validate listing_type enum values
    if cleaned_item.get('listing_type') not in ['CAN_THUE', 'CAN_CHO_THUE', 'CAN_BAN', 'CAN_MUA', 'KHAC', None]:
        cleaned_item['listing_type'] = None

    # Validate furnished_status enum
    if cleaned_item.get('furnished_status') not in ['FULL', 'PARTIAL', 'UNFURNISHED', None]:
        cleaned_item['furnished_status'] = None

    # Validate floor_level_category enum
    if cleaned_item.get('floor_level_category') not in ['LOW', 'MEDIUM', 'HIGH', None]:
        cleaned_item['floor_level_category'] = None

    # data_status là NOT NULL, default PENDING
    if not cleaned_item.get('data_status'):
        cleaned_item['data_status'] = 'PENDING'

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
                notes, status, data_status, unit_allocation, listing_type, phone_number,
                furnished_status, floor_level_category, move_in_ready, includes_transfer_fees
            ) VALUES (
                %(property_group)s, %(unit_type)s, %(unit_code)s, %(unit_axis)s, %(unit_floor_number)s,
                %(area_land)s, %(area_construction)s, %(area_net)s, %(area_gross)s,
                %(num_bedrooms)s, %(num_bathrooms)s, %(type_view)s,
                %(direction_door)s, %(direction_balcony)s,
                %(price)s, %(price_early)s, %(price_schedule)s, %(price_loan)s, %(price_rent)s,
                %(notes)s, %(status)s, %(data_status)s, %(unit_allocation)s, %(listing_type)s, %(phone_number)s,
                %(furnished_status)s, %(floor_level_category)s, %(move_in_ready)s, %(includes_transfer_fees)s
            )
            """
            
            # Execute batch insert using executemany
            cursor.executemany(insert_sql, cleaned_apartments)
            connection.commit()

            inserted_count = cursor.rowcount
            # lastrowid trả về ID của record đầu tiên, các record sau có ID liên tiếp
            first_id = cursor.lastrowid
            apartment_ids = list(range(first_id, first_id + inserted_count)) if first_id else []
            logger.info(f"Batch insert completed: {inserted_count} inserted, IDs: {apartment_ids}")

            return jsonify({
                'success': True,
                'data': {
                    'total_items': len(apartments),
                    'inserted_count': inserted_count,
                    'apartment_ids': apartment_ids
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
    - property_group_slug: Filter theo property_group slug (optional)
    - unit_type_id: Filter theo unit_type_id (optional)
    - unit_type_slug: Filter theo unit_type slug (optional)
    - listing_type: Filter theo listing_type (optional): CAN_THUE, CAN_CHO_THUE, CAN_BAN, CAN_MUA, KHAC
    - price_from: Filter giá từ (optional)
    - price_to: Filter giá đến (optional)
    - area_from: Filter diện tích từ (optional)
    - area_to: Filter diện tích đến (optional)
    """
    try:
        # Lấy query parameters
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)
        property_group_id = request.args.get('property_group_id', type=int)
        property_group_slug = request.args.get('property_group_slug', type=str)
        unit_type_id = request.args.get('unit_type_id', type=int)
        unit_type_slug = request.args.get('unit_type_slug', type=str)
        listing_type = request.args.get('listing_type', type=str)
        price_from = request.args.get('price_from', type=float)
        price_to = request.args.get('price_to', type=float)
        area_from = request.args.get('area_from', type=float)
        area_to = request.args.get('area_to', type=float)
        
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
        
        if listing_type and listing_type not in ['CAN_THUE', 'CAN_CHO_THUE', 'CAN_BAN', 'CAN_MUA', 'KHAC']:
            return jsonify({
                'success': False,
                'error': 'listing_type must be one of: CAN_THUE, CAN_CHO_THUE, CAN_BAN, CAN_MUA, KHAC'
            }), 400
        
        logger.info(f"Getting apartments list: limit={limit}, offset={offset}, property_group_id={property_group_id}, property_group_slug={property_group_slug}, unit_type_id={unit_type_id}, unit_type_slug={unit_type_slug}, listing_type={listing_type}, price_from={price_from}, price_to={price_to}, area_from={area_from}, area_to={area_to}")

        # Gọi service method
        result = warehouse_service.get_apartments_list(
            limit=limit,
            offset=offset,
            property_group_id=property_group_id,
            property_group_slug=property_group_slug,
            unit_type_id=unit_type_id,
            unit_type_slug=unit_type_slug,
            listing_type=listing_type,
            price_from=price_from,
            price_to=price_to,
            area_from=area_from,
            area_to=area_to
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

@warehouse_bp.route('/api/warehouse/apartments/<int:apartment_id>/data-status', methods=['PATCH'])
def update_apartment_data_status(apartment_id):
    """
    Cập nhật data_status của apartment (REVIEWING | PENDING | APPROVED).
    Body: {"data_status": "APPROVED"}
    """
    try:
        data = request.get_json() or {}
        data_status = data.get('data_status')
        if not data_status or data_status not in ('REVIEWING', 'PENDING', 'APPROVED'):
            return jsonify({
                'success': False,
                'error': 'data_status is required and must be REVIEWING, PENDING or APPROVED'
            }), 400
        result = warehouse_service.update_apartment_data_status(apartment_id, data_status)
        if result.get('success'):
            return jsonify(result)
        return jsonify(result), 404 if 'not found' in result.get('error', '').lower() else 500
    except Exception as e:
        logger.error(f"Error in update_apartment_data_status: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@warehouse_bp.route('/api/warehouse/apartments/<int:apartment_id>', methods=['DELETE'])
def delete_apartment(apartment_id):
    """Xóa apartment khỏi warehouse (hard delete)."""
    try:
        result = warehouse_service.delete_apartment(apartment_id)
        if result.get('success'):
            return jsonify(result)
        return jsonify(result), 404 if 'not found' in result.get('error', '').lower() else 500
    except Exception as e:
        logger.error(f"Error in delete_apartment: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

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

@warehouse_bp.route('/api/warehouse/unit-types', methods=['GET'])
def get_unit_types():
    """
    Lấy danh sách unit types
    """
    try:
        connection = get_warehouse_connection()
        if not connection:
            return jsonify({
                'success': False,
                'error': 'Database connection failed'
            }), 500

        try:
            cursor = connection.cursor(pymysql.cursors.DictCursor)

            # Check if slug column exists
            cursor.execute("SHOW COLUMNS FROM types_unit LIKE 'slug'")
            has_slug = cursor.fetchone() is not None

            if has_slug:
                query = """
                    SELECT id, name, slug
                    FROM types_unit
                    ORDER BY name
                """
            else:
                query = """
                    SELECT id, name
                    FROM types_unit
                    ORDER BY name
                """

            cursor.execute(query)
            unit_types = cursor.fetchall()
            cursor.close()

            result = []
            for unit_type in unit_types:
                result.append({
                    'id': unit_type['id'],
                    'name': unit_type['name'],
                    'slug': unit_type.get('slug') if has_slug else None
                })

            return jsonify({
                'success': True,
                'data': result,
                'count': len(result)
            })

        finally:
            connection.close()

    except Exception as e:
        logger.error(f"Error in get_unit_types: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@warehouse_bp.route('/api/warehouse/property-groups', methods=['GET'])
def get_property_groups():
    """
    Lấy danh sách property groups theo parent_id hoặc slug
    Query parameters:
    - parent_id: ID của parent group (optional, None để lấy root groups)
    - slug: Slug của property group để lấy children (optional)
    """
    try:
        # Lấy query parameters
        parent_id = request.args.get('parent_id', type=int)
        slug = request.args.get('slug', type=str)
        
        connection = get_warehouse_connection()
        if not connection:
            return jsonify({
                'success': False,
                'error': 'Database connection failed'
            }), 500
        
        try:
            cursor = connection.cursor(pymysql.cursors.DictCursor)
            
            # Query property groups với join types_group để lấy type name
            if slug:
                # Lấy property group theo slug
                query = """
                    SELECT pg.id, pg.name, pg.description, pg.thumbnail, pg.slug,
                           pg.parent_id, pg.group_type, tg.name as group_type_name
                    FROM property_groups pg
                    LEFT JOIN types_group tg ON pg.group_type = tg.id
                    WHERE pg.slug = %s
                    ORDER BY pg.name
                    LIMIT 1
                """
                cursor.execute(query, (slug,))
                current_group = cursor.fetchone()

                if current_group:
                    # Lấy children của property group này
                    query = """
                        SELECT pg.id, pg.name, pg.description, pg.thumbnail, pg.slug,
                               pg.parent_id, pg.group_type, tg.name as group_type_name
                        FROM property_groups pg
                        LEFT JOIN types_group tg ON pg.group_type = tg.id
                        WHERE pg.parent_id = %s
                        ORDER BY pg.name
                    """
                    cursor.execute(query, (current_group['id'],))
                    children = cursor.fetchall()

                    # Lấy tất cả các cấp cha (parents hierarchy)
                    parents = []
                    current_parent_id = current_group['parent_id']
                    while current_parent_id is not None:
                        query = """
                            SELECT pg.id, pg.name, pg.description, pg.thumbnail, pg.slug,
                                   pg.parent_id, pg.group_type, tg.name as group_type_name
                            FROM property_groups pg
                            LEFT JOIN types_group tg ON pg.group_type = tg.id
                            WHERE pg.id = %s
                        """
                        cursor.execute(query, (current_parent_id,))
                        parent = cursor.fetchone()
                        if parent:
                            parents.insert(0, {  # Insert at beginning to maintain order from root to current
                                'id': parent['id'],
                                'name': parent['name'],
                                'description': parent['description'],
                                'thumbnail': parent['thumbnail'],
                                'slug': parent.get('slug'),
                                'parent_id': parent['parent_id'],
                                'group_type': parent['group_type'],
                                'group_type_name': parent['group_type_name']
                            })
                            current_parent_id = parent['parent_id']
                        else:
                            break

                    cursor.close()

                    # Convert current group to dict
                    current_result = {
                        'id': current_group['id'],
                        'name': current_group['name'],
                        'description': current_group['description'],
                        'thumbnail': current_group['thumbnail'],
                        'slug': current_group.get('slug'),
                        'parent_id': current_group['parent_id'],
                        'group_type': current_group['group_type'],
                        'group_type_name': current_group['group_type_name']
                    }

                    # Convert children to list of dicts
                    children_result = []
                    for child in children:
                        children_result.append({
                            'id': child['id'],
                            'name': child['name'],
                            'description': child['description'],
                            'thumbnail': child['thumbnail'],
                            'slug': child.get('slug'),
                            'parent_id': child['parent_id'],
                            'group_type': child['group_type'],
                            'group_type_name': child['group_type_name']
                        })

                    return jsonify({
                        'success': True,
                        'current': current_result,
                        'parents': parents,
                        'data': children_result,
                        'count': len(children_result)
                    })
                else:
                    # Slug not found
                    cursor.close()
                    return jsonify({
                        'success': True,
                        'current': None,
                        'parents': [],
                        'data': [],
                        'count': 0
                    })
            elif parent_id is None:
                query = """
                    SELECT pg.id, pg.name, pg.description, pg.thumbnail, pg.slug,
                           pg.parent_id, pg.group_type, tg.name as group_type_name
                    FROM property_groups pg 
                    LEFT JOIN types_group tg ON pg.group_type = tg.id 
                    WHERE pg.parent_id IS NULL
                    ORDER BY pg.name
                """
                cursor.execute(query)
            else:
                query = """
                    SELECT pg.id, pg.name, pg.description, pg.thumbnail, pg.slug,
                           pg.parent_id, pg.group_type, tg.name as group_type_name
                    FROM property_groups pg 
                    LEFT JOIN types_group tg ON pg.group_type = tg.id 
                    WHERE pg.parent_id = %s
                    ORDER BY pg.name
                """
                cursor.execute(query, (parent_id,))
            
            groups = cursor.fetchall()
            cursor.close()
            
            # Convert to list of dicts
            result = []
            for group in groups:
                result.append({
                    'id': group['id'],
                    'name': group['name'],
                    'description': group['description'],
                    'thumbnail': group['thumbnail'],
                    'slug': group.get('slug'),
                    'parent_id': group['parent_id'],
                    'group_type': group['group_type'],
                    'group_type_name': group['group_type_name']
                })
            
            return jsonify({
                'success': True,
                'data': result,
                'count': len(result)
            })
            
        finally:
            connection.close()
            
    except Exception as e:
        logger.error(f"Error in get_property_groups: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
