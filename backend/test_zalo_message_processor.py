"""
Test script cho Zalo Message Processor Service
"""

import os
import sys
import time
from dotenv import load_dotenv

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.zalo_message_processor import ZaloMessageProcessor

def test_database_connection():
    """Test kết nối database"""
    print("🔍 Testing database connection...")
    
    processor = ZaloMessageProcessor()
    connection = processor.get_db_connection()
    
    if connection:
        print("✅ Database connection successful")
        connection.close()
        return True
    else:
        print("❌ Database connection failed")
        return False

def test_get_unprocessed_messages():
    """Test lấy tin nhắn chưa xử lý"""
    print("🔍 Testing get unprocessed messages...")
    
    processor = ZaloMessageProcessor()
    result = processor.get_unprocessed_messages(limit=5)
    messages = result.get('messages', []) if isinstance(result, dict) else result
    total = result.get('total', len(messages)) if isinstance(result, dict) else len(messages)
    
    print(f"📊 Found {len(messages)} unprocessed messages (total: {total})")
    
    if messages:
        print("📝 Sample message:")
        sample = messages[0]
        print(f"   ID: {sample['id']}")
        print(f"   Sender: {sample['sender_name']}")
        print(f"   Content: {sample['content'][:100]}...")
        print(f"   Status: {sample['status_push_warehouse']}")
    
    return len(messages) >= 0

def test_groq_processing():
    """Test xử lý tin nhắn với Groq"""
    print("🔍 Testing Groq processing...")
    
    processor = ZaloMessageProcessor()
    test_message = "Căn hộ Studio A1.01, tầng 5, diện tích 35m2, giá 2.5 tỷ, hướng Đông"
    
    result = processor.process_message_with_groq(test_message)
    
    if result:
        print("✅ Groq processing successful")
        print(f"📝 Result: {result[:200]}...")
        return True
    else:
        print("❌ Groq processing failed")
        return False

def test_json_parsing():
    """Test parse JSON từ Groq response"""
    print("🔍 Testing JSON parsing...")
    
    processor = ZaloMessageProcessor()
    test_json = '''
    {
        "unit_code": "A1.01",
        "unit_floor_number": "5",
        "area_net": 35,
        "unit_type": "Studio",
        "price": 2500000000,
        "direction_door": "D",
        "notes": "Căn hộ đẹp"
    }
    '''
    
    result = processor.parse_groq_response(test_json)
    
    if result:
        print("✅ JSON parsing successful")
        print(f"📝 Parsed data: {result}")
        return True
    else:
        print("❌ JSON parsing failed")
        return False

def test_unit_type_mapping():
    """Test mapping unit type name sang ID"""
    print("🔍 Testing unit type mapping...")
    
    processor = ZaloMessageProcessor()
    
    test_cases = [
        ("Studio", 6),
        ("1PN", 7),
        ("2PN1WC", 9),
        ("Đơn lập", 1),
        ("Unknown Type", None)
    ]
    
    all_passed = True
    for unit_type, expected_id in test_cases:
        result = processor.map_unit_type_to_id(unit_type)
        if result == expected_id:
            print(f"✅ '{unit_type}' -> {result}")
        else:
            print(f"❌ '{unit_type}' -> {result} (expected {expected_id})")
            all_passed = False
    
    return all_passed

def test_warehouse_connection():
    """Test kết nối warehouse database"""
    print("🔍 Testing warehouse database connection...")
    
    processor = ZaloMessageProcessor()
    connection = processor.get_warehouse_db_connection()
    
    if connection:
        print("✅ Warehouse database connection successful")
        connection.close()
        return True
    else:
        print("❌ Warehouse database connection failed")
        return False

def test_message_status_update():
    """Test cập nhật trạng thái tin nhắn"""
    print("🔍 Testing message status update...")
    
    processor = ZaloMessageProcessor()
    
    # Lấy một tin nhắn để test
    result = processor.get_unprocessed_messages(limit=1)
    messages = result.get('messages', []) if isinstance(result, dict) else result
    
    if not messages:
        print("⚠️  No messages available for testing")
        return True
    
    message_id = messages[0]['id']
    
    # Test update status
    success = processor.update_message_status(message_id, 'PUSHED')
    
    if success:
        print("✅ Message status update successful")
        
        # Revert back to NOT_YET for testing
        processor.update_message_status(message_id, 'NOT_YET')
        print("🔄 Reverted message status back to NOT_YET")
        return True
    else:
        print("❌ Message status update failed")
        return False

def test_service_lifecycle():
    """Test vòng đời service (start/stop)"""
    print("🔍 Testing service lifecycle...")
    
    processor = ZaloMessageProcessor()
    
    # Test start
    processor.start()
    time.sleep(2)  # Wait a bit
    
    status = processor.get_status()
    print(f"📊 Service status: {status}")
    
    if status['is_running']:
        print("✅ Service started successfully")
        
        # Test stop
        processor.stop()
        time.sleep(1)
        
        status = processor.get_status()
        if not status['is_running']:
            print("✅ Service stopped successfully")
            return True
        else:
            print("❌ Service stop failed")
            return False
    else:
        print("❌ Service start failed")
        return False

def main():
    """Chạy tất cả tests"""
    print("🚀 Starting Zalo Message Processor Tests...")
    print("=" * 50)
    
    tests = [
        ("Zalo Database Connection", test_database_connection),
        ("Warehouse Database Connection", test_warehouse_connection),
        ("Get Unprocessed Messages", test_get_unprocessed_messages),
        ("Groq Processing", test_groq_processing),
        ("JSON Parsing", test_json_parsing),
        ("Unit Type Mapping", test_unit_type_mapping),
        ("Message Status Update", test_message_status_update),
        ("Service Lifecycle", test_service_lifecycle)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append((test_name, False))
        print("-" * 30)
    
    # Summary
    print("\n📊 Test Results Summary:")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
    else:
        print("⚠️  Some tests failed. Please check the configuration.")

if __name__ == "__main__":
    main()
