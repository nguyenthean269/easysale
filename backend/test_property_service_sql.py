#!/usr/bin/env python3
"""
Test PropertyService với raw SQL
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_property_service_sql():
    """Test PropertyService với raw SQL"""
    try:
        import pymysql
        from dotenv import load_dotenv
        from utils.property_service_sql import PropertyService
        
        # Load environment variables
        load_dotenv()
        
        print("=== TEST PROPERTY SERVICE WITH RAW SQL ===\n")
        
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
        
        # Test 1: Lấy property tree
        print("\n1. Test lấy property tree:")
        print("-" * 50)
        tree = PropertyService.get_property_tree_with_sql(1, connection)
        print(tree)
        
        # Test 2: Lấy unit types
        print("\n2. Test lấy unit types:")
        print("-" * 50)
        unit_types = PropertyService.get_unit_types_with_sql(connection)
        print(unit_types)
        
        # Test 3: Lấy full prompt
        print("\n3. Test lấy full prompt:")
        print("-" * 50)
        full_prompt = PropertyService.get_property_tree_for_prompt_with_sql(1, connection)
        print(full_prompt[:1000] + "..." if len(full_prompt) > 1000 else full_prompt)
        
        connection.close()
        print("\n✓ Test hoàn thành thành công!")
        
    except Exception as e:
        print(f"Lỗi: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_property_service_sql()
