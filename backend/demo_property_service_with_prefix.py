#!/usr/bin/env python3
"""
Demo PropertyService với types_group prefix
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def demo_property_service_with_prefix():
    """Demo PropertyService với types_group prefix"""
    try:
        import pymysql
        from dotenv import load_dotenv
        from utils.property_service_sql import PropertyService
        
        # Load environment variables
        load_dotenv()
        
        print("=== DEMO PROPERTY SERVICE WITH TYPES_GROUP PREFIX ===\n")
        
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
        
        # Demo với các root groups khác nhau
        cursor = connection.cursor()
        cursor.execute("""
            SELECT pg.id, pg.name, pg.group_type, tg.name as type_name 
            FROM property_groups pg 
            LEFT JOIN types_group tg ON pg.group_type = tg.id 
            WHERE pg.parent_id IS NULL
            ORDER BY pg.id
            LIMIT 3
        """)
        root_groups = cursor.fetchall()
        
        for i, root_group in enumerate(root_groups, 1):
            root_id = root_group[0]
            root_name = root_group[1]
            group_type = root_group[2]
            type_name = root_group[3]
            
            print(f"\n{i}. Demo với root group: {root_name} (ID: {root_id})")
            print(f"   Group Type: {group_type}, Type Name: {type_name}")
            print("-" * 60)
            
            # Lấy property tree
            tree = PropertyService.get_property_tree_with_sql(root_id, connection)
            print("Property Tree:")
            print(tree)
            
            print("\n" + "="*80)
        
        # Demo full prompt
        print("\n5. Demo Full Prompt với types_group prefix:")
        print("-" * 50)
        if root_groups:
            root_id = root_groups[0][0]
            full_prompt = PropertyService.get_property_tree_for_prompt_with_sql(root_id, connection)
            print("Full Prompt:")
            print(full_prompt)
        
        cursor.close()
        connection.close()
        print("\n✓ Demo hoàn thành thành công!")
        
    except Exception as e:
        print(f"Lỗi: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    demo_property_service_with_prefix()
