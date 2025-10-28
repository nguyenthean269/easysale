#!/usr/bin/env python3
"""
Test ZaloMessageProcessor với các giá trị ZALO_MESSAGE_PROCESSOR_SCHEDULE khác nhau
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_schedule_configuration():
    """Test các cấu hình schedule khác nhau"""
    try:
        from services.zalo_message_processor import ZaloMessageProcessor
        
        print("=== TEST SCHEDULE CONFIGURATION ===\n")
        
        # Test cases với các giá trị khác nhau
        test_cases = [
            {"schedule": "0", "description": "Schedule disabled"},
            {"schedule": "5", "description": "5 minutes interval"},
            {"schedule": "10", "description": "10 minutes interval (default)"},
            {"schedule": "30", "description": "30 minutes interval"},
            {"schedule": "60", "description": "1 hour interval"},
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"{i}. Test với ZALO_MESSAGE_PROCESSOR_SCHEDULE={test_case['schedule']} ({test_case['description']}):")
            print("-" * 60)
            
            # Set environment variable
            os.environ['ZALO_MESSAGE_PROCESSOR_SCHEDULE'] = test_case['schedule']
            
            # Tạo instance mới
            processor = ZaloMessageProcessor()
            
            # Kiểm tra các thuộc tính
            print(f"   - interval: {processor.interval} seconds ({processor.interval//60} minutes)")
            print(f"   - schedule_enabled: {processor.schedule_enabled}")
            print(f"   - is_running: {processor.is_running}")
            
            # Test start method
            print(f"   - Testing start()...")
            processor.start()
            print(f"   - is_running after start: {processor.is_running}")
            
            # Test status
            status = processor.get_status()
            print(f"   - Status: {status}")
            
            # Stop nếu đang chạy
            if processor.is_running:
                processor.stop()
                print(f"   - Stopped service")
            
            print("\n" + "="*80 + "\n")
        
        print("✓ Test hoàn thành!")
        
    except Exception as e:
        print(f"Lỗi: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_schedule_configuration()
