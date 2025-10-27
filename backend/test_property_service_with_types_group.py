#!/usr/bin/env python3
"""
Test PropertyService với join types_group
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_property_service_with_types_group():
    """Test PropertyService với join types_group"""
    try:
        import pymysql
        from dotenv import load_dotenv
        from utils.property_service_sql import PropertyService
        
        # Load environment variables
        load_dotenv()
        
        print("=== TEST PROPERTY SERVICE WITH TYPES_GROUP ===\n")
        
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
        
        # Test 1: Kiểm tra dữ liệu types_group
        print("\n1. Kiểm tra dữ liệu types_group:")
        print("-" * 50)
        cursor = connection.cursor()
        cursor.execute("SELECT id, name FROM types_group ORDER BY id")
        types_groups = cursor.fetchall()
        print(f"Tổng số types_group: {len(types_groups)}")
        for tg in types_groups:
            print(f"   - ID: {tg[0]}, Name: {tg[1]}")
        
        # Test 2: Kiểm tra dữ liệu property_groups với join
        print("\n2. Kiểm tra property_groups với join types_group:")
        print("-" * 50)
        cursor.execute("""
            SELECT pg.id, pg.name, pg.group_type, tg.name as type_name 
            FROM property_groups pg 
            LEFT JOIN types_group tg ON pg.group_type = tg.id 
            WHERE pg.parent_id IS NULL
            ORDER BY pg.id
            LIMIT 5
        """)
        root_groups = cursor.fetchall()
        print(f"Root groups với types_group:")
        for rg in root_groups:
            type_name = f"{rg[3]} {rg[1]}" if rg[3] else rg[1]
            print(f"   - ID: {rg[0]}, Name: {rg[1]}, Group Type: {rg[2]}, Type Name: {rg[3]}, Full Name: {type_name}")
        
        # Test 3: Lấy property tree với types_group
        print("\n3. Test lấy property tree với types_group:")
        print("-" * 50)
        if root_groups:
            root_id = root_groups[0][0]
            tree = PropertyService.get_property_tree_with_sql(root_id, connection)
            print(tree)
        
        # Test 4: Lấy full prompt với types_group
        print("\n4. Test lấy full prompt với types_group:")
        print("-" * 50)
        if root_groups:
            root_id = root_groups[0][0]
            full_prompt = PropertyService.get_property_tree_for_prompt_with_sql(root_id, connection)
            print(full_prompt[:1500] + "..." if len(full_prompt) > 1500 else full_prompt)
        
        cursor.close()
        connection.close()
        print("\n✓ Test hoàn thành thành công!")
        
    except Exception as e:
        print(f"Lỗi: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_property_service_with_types_group()
