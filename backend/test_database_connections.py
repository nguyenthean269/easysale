#!/usr/bin/env python3
"""
Test Database Connection và Retry Mechanism
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_database_connections():
    """Test các database connections"""
    try:
        from services.zalo_message_processor import ZaloMessageProcessor
        
        print("=== TESTING DATABASE CONNECTIONS ===\n")
        
        processor = ZaloMessageProcessor()
        
        # Test 1: Zalo database connection
        print("1. Testing Zalo database connection...")
        zalo_conn = processor.get_zalo_db_connection()
        if zalo_conn:
            print("   ✅ Zalo database connection successful")
            zalo_conn.close()
        else:
            print("   ❌ Zalo database connection failed")
        print()
        
        # Test 2: Warehouse database connection
        print("2. Testing Warehouse database connection...")
        warehouse_conn = processor.get_warehouse_db_connection()
        if warehouse_conn:
            print("   ✅ Warehouse database connection successful")
            warehouse_conn.close()
        else:
            print("   ❌ Warehouse database connection failed")
        print()
        
        # Test 3: Get unprocessed messages
        print("3. Testing get unprocessed messages...")
        messages = processor.get_unprocessed_messages(limit=5)
        print(f"   Found {len(messages)} unprocessed messages")
        if messages:
            print(f"   First message: {messages[0]}")
        print()
        
        # Test 4: Processor status
        print("4. Testing processor status...")
        status = processor.get_status()
        print(f"   Status: {status}")
        print()
        
        print("✅ All tests completed!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_database_connections()





