#!/usr/bin/env python3
"""
Test GPT-OSS response handling
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_gpt_oss_response_handling():
    """Test xử lý response từ GPT-OSS"""
    try:
        from utils.property_service_sql import PropertyService
        
        print("=== TEST GPT-OSS RESPONSE HANDLING ===\n")
        
        # Test cases với các loại response khác nhau từ GPT-OSS
        test_cases = [
            # Case 1: Response hoàn hảo
            {
                "name": "Perfect JSON response",
                "response": '{"property_group": 23, "unit_code": "S4.01", "unit_floor_number": 15, "area_gross": 85, "num_bedrooms": 2, "num_bathrooms": 2, "direction_door": "N", "price": 3200000000, "unit_type": "2PN2WC"}'
            },
            
            # Case 2: Response với string numbers
            {
                "name": "String numbers response",
                "response": '{"property_group": "23", "unit_code": "S4.01", "unit_floor_number": "15", "area_gross": "85m2", "num_bedrooms": "2PN", "num_bathrooms": "2WC", "direction_door": "N", "price": "3.2 tỷ"}'
            },
            
            # Case 3: Response với text thêm
            {
                "name": "Response with extra text",
                "response": 'Đây là thông tin căn hộ: {"property_group": 23, "unit_code": "S4.01", "unit_floor_number": 15, "area_gross": 85, "num_bedrooms": 2, "num_bathrooms": 2, "direction_door": "N", "price": 3200000000} Cảm ơn bạn!'
            },
            
            # Case 4: Response với null values
            {
                "name": "Response with null values",
                "response": '{"property_group": 23, "unit_code": null, "unit_axis": null, "unit_floor_number": 15, "area_gross": 85, "num_bedrooms": 2, "num_bathrooms": 2, "direction_door": "N", "price": 3200000000, "notes": null}'
            },
            
            # Case 5: Response với invalid enum values
            {
                "name": "Response with invalid enum",
                "response": '{"property_group": 23, "unit_code": "S4.01", "unit_floor_number": 15, "area_gross": 85, "num_bedrooms": 2, "num_bathrooms": 2, "direction_door": "INVALID", "status": "INVALID_STATUS"}'
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"{i}. {test_case['name']}:")
            print("-" * 50)
            print(f"Input: {test_case['response']}")
            
            # Parse JSON
            import json
            try:
                # Tìm JSON trong response
                response_clean = test_case['response'].strip()
                start_idx = response_clean.find('{')
                end_idx = response_clean.rfind('}')
                
                if start_idx != -1 and end_idx != -1:
                    json_str = response_clean[start_idx:end_idx + 1]
                    apartment_data = json.loads(json_str)
                    
                    # Validate và fix data
                    fixed_data = PropertyService.validate_and_fix_apartment_data(apartment_data)
                    
                    print(f"Parsed: {apartment_data}")
                    print(f"Fixed:  {fixed_data}")
                else:
                    print("No JSON found")
                    
            except Exception as e:
                print(f"Error: {e}")
            
            print("\n" + "="*80 + "\n")
        
        print("✓ Test hoàn thành!")
        
    except Exception as e:
        print(f"Lỗi: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_gpt_oss_response_handling()
