#!/usr/bin/env python3
"""
Demo sử dụng PropertyService để lấy tree property groups cho prompt
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from utils.property_service import PropertyService


def demo_property_tree_for_prompt():
    """Demo sử dụng property tree trong prompt"""
    
    with app.app_context():
        print("=== DEMO PROPERTY TREE CHO PROMPT ===\n")
        
        # Lấy tất cả root groups
        root_groups = PropertyService.get_property_groups_by_parent(None)
        
        if not root_groups:
            print("Không có root groups nào trong database.")
            return
        
        print("Các root groups có sẵn:")
        for i, group in enumerate(root_groups, 1):
            print(f"{i}. {group['name']} (ID: {group['id']})")
        
        print("\n" + "="*50)
        
        # Demo với root group đầu tiên
        root_id = root_groups[0]['id']
        root_name = root_groups[0]['name']
        
        print(f"\nDemo với root group: {root_name} (ID: {root_id})")
        print("="*50)
        
        # Lấy tree format cho prompt
        tree_prompt = PropertyService.get_property_tree_for_prompt(root_id)
        print(tree_prompt)
        
        print("\n" + "="*50)
        print("Cách sử dụng trong code:")
        print("="*50)
        
        code_example = f'''
# Import service
from utils.property_service import PropertyService

# Lấy tree cho root group ID {root_id}
tree_content = PropertyService.get_property_tree_for_prompt({root_id})

# Sử dụng trong prompt
prompt = f"""
Bạn là một AI assistant chuyên về bất động sản.

{{tree_content}}

Hãy trả lời câu hỏi của khách hàng dựa trên thông tin dự án trên.
"""
'''
        print(code_example)


def demo_all_property_trees():
    """Demo lấy tree cho tất cả root groups"""
    
    with app.app_context():
        print("\n=== DEMO TẤT CẢ PROPERTY TREES ===\n")
        
        root_groups = PropertyService.get_property_groups_by_parent(None)
        
        if not root_groups:
            print("Không có root groups nào trong database.")
            return
        
        for group in root_groups:
            print(f"--- {group['name']} (ID: {group['id']}) ---")
            tree = PropertyService.get_property_tree(group['id'])
            print(tree)
            print()


if __name__ == "__main__":
    print("Bắt đầu demo PropertyService...\n")
    
    try:
        with app.app_context():
            demo_property_tree_for_prompt()
            demo_all_property_trees()
    except Exception as e:
        print(f"Lỗi: {str(e)}")
        print("Có thể database chưa được khởi tạo hoặc chưa có dữ liệu.")
