#!/usr/bin/env python3
"""
Test script cho PropertyService
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from models import db, PropertyGroup
from utils.property_service import PropertyService


def test_property_service():
    """Test các hàm trong PropertyService"""
    
    with app.app_context():
        print("=== TEST PROPERTY SERVICE ===\n")
        
        # Test 1: Lấy tất cả property groups
        print("1. Test lấy tất cả property groups:")
        all_groups = PropertyService.get_all_property_groups()
        print(f"   Tổng số groups: {len(all_groups)}")
        if all_groups:
            print(f"   Ví dụ group đầu tiên: {all_groups[0]['name']} (ID: {all_groups[0]['id']})")
        print()
        
        # Test 2: Lấy root groups (parent_id = None)
        print("2. Test lấy root groups:")
        root_groups = PropertyService.get_property_groups_by_parent(None)
        print(f"   Số root groups: {len(root_groups)}")
        for group in root_groups[:5]:  # Hiển thị 5 groups đầu tiên
            print(f"   - {group['name']} (ID: {group['id']})")
        print()
        
        # Test 3: Lấy tree cho một root group cụ thể
        if root_groups:
            root_id = root_groups[0]['id']
            print(f"3. Test lấy tree cho root group ID {root_id} ({root_groups[0]['name']}):")
            tree = PropertyService.get_property_tree(root_id)
            print(tree)
            print()
            
            # Test 4: Lấy tree với đệ quy
            print(f"4. Test lấy tree đệ quy cho root group ID {root_id}:")
            tree_recursive = PropertyService.get_property_tree_recursive(root_id)
            print(tree_recursive)
            print()
            
            # Test 5: Lấy tree format cho prompt
            print(f"5. Test lấy tree format cho prompt cho root group ID {root_id}:")
            tree_prompt = PropertyService.get_property_tree_for_prompt(root_id)
            print(tree_prompt)
            print()
        
        # Test 6: Test với ID không tồn tại
        print("6. Test với ID không tồn tại:")
        invalid_tree = PropertyService.get_property_tree(99999)
        print(invalid_tree)
        print()
        
        # Test 7: Lấy children của một group cụ thể
        if root_groups:
            root_id = root_groups[0]['id']
            print(f"7. Test lấy children của root group ID {root_id}:")
            children = PropertyService.get_property_groups_by_parent(root_id)
            print(f"   Số children: {len(children)}")
            for child in children[:3]:  # Hiển thị 3 children đầu tiên
                print(f"   - {child['name']} (ID: {child['id']})")
        print()


def test_database_connection():
    """Test kết nối database"""
    try:
        with app.app_context():
            # Test query đơn giản
            count = PropertyGroup.query.count()
            print(f"✓ Kết nối database thành công. Tổng số property groups: {count}")
            return True
    except Exception as e:
        print(f"✗ Lỗi kết nối database: {str(e)}")
        return False


if __name__ == "__main__":
    print("Bắt đầu test PropertyService...\n")
    
    # Test kết nối database trước
    if test_database_connection():
        print()
        test_property_service()
    else:
        print("Không thể test vì lỗi kết nối database.")
