#!/usr/bin/env python3
"""
Test PropertyService với description
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_property_service_with_description():
    """Test PropertyService với description"""
    try:
        import pymysql
        from dotenv import load_dotenv
        from utils.property_service_sql import PropertyService
        
        # Load environment variables
        load_dotenv()
        
        print("=== TEST PROPERTY SERVICE WITH DESCRIPTION ===\n")
        
        # Tạo connection đến warehouse database
        connection = pymysql.connect(
            host=os.getenv('DB_WAREHOUSE_HOST', '103.6.234.59'),
            port=int(os.getenv('DB_WAREHOUSE_PORT', '6033')),
            user=os.getenv('DB_WAREHOUSE_USER', 'root'),
            password=os.getenv('DB_WAREHOUSE_PASSWORD', ''),
            database=os.getenv('DB_WAREHOUSE_NAME', 'warehouse'),
            charset='utf8mb4'
        )
        
        print("✓ Kết nối database thành công")
        
        # Test 1: Kiểm tra dữ liệu với description
        print("\n1. Kiểm tra property_groups với description:")
        print("-" * 50)
        cursor = connection.cursor()
        cursor.execute("""
            SELECT pg.id, pg.name, pg.description, pg.group_type, tg.name as type_name 
            FROM property_groups pg 
            LEFT JOIN types_group tg ON pg.group_type = tg.id 
            WHERE pg.parent_id IS NULL
            ORDER BY pg.id
            LIMIT 3
        """)
        root_groups = cursor.fetchall()
        
        for rg in root_groups:
            print(f"   - ID: {rg[0]}, Name: {rg[1]}, Description: {rg[2]}, Group Type: {rg[3]}, Type Name: {rg[4]}")
        
        # Test 2: Lấy property tree với description
        print("\n2. Test lấy property tree với description:")
        print("-" * 50)
        if root_groups:
            root_id = root_groups[0][0]
            tree = PropertyService.get_property_tree_with_sql(root_id, connection)
            print("Property Tree với Description:")
            print(tree)
        
        # Test 3: Lấy full prompt với description
        print("\n3. Test lấy full prompt với description:")
        print("-" * 50)
        if root_groups:
            root_id = root_groups[0][0]
            full_prompt = PropertyService.get_property_tree_for_prompt_with_sql(root_id, connection)
            print("Full Prompt với Description:")
            print(full_prompt[:2000] + "..." if len(full_prompt) > 2000 else full_prompt)
        
        cursor.close()
        connection.close()
        print("\n✓ Test hoàn thành thành công!")
        
    except Exception as e:
        print(f"Lỗi: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_property_service_with_description()
