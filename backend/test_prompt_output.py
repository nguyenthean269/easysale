#!/usr/bin/env python3
"""
Test in ra prompt để xem kết quả
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_prompt_output():
    """Test in ra prompt"""
    try:
        from utils.property_service import PropertyService
        
        print("=== TEST PROPERTY TREE FOR PROMPT ===\n")
        
        # Test với root_id = 1
        print("1. Test với root_id = 1:")
        print("-" * 50)
        result = PropertyService.get_property_tree_for_prompt(1)
        print(result)
        print("\n" + "=" * 80 + "\n")
        
        # Test với root_id = 2
        print("2. Test với root_id = 2:")
        print("-" * 50)
        result = PropertyService.get_property_tree_for_prompt(2)
        print(result)
        print("\n" + "=" * 80 + "\n")
        
        # Test tree đơn giản
        print("3. Test tree đơn giản với root_id = 1:")
        print("-" * 50)
        result = PropertyService.get_property_tree(1)
        print(result)
        print("\n" + "=" * 80 + "\n")
        
        # Test tree recursive
        print("4. Test tree recursive với root_id = 1:")
        print("-" * 50)
        result = PropertyService.get_property_tree_recursive(1)
        print(result)
        
    except Exception as e:
        print(f"Lỗi: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_prompt_output()
