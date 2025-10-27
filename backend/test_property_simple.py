#!/usr/bin/env python3
"""
Test đơn giản cho PropertyService
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_import():
    """Test import các module"""
    try:
        from utils.property_service import PropertyService
        print("✓ Import PropertyService thành công")
        
        from models import PropertyGroup
        print("✓ Import PropertyGroup thành công")
        
        return True
    except Exception as e:
        print(f"✗ Lỗi import: {str(e)}")
        return False

def test_property_service_methods():
    """Test các method của PropertyService"""
    try:
        from utils.property_service import PropertyService
        
        # Test method get_property_tree
        print("\n=== Test get_property_tree ===")
        result = PropertyService.get_property_tree(1)
        print(f"Kết quả get_property_tree(1): {result[:100]}...")
        
        # Test method get_property_tree_recursive
        print("\n=== Test get_property_tree_recursive ===")
        result = PropertyService.get_property_tree_recursive(1)
        print(f"Kết quả get_property_tree_recursive(1): {result[:100]}...")
        
        # Test method get_property_tree_for_prompt
        print("\n=== Test get_property_tree_for_prompt ===")
        result = PropertyService.get_property_tree_for_prompt(1)
        print(f"Kết quả get_property_tree_for_prompt(1): {result[:100]}...")
        
        return True
    except Exception as e:
        print(f"✗ Lỗi test methods: {str(e)}")
        return False

if __name__ == "__main__":
    print("Bắt đầu test PropertyService...\n")
    
    # Test import
    if test_import():
        print()
        # Test methods
        test_property_service_methods()
    else:
        print("Không thể test vì lỗi import.")
