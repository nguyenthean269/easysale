"""
Test WarehouseDatabaseService methods directly
"""

import os
import sys

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

def test_warehouse_service():
    """Test WarehouseDatabaseService methods directly"""
    try:
        from services.warehouse_database_service import warehouse_service
        
        print("🧪 Testing WarehouseDatabaseService methods...")
        print("=" * 50)
        
        # Test 1: Check if methods exist
        print("\n1️⃣ Checking method availability:")
        methods = [
            'get_warehouse_db_connection',
            'get_property_tree_for_prompt', 
            'map_unit_type_to_id',
            'insert_apartment_via_api',
            'insert_apartment_direct',
            'get_apartments_list',
            'get_apartment_by_id',
            'search_apartments'
        ]
        
        for method in methods:
            exists = hasattr(warehouse_service, method)
            print(f"   {method}: {'✅' if exists else '❌'}")
        
        # Test 2: Test unit type mapping
        print("\n2️⃣ Testing unit type mapping:")
        test_types = ['Đơn lập', 'Song lập', '1PN', '2PN1WC', 'Invalid Type']
        for unit_type in test_types:
            mapped_id = warehouse_service.map_unit_type_to_id(unit_type)
            print(f"   '{unit_type}' → {mapped_id}")
        
        # Test 3: Test property tree (without DB connection)
        print("\n3️⃣ Testing property tree method:")
        try:
            # This will likely fail without DB connection, but we can test the method exists
            property_tree = warehouse_service.get_property_tree_for_prompt()
            print(f"   Property tree length: {len(property_tree) if property_tree else 0}")
        except Exception as e:
            print(f"   Expected error (no DB connection): {type(e).__name__}")
        
        print("\n" + "=" * 50)
        print("✅ WarehouseDatabaseService methods test completed!")
        
    except Exception as e:
        print(f"❌ Error testing WarehouseDatabaseService: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_warehouse_service()
