#!/usr/bin/env python3
"""
Test lấy unit types từ database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_unit_types():
    """Test lấy unit types từ database"""
    try:
        from app import app
        from utils.property_service import PropertyService
        from models import TypesUnit
        
        with app.app_context():
            print("=== TEST UNIT TYPES FROM DATABASE ===\n")
            
            # Test 1: Lấy tất cả unit types
            print("1. Lấy tất cả unit types từ database:")
            print("-" * 50)
            unit_types = TypesUnit.query.order_by(TypesUnit.name).all()
            print(f"Tổng số unit types: {len(unit_types)}")
            for unit_type in unit_types:
                print(f"   - ID: {unit_type.id}, Name: {unit_type.name}")
            print()
            
            # Test 2: Sử dụng PropertyService
            print("2. Sử dụng PropertyService.get_unit_types_for_prompt():")
            print("-" * 50)
            unit_types_str = PropertyService.get_unit_types_for_prompt()
            print(unit_types_str)
            print()
            
            # Test 3: Test full property tree với unit types
            print("3. Test full property tree với unit types:")
            print("-" * 50)
            full_tree = PropertyService.get_property_tree_for_prompt(1)
            print(full_tree[:1000] + "..." if len(full_tree) > 1000 else full_tree)
            
    except Exception as e:
        print(f"Lỗi: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_unit_types()
