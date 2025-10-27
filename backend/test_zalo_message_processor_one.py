#!/usr/bin/env python3
"""
Test script cho Zalo Message Processor - Test One Mode
Demo cách sử dụng mode test-one để test một message cụ thể
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Add parent directory to path để import zalo_message_processor
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.zalo_message_processor import ZaloMessageProcessor

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_message_by_id(message_id: int):
    """
    Test một message cụ thể theo ID
    
    Args:
        message_id: ID của message cần test
    """
    logger.info(f"🧪 Testing message with ID: {message_id}")
    
    # Khởi tạo processor
    processor = ZaloMessageProcessor()
    
    # Chạy test-one mode
    result, error = processor.run_test_one_mode(message_id)
    
    if error:
        logger.error(f"❌ Test failed: {error}")
        return False
    else:
        logger.info("✅ Test completed successfully")
        logger.info(f"📊 Result: {result}")
        return True

def main():
    """Main function"""
    if len(sys.argv) != 2:
        print("Usage: python test_zalo_message_processor_one.py <message_id>")
        print("Example: python test_zalo_message_processor_one.py 123")
        sys.exit(1)
    
    try:
        message_id = int(sys.argv[1])
        success = test_message_by_id(message_id)
        
        if success:
            print("✅ Test completed successfully")
            sys.exit(0)
        else:
            print("❌ Test failed")
            sys.exit(1)
            
    except ValueError:
        print("❌ Error: message_id must be a number")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

