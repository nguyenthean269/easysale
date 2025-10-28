"""
Test WarehouseDatabaseService methods directly with list IDs
"""

import os
import sys

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

def test_warehouse_service():
    """Test WarehouseDatabaseService methods with list IDs"""
    try:
        from services.warehouse_database_service import warehouse_service
        
        print("🧪 Testing WarehouseDatabaseService with list IDs...")
        print("=" * 60)
        
        # Test 1: Check if new method exists
        print("\n1️⃣ Checking method availability:")
        methods = [
            'get_apartments_by_ids',
            'get_apartment_by_id',  # Should still exist for backward compatibility
        ]
        
        for method in methods:
            exists = hasattr(warehouse_service, method)
            print(f"   {method}: {'✅' if exists else '❌'}")
        
        # Test 2: Test with empty list
        print("\n2️⃣ Testing with empty list:")
        try:
            result = warehouse_service.get_apartments_by_ids([])
            print(f"   Result: {result}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Test 3: Test with single ID
        print("\n3️⃣ Testing with single ID:")
        try:
            result = warehouse_service.get_apartments_by_ids([1])
            print(f"   Success: {result.get('success', False)}")
            print(f"   Found count: {result.get('found_count', 0)}")
            print(f"   Requested count: {result.get('requested_count', 0)}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Test 4: Test with multiple IDs
        print("\n4️⃣ Testing with multiple IDs:")
        try:
            result = warehouse_service.get_apartments_by_ids([1, 2, 3, 999])
            print(f"   Success: {result.get('success', False)}")
            print(f"   Found count: {result.get('found_count', 0)}")
            print(f"   Requested count: {result.get('requested_count', 0)}")
            print(f"   Missing IDs: {result.get('missing_ids', [])}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Test 5: Test backward compatibility
        print("\n5️⃣ Testing backward compatibility (single ID method):")
        try:
            result = warehouse_service.get_apartment_by_id(1)
            print(f"   Success: {result.get('success', False)}")
            if result.get('success'):
                print(f"   Data keys: {list(result.get('data', {}).keys())}")
            else:
                print(f"   Error: {result.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"   Error: {e}")
        
        print("\n" + "=" * 60)
        print("✅ WarehouseDatabaseService list IDs test completed!")
        
    except Exception as e:
        print(f"❌ Error testing WarehouseDatabaseService: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_warehouse_service()
