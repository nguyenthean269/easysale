from typing import List, Optional
import json


class PropertyService:
    """Service để xử lý các thao tác liên quan đến property groups"""
    
    @staticmethod
    def get_property_tree_with_sql(root_id: int, db_connection) -> str:
        """
        Lấy danh sách tree property groups sử dụng raw SQL
        
        Args:
            root_id (int): ID của group root
            db_connection: Database connection
            
        Returns:
            str: Chuỗi tree theo định dạng
        """
        try:
            # Lấy root group với join types_group để lấy tiền tố và description
            cursor = db_connection.cursor()
            cursor.execute("""
                SELECT pg.id, pg.name, pg.description, tg.name as type_name 
                FROM property_groups pg 
                LEFT JOIN types_group tg ON pg.group_type = tg.id 
                WHERE pg.id = %s
            """, (root_id,))
            root_group = cursor.fetchone()
            
            if not root_group:
                return f"Không tìm thấy group với ID: {root_id}"
            
            # Tạo tên với tiền tố từ types_group và description
            root_name = f"{root_group[3]} {root_group[1]}" if root_group[3] else root_group[1]
            root_description = f" - {root_group[2]}" if root_group[2] else ""
            
            # Lấy tất cả children của root group với join types_group và description
            cursor.execute("""
                SELECT pg.id, pg.name, pg.description, tg.name as type_name 
                FROM property_groups pg 
                LEFT JOIN types_group tg ON pg.group_type = tg.id 
                WHERE pg.parent_id = %s 
                ORDER BY pg.name
            """, (root_id,))
            children = cursor.fetchall()
            
            if not children:
                return f"- {root_name} (ID:{root_id}){root_description}"
            
            # Xây dựng tree string
            tree_lines = []
            
            # Thêm root group với tiền tố và description
            tree_lines.append(f"- {root_name} (ID:{root_id}){root_description}")
            
            # Thêm children với tiền tố và description
            for child in children:
                child_name = f"{child[3]} {child[1]}" if child[3] else child[1]
                child_description = f" - {child[2]}" if child[2] else ""
                tree_lines.append(f"- - {child_name} (ID:{child[0]}){child_description}")
                
                # Lấy grandchildren (level 2) với join types_group và description
                cursor.execute("""
                    SELECT pg.id, pg.name, pg.description, tg.name as type_name 
                    FROM property_groups pg 
                    LEFT JOIN types_group tg ON pg.group_type = tg.id 
                    WHERE pg.parent_id = %s 
                    ORDER BY pg.name
                """, (child[0],))
                grandchildren = cursor.fetchall()
                
                for grandchild in grandchildren:
                    grandchild_name = f"{grandchild[3]} {grandchild[1]}" if grandchild[3] else grandchild[1]
                    grandchild_description = f" - {grandchild[2]}" if grandchild[2] else ""
                    tree_lines.append(f"- - - {grandchild_name} (ID:{grandchild[0]}){grandchild_description}")
            
            cursor.close()
            return "\n".join(tree_lines)
            
        except Exception as e:
            return f"Lỗi khi lấy property tree: {str(e)}"
    
    @staticmethod
    def get_unit_types_with_sql(db_connection) -> str:
        """
        Lấy danh sách unit types sử dụng raw SQL
        
        Args:
            db_connection: Database connection
            
        Returns:
            str: Chuỗi unit types đã format cho prompt
        """
        try:
            cursor = db_connection.cursor()
            cursor.execute("SELECT id, name FROM types_unit ORDER BY name")
            unit_types = cursor.fetchall()
            
            if not unit_types:
                cursor.close()
                return "Danh sách các loại căn hộ (unit_type):\n(Không có dữ liệu)"
            
            unit_types_str = "Danh sách các loại căn hộ (unit_type):\n"
            for unit_type in unit_types:
                unit_types_str += f"(ID:{unit_type[0]}) {unit_type[1]}\n"
            
            cursor.close()
            return unit_types_str.strip()
            
        except Exception as e:
            return f"Lỗi khi lấy unit types: {str(e)}"
    
    @staticmethod
    def get_property_tree_for_prompt_with_sql(root_id: int, db_connection) -> str:
        """
        Lấy danh sách tree property groups được format sẵn cho prompt sử dụng raw SQL
        
        Args:
            root_id (int): ID của group root
            db_connection: Database connection
            
        Returns:
            str: Chuỗi tree đã được format cho prompt
        """
        tree_content = PropertyService.get_property_tree_with_sql(root_id, db_connection)
        unit_types_content = PropertyService.get_unit_types_with_sql(db_connection)
        
        if tree_content.startswith("Lỗi") or tree_content.startswith("Không tìm thấy"):
            return tree_content
        
        return f"""<thong-tin-du-an>
Danh sách các phân khu/tòa và id tương ứng:

{tree_content}

{unit_types_content}
</thong-tin-du-an>"""
    
    # Giữ lại các method cũ để backward compatibility
    @staticmethod
    def get_property_tree(root_id: int, db_instance=None) -> str:
        """Backward compatibility method"""
        return f"Không tìm thấy group với ID: {root_id}"
    
    @staticmethod
    def get_property_tree_recursive(root_id: int, max_depth: int = 3, db_instance=None) -> str:
        """Backward compatibility method"""
        return f"Không tìm thấy group với ID: {root_id}"
    
    @staticmethod
    def get_unit_types_for_prompt(db_instance=None) -> str:
        """Backward compatibility method"""
        return "Danh sách các loại căn hộ (unit_type):\n(Không có dữ liệu)"
    
    @staticmethod
    def validate_and_fix_apartment_data(apartment_data: dict) -> dict:
        """
        Validate và fix data types cho apartment data từ GPT-OSS
        
        Args:
            apartment_data: Dict chứa thông tin căn hộ
            
        Returns:
            Dict đã được validate và fix
        """
        try:
            # Define field types và default values
            field_configs = {
                'property_group': {'type': int, 'default': None},
                'unit_code': {'type': str, 'default': None},
                'unit_axis': {'type': str, 'default': None},
                'unit_floor_number': {'type': int, 'default': None},
                'area_land': {'type': float, 'default': None},
                'area_construction': {'type': float, 'default': None},
                'area_net': {'type': float, 'default': None},
                'area_gross': {'type': float, 'default': None},
                'num_bedrooms': {'type': int, 'default': None},
                'num_bathrooms': {'type': int, 'default': None},
                'unit_type': {'type': str, 'default': None},
                'direction_door': {'type': str, 'default': None},
                'direction_balcony': {'type': str, 'default': None},
                'price': {'type': float, 'default': None},
                'price_early': {'type': float, 'default': None},
                'price_schedule': {'type': float, 'default': None},
                'price_loan': {'type': float, 'default': None},
                'price_rent': {'type': float, 'default': None},
                'notes': {'type': str, 'default': None},
                'status': {'type': str, 'default': None}
            }
            
            # Validate và fix từng field
            for field, config in field_configs.items():
                if field not in apartment_data:
                    apartment_data[field] = config['default']
                    continue
                
                value = apartment_data[field]
                
                # Skip null values
                if value is None or value == 'null':
                    apartment_data[field] = config['default']
                    continue
                
                # Convert string numbers to appropriate types
                if config['type'] in [int, float] and isinstance(value, str):
                    try:
                        # Remove common suffixes
                        clean_value = value.replace('m2', '').replace('tỷ', '').replace('triệu', '').strip()
                        if config['type'] == int:
                            apartment_data[field] = int(float(clean_value))
                        else:
                            apartment_data[field] = float(clean_value)
                    except (ValueError, TypeError):
                        apartment_data[field] = config['default']
                
                # Validate enum values
                elif field in ['direction_door', 'direction_balcony']:
                    valid_directions = ['D', 'T', 'N', 'B', 'DB', 'DN', 'TB', 'TN']
                    if value not in valid_directions:
                        apartment_data[field] = config['default']
                
                elif field == 'status':
                    valid_statuses = ['CHUA_BAN', 'DA_LOCK', 'DA_COC', 'DA_BAN']
                    if value not in valid_statuses:
                        apartment_data[field] = config['default']
            
            return apartment_data
            
        except Exception as e:
            print(f"Error validating apartment data: {e}")
            return apartment_data
