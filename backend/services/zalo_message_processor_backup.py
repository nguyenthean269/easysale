"""
Zalo Message Processor Service
Service xử lý tin nhắn từ Zalo định kỳ 10 phút một lần
"""

import os
import time
import threading
import logging
import json
import argparse
from datetime import datetime
from typing import List, Dict, Optional
from groq import Groq
from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from utils.property_service_sql import PropertyService

# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Debug environment variables
logger.info("🔧 Environment variables loaded:")
logger.info(f"DB_CHAT_HOST: {os.getenv('DB_CHAT_HOST', 'NOT_SET')}")
logger.info(f"DB_CHAT_PORT: {os.getenv('DB_CHAT_PORT', 'NOT_SET')}")
logger.info(f"DB_CHAT_USER: {os.getenv('DB_CHAT_USER', 'NOT_SET')}")
logger.info(f"DB_CHAT_PASSWORD: {'SET' if os.getenv('DB_CHAT_PASSWORD') else 'NOT_SET'}")
logger.info(f"DB_CHAT_NAME: {os.getenv('DB_CHAT_NAME', 'NOT_SET')}")
logger.info(f"DB_WAREHOUSE_HOST: {os.getenv('DB_WAREHOUSE_HOST', 'NOT_SET')}")
logger.info(f"DB_WAREHOUSE_PORT: {os.getenv('DB_WAREHOUSE_PORT', 'NOT_SET')}")
logger.info(f"DB_WAREHOUSE_USER: {os.getenv('DB_WAREHOUSE_USER', 'NOT_SET')}")
logger.info(f"DB_WAREHOUSE_PASSWORD: {'SET' if os.getenv('DB_WAREHOUSE_PASSWORD') else 'NOT_SET'}")
logger.info(f"DB_WAREHOUSE_NAME: {os.getenv('DB_WAREHOUSE_NAME', 'NOT_SET')}")

# Tạo Flask app cho zalo_messages database
zalo_app = Flask(__name__)
zalo_app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql://{os.getenv('DB_CHAT_USER', 'easychat')}:{os.getenv('DB_CHAT_PASSWORD', '')}@{os.getenv('DB_CHAT_HOST', '103.6.234.59')}:{os.getenv('DB_CHAT_PORT', '6033')}/{os.getenv('DB_CHAT_NAME', 'zalo_messages')}"
zalo_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
zalo_db = SQLAlchemy(zalo_app)

# Tạo Flask app cho warehouse database
warehouse_app = Flask(__name__)
warehouse_app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql://{os.getenv('DB_WAREHOUSE_USER', 'root')}:{os.getenv('DB_WAREHOUSE_PASSWORD', '')}@{os.getenv('DB_WAREHOUSE_HOST', '103.6.234.59')}:{os.getenv('DB_WAREHOUSE_PORT', '6033')}/{os.getenv('DB_WAREHOUSE_NAME', 'warehouse')}"
warehouse_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
warehouse_db = SQLAlchemy(warehouse_app)

class ZaloMessageProcessor:
    """Service xử lý tin nhắn Zalo định kỳ"""
    
    def __init__(self):
        """Khởi tạo service"""
        # Groq client
        self.groq_client = Groq(api_key=os.getenv('GROQ_API_KEY'))
        
        # Service control
        self.is_running = False
        self.thread = None
        
        # Lấy interval từ environment variable (đơn vị phút)
        schedule_minutes = int(os.getenv('ZALO_MESSAGE_PROCESSOR_SCHEDULE', '10'))
        self.interval = schedule_minutes * 60  # Chuyển từ phút sang giây
        self.schedule_enabled = schedule_minutes > 0  # Chỉ enable nếu > 0
        
        # Unit type mapping từ name sang id
        self.unit_type_mapping = {
            'Đơn lập': 1,
            'Song lập': 2,
            'Tứ lập': 3,
            'Tứ lập cạnh góc': 4,
            'Shophouse': 5,
            'Studio': 6,
            '1PN': 7,
            '1PN+': 8,
            '2PN1WC': 9,
            '2PN2WC': 10,
            '3PN': 11,
            'Đơn lập cạnh góc': 12
        }
        
        logger.info(f"ZaloMessageProcessor initialized (schedule: {self.interval//60} minutes, enabled: {self.schedule_enabled})")
    
    def get_zalo_db_connection(self):
        """Tạo kết nối database zalo_messages với retry mechanism"""
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Attempting to connect to zalo_messages database... (attempt {attempt + 1}/{max_retries})")
                
                with zalo_app.app_context():
                    # Sử dụng SQLAlchemy engine với connection pooling
                    connection = zalo_db.engine.connect()
                    logger.info("✅ Zalo database connection successful")
                    return connection
                    
            except Exception as e:
                logger.error(f"❌ Zalo database connection error (attempt {attempt + 1}): {e}")
                logger.error(f"Error type: {type(e)}")
                
                if attempt < max_retries - 1:
                    logger.info(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    logger.error("❌ Failed to connect to zalo database after all retries")
                    return None
    
    def get_warehouse_db_connection(self):
        """Tạo kết nối database warehouse với retry mechanism"""
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Attempting to connect to warehouse database... (attempt {attempt + 1}/{max_retries})")
                
                with warehouse_app.app_context():
                    # Sử dụng SQLAlchemy engine
                    connection = warehouse_db.engine.connect()
                    logger.info("✅ Warehouse database connection successful")
                    return connection
                    
            except Exception as e:
                logger.error(f"❌ Warehouse database connection error (attempt {attempt + 1}): {e}")
                logger.error(f"Error type: {type(e)}")
                
                if attempt < max_retries - 1:
                    logger.info(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    logger.error("❌ Failed to connect to warehouse database after all retries")
                    return None
    
    def get_unprocessed_messages(self, limit: int = 20) -> List[Dict]:
        """
        Lấy danh sách tin nhắn chưa xử lý từ bảng received_messages
        
        Args:
            limit: Số lượng tin nhắn tối đa cần lấy
            
        Returns:
            List các tin nhắn chưa xử lý
        """
        try:
            logger.info("🔍 Starting to fetch unprocessed messages...")
            
            # Retry logic cho connection
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    logger.info(f"🔄 Attempt {attempt + 1}/{max_retries}")
                    
                    with zalo_app.app_context():
                        logger.info("📡 Zalo app context created")
                        connection = self.get_zalo_db_connection()
                        if not connection:
                            logger.error("❌ No database connection available")
                            continue
                        
                        logger.info("📊 Executing query to fetch messages...")
                        from sqlalchemy import text
                        
                        query = text("""
                        SELECT id, session_id, config_id, sender_id, sender_name, 
                               content, thread_id, thread_type, received_at, 
                               status_push_kafka, status_push_warehouse, reply_quote
                        FROM received_messages 
                        WHERE status_push_warehouse = 'NOT_YET' 
                        ORDER BY received_at ASC 
                        LIMIT :limit
                        """)
                        
                        logger.info(f"🔍 Query: {query}")
                        logger.info(f"🔍 Limit: {limit}")
                        
                        result = connection.execute(query, {"limit": limit})
                        logger.info("✅ Query executed successfully")
                        
                        messages = []
                        for row in result:
                            messages.append(dict(row._mapping))
                        
                        logger.info(f"✅ Found {len(messages)} unprocessed messages")
                        return messages
                        
                except Exception as e:
                    logger.error(f"❌ Attempt {attempt + 1} failed: {e}")
                    if attempt < max_retries - 1:
                        logger.info(f"🔄 Retrying in 2 seconds...")
                        time.sleep(2)
                    else:
                        raise e
                        
        except Exception as e:
            logger.error(f"❌ Error fetching messages after {max_retries} attempts: {e}")
            logger.error(f"❌ Error type: {type(e)}")
            import traceback
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            return []
    
    def get_property_tree_for_prompt(self, root_id: int = 1) -> str:
        """
        Lấy property tree cho prompt
        
        Args:
            root_id (int): ID của root group (mặc định là 1)
            
        Returns:
            str: Property tree đã format cho prompt
        """
        try:
            # Lấy property tree từ database (đã bao gồm unit types)
            # Sử dụng raw SQL để tránh vấn đề với app context
            import pymysql
            
            # Tạo connection đến warehouse database
            connection = pymysql.connect(
                host=os.getenv('DB_WAREHOUSE_HOST', '103.6.234.59'),
                port=int(os.getenv('DB_WAREHOUSE_PORT', '6033')),
                user=os.getenv('DB_WAREHOUSE_USER', 'root'),
                password=os.getenv('DB_WAREHOUSE_PASSWORD', ''),
                database=os.getenv('DB_WAREHOUSE_NAME', 'warehouse'),
                charset='utf8mb4'
            )
            
            property_tree = PropertyService.get_property_tree_for_prompt_with_sql(root_id, connection)
            connection.close()


            return property_tree
            
        except Exception as e:
            logger.error(f"Lỗi khi lấy property tree: {str(e)}")
            # Fallback về hardcoded data nếu có lỗi
            return """Không có thông tin dự án"""
    
    def process_message_with_groq(self, message_content: str) -> Optional[str]:
        """
        Gửi tin nhắn tới Groq API để bóc tách thông tin căn hộ
        
        Args:
            message_content: Nội dung tin nhắn cần xử lý
            
        Returns:
            Kết quả từ Groq API hoặc None nếu lỗi
        """
        try:
            # Lấy property tree từ database
            property_tree = self.get_property_tree_for_prompt()
            
            # Prompt để Groq trả về JSON
            prompt = f"""
            Hãy phân tích tin nhắn rao bán căn hộ trong cặp thẻ XML <message></message> và trả về  duy nhất JSON string chứa thông tin căn hộ như được mô tả trong cặp thẻ XML <output></output>
            
            <message>
            {message_content}
            </message>
            
            

            <output>
{{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Thông tin căn hộ rao bán",
  "type": "object",
  "properties": {{
    "property_group": {{
      "type": "numer",
      "description": "Người dùng đang có căn hộ rao bán tại tòa có ID là bao nhiêu?"
    }},
    "unit_code": {{
      "type": ["string", "null"],
      "description": "Mã căn hộ nếu có"
    }},
    "unit_axis": {{
      "type": ["string", "null"],
      "description": "Trục căn nếu có"
    }},
    "unit_floor_number": {{
      "type": ["integer", "null"],
      "description": "Tầng nếu có"
    }},
    "area_land": {{
      "type": ["number", "null"],
      "description": "Diện tích đất nếu có"
    }},
    "area_construction": {{
      "type": ["number", "null"],
      "description": "Diện tích xây dựng nếu có"
    }},
    "area_net": {{
      "type": ["number", "null"],
      "description": "Diện tích thông thủy nếu có"
    }},
    "area_gross": {{
      "type": ["number", "null"],
      "description": "Diện tích tim tường nếu có"
    }},
    "num_bedrooms": {{
      "type": ["integer", "null"],
      "description": "Số phòng ngủ nếu có"
    }},
    "num_bathrooms": {{
      "type": ["integer", "null"],
      "description": "Số phòng tắm nếu có"
    }},
    "unit_type": {{
      "type": "number",
      "description": "ID của loại căn hộ"
    }},
    "direction_door": {{
      "type": ["string", "null"],
      "enum": ["D", "T", "N", "B", "DB", "DN", "TB", "TN", null],
      "description": "Hướng cửa chính"
    }},
    "direction_balcony": {{
      "type": ["string", "null"],
      "enum": ["D", "T", "N", "B", "DB", "DN", "TB", "TN", null],
      "description": "Hướng ban công"
    }},
    "price": {{
      "type": "number",
      "description": "Giá nếu có. Đơn vị VNĐ"
    }},
    "price_early": {{
      "type": "number",
      "description": "Giá thanh toán sớm nếu có. Đơn vị VNĐ"
    }},
    "price_schedule": {{
      "type": "number",
      "description": "Giá thanh toán theo tiến độ nếu có. Đơn vị VNĐ"
    }},
    "price_loan": {{
      "type": "number",
      "description": "Giá vay ngân hàng nếu có. Đơn vị VNĐ"
    }},
    "price_rent": {{
      "type": "number",
      "description": "Giá vay ngân hàng nếu có. Đơn vị VNĐ"
    }},
    "notes": {{
      "type": ["string", "null"],
      "description": "Ghi chú nếu có"
    }},
    "status": {{
      "type": ["string", "null"],
      "enum": ["CHUA_BAN", "DA_LOCK", "DA_COC", "DA_BAN", null],
      "description": "Trạng thái nếu có"
    }}
  }},
  "required": ["property_group"],
  "additionalProperties": false
}}
</output>



            {property_tree}

            Lưu ý quan trọng:
            - Chỉ trả về duy nhất JSON, không có nội dung nào khác.
            - Không diễn giải, chỉ trả về JSON.
            - Nếu người dùng đề cập diện tích mà không nói là loại diện tích gì thì đó chính là diện tích tim tường.
            - Nếu người dùng đề cập hướng mà không nói là hướng cửa chính hay hướng ban công thì đó chính là hướng cửa chính.
            - Nếu không tìm thấy thông tin nào, trả về null cho trường đó.
            
            
            
            """

            print("prompt")
            print(prompt)
            # exit()
            
            completion = self.groq_client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,  # Giảm temperature để kết quả ổn định hơn với GPT-OSS
                max_completion_tokens=2048,  # Tăng token limit cho GPT-OSS
                top_p=0.9,  # Giảm top_p để tập trung hơn
                stream=True,
                stop=None
            )
            
            # Collect streaming response với error handling tốt hơn
            response_content = ""
            try:
                for chunk in completion:
                    if hasattr(chunk, 'choices') and chunk.choices and len(chunk.choices) > 0:
                        if hasattr(chunk.choices[0], 'delta') and chunk.choices[0].delta:
                            if hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content:
                                response_content += chunk.choices[0].delta.content
            except Exception as stream_error:
                logger.error(f"Error in streaming response: {stream_error}")
                # Fallback: thử lấy response không streaming
                try:
                    completion_no_stream = self.groq_client.chat.completions.create(
                        model="openai/gpt-oss-120b",
                        messages=[
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        temperature=0.1,
                        max_completion_tokens=2048,
                        top_p=0.9,
                        stream=False
                    )
                    response_content = completion_no_stream.choices[0].message.content
                except Exception as fallback_error:
                    logger.error(f"Fallback also failed: {fallback_error}")
                    return None
            
            logger.info(f"GPT-OSS processing completed for message, response length: {len(response_content)}")
            return response_content
            
        except Exception as e:
            logger.error(f"Error processing message with Groq: {e}")
            return None
    
    def parse_groq_response(self, groq_response: str) -> Optional[Dict]:
        """
        Parse JSON response từ Groq/GPT-OSS
        
        Args:
            groq_response: Response từ Groq API
            
        Returns:
            Dict chứa thông tin căn hộ hoặc None nếu lỗi
        """
        try:
            # Clean response để lấy JSON
            response_clean = groq_response.strip()
            
            # Log raw response để debug
            logger.info(f"Raw GPT-OSS response: {response_clean[:300]}...")
            
            # Tìm JSON trong response (có thể có text khác)
            start_idx = response_clean.find('{')
            end_idx = response_clean.rfind('}')
            
            if start_idx == -1 or end_idx == -1:
                logger.error("No JSON found in GPT-OSS response")
                logger.error(f"Full response: {response_clean}")
                return None
            
            json_str = response_clean[start_idx:end_idx + 1]
            logger.info(f"Extracted JSON: {json_str}")
            
            apartment_data = json.loads(json_str)
            
            # Validate và fix data types cho GPT-OSS
            apartment_data = PropertyService.validate_and_fix_apartment_data(apartment_data)
            
            logger.info(f"Successfully parsed GPT-OSS response: {len(apartment_data)} fields")
            return apartment_data
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            logger.error(f"Raw response: {groq_response[:500]}...")
            
            # Thử parse lại với một số fix cơ bản cho GPT-OSS
            try:
                # Fix common JSON issues với GPT-OSS
                fixed_response = response_clean
                
                # Fix các lỗi phổ biến
                fixes = [
                    ('"property_group": "S401"', '"property_group": 401'),
                    ('"unit_axis', '"unit_axis"'),
                    ('"unit_code', '"unit_code"'),
                    ('"price": "3.2 tỷ"', '"price": 3200000000'),
                    ('"area_gross": "85m2"', '"area_gross": 85'),
                    ('"num_bedrooms": "2PN"', '"num_bedrooms": 2'),
                    ('"num_bathrooms": "2WC"', '"num_bathrooms": 2'),
                ]
                
                for old, new in fixes:
                    fixed_response = fixed_response.replace(old, new)
                
                # Tìm JSON lại
                start_idx = fixed_response.find('{')
                end_idx = fixed_response.rfind('}')
                
                if start_idx != -1 and end_idx != -1:
                    json_str = fixed_response[start_idx:end_idx + 1]
                    apartment_data = json.loads(json_str)
                    apartment_data = PropertyService.validate_and_fix_apartment_data(apartment_data)
                    logger.info("Successfully parsed after fixing JSON")
                    return apartment_data
                    
            except Exception as fix_error:
                logger.error(f"Failed to fix JSON: {fix_error}")
            
            return None
        except Exception as e:
            logger.error(f"Error parsing GPT-OSS response: {e}")
            return None
    
    def map_unit_type_to_id(self, unit_type_name) -> Optional[int]:
        """
        Map unit type name sang ID
        
        Args:
            unit_type_name: Tên loại căn hộ (có thể là string hoặc int)
            
        Returns:
            ID tương ứng hoặc None nếu không tìm thấy
        """
        if not unit_type_name:
            return None
        
        # Nếu đã là int thì return luôn
        if isinstance(unit_type_name, int):
            return unit_type_name
            
        # Convert to string nếu cần
        unit_type_str = str(unit_type_name)
            
        # Tìm exact match trước
        if unit_type_str in self.unit_type_mapping:
            return self.unit_type_mapping[unit_type_str]
        
        # Tìm partial match
        for name, id_val in self.unit_type_mapping.items():
            if unit_type_str.lower() in name.lower() or name.lower() in unit_type_str.lower():
                logger.info(f"Mapped '{unit_type_name}' to '{name}' (ID: {id_val})")
                return id_val
        
        logger.warning(f"Unit type '{unit_type_name}' not found in mapping")
        return None
    
    def insert_apartment_via_api(self, apartment_data: Dict) -> tuple[bool, int | None]:
        """
        Insert apartment vào warehouse database thông qua API
        
        Args:
            apartment_data: Dữ liệu căn hộ từ Groq
            
        Returns:
            Tuple (success: bool, apartment_id: int | None)
        """
        try:
            import requests
            
            # Map unit_type name sang ID
            unit_type_id = None
            if apartment_data.get('unit_type'):
                unit_type_id = self.map_unit_type_to_id(apartment_data['unit_type'])
            
            # Chuẩn bị dữ liệu để gửi tới API
            logger.info(f"🔍 Original apartment_data: {apartment_data}")
            logger.info(f"🔍 unit_type_id mapped: {unit_type_id}")
            
            apartment_record = {
                'property_group': apartment_data.get('property_group', 1),  # Default to 1
                'unit_type': unit_type_id,
                'unit_code': apartment_data.get('unit_code'),
                'unit_axis': apartment_data.get('unit_axis'),
                'unit_floor_number': apartment_data.get('unit_floor_number'),
                'area_land': apartment_data.get('area_land'),
                'area_construction': apartment_data.get('area_construction'),
                'area_net': apartment_data.get('area_net'),
                'area_gross': apartment_data.get('area_gross'),
                'num_bedrooms': apartment_data.get('num_bedrooms'),
                'num_bathrooms': apartment_data.get('num_bathrooms'),
                'type_view': apartment_data.get('type_view'),
                'direction_door': apartment_data.get('direction_door'),
                'direction_balcony': apartment_data.get('direction_balcony'),
                'price': apartment_data.get('price'),
                'price_early': apartment_data.get('price_early'),
                'price_schedule': apartment_data.get('price_schedule'),
                'price_loan': apartment_data.get('price_loan'),
                'notes': apartment_data.get('notes'),
                'status': apartment_data.get('status'),
                'unit_allocation': 'QUY_CHEO'  # Luôn set mặc định
            }
            
            logger.info(f"🔍 Prepared apartment_record: {apartment_record}")
            
            # Gọi API warehouse để insert
            api_url = f"http://localhost:5000/warehouse/api/warehouse/apartments/single-insert"
            
            response = requests.post(api_url, json=apartment_record, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    apartment_id = result.get('data', {}).get('apartment_id')
                    logger.info(f"✅ Successfully inserted apartment via API: {apartment_record.get('unit_code', 'N/A')} (ID: {apartment_id})")
                    return True, apartment_id
                else:
                    logger.error(f"❌ API returned error: {result.get('error')}")
                    return False, None
            else:
                logger.error(f"❌ API request failed with status {response.status_code}: {response.text}")
                return False, None
                
        except Exception as e:
            logger.error(f"❌ Error calling warehouse API: {str(e)}")
            logger.error(f"❌ Error type: {type(e)}")
            logger.error(f"❌ Error details: {e}")
            import traceback
            logger.error(f"❌ Full traceback: {traceback.format_exc()}")
            return False, None
                    'unit_floor_number': apartment_data.get('unit_floor_number'),
                    'area_land': apartment_data.get('area_land'),
                    'area_construction': apartment_data.get('area_construction'),
                    'area_net': apartment_data.get('area_net'),
                    'area_gross': apartment_data.get('area_gross'),
                    'num_bedrooms': apartment_data.get('num_bedrooms'),
                    'num_bathrooms': apartment_data.get('num_bathrooms'),
                    'type_view': None,  # Hardcode
                    'direction_door': apartment_data.get('direction_door'),
                    'direction_balcony': apartment_data.get('direction_balcony'),
                    'price': apartment_data.get('price'),
                    'price_early': apartment_data.get('price_early'),
                    'price_schedule': apartment_data.get('price_schedule'),
                    'price_loan': apartment_data.get('price_loan'),
                    'notes': apartment_data.get('notes'),
                    'status': apartment_data.get('status'),
                    'unit_allocation': 'QUY_CHEO'  # Hardcode
                }
                
                # Kiểm tra xem có căn hộ nào với unit_code này chưa
                if apartment_record['unit_code']:
                    check_query = text("SELECT id FROM apartments WHERE unit_code = :unit_code")
                    result = connection.execute(check_query, {"unit_code": apartment_record['unit_code']})
                    existing = result.fetchone()
                    
                    if existing:
                        # Update existing record
                        update_fields = []
                        update_values = {}
                        
                        for field, value in apartment_record.items():
                            if value is not None and field != 'property_group':  # Không update property_group
                                update_fields.append(f"{field} = :{field}")
                                update_values[field] = value
                        
                        if update_fields:
                            update_values['id'] = existing[0]  # Add ID for WHERE clause
                            update_query = text(f"""
                                UPDATE apartments 
                                SET {', '.join(update_fields)}
                                WHERE id = :id
                            """)
                            connection.execute(update_query, update_values)
                            logger.info(f"Updated apartment with unit_code: {apartment_record['unit_code']}")
                    else:
                        # Insert new record
                        insert_fields = []
                        insert_values = {}
                        
                        for field, value in apartment_record.items():
                            if value is not None:
                                insert_fields.append(field)
                                insert_values[field] = value
                        
                        if insert_fields:
                            placeholders = [f":{field}" for field in insert_fields]
                            insert_query = text(f"""
                                INSERT INTO apartments ({', '.join(insert_fields)})
                                VALUES ({', '.join(placeholders)})
                            """)
                            connection.execute(insert_query, insert_values)
                            logger.info(f"Inserted new apartment with unit_code: {apartment_record['unit_code']}")
                else:
                    # Không có unit_code, insert mới
                    insert_fields = []
                    insert_values = {}
                    
                    for field, value in apartment_record.items():
                        if value is not None:
                            insert_fields.append(field)
                            insert_values[field] = value
                    
                    if insert_fields:
                        placeholders = [f":{field}" for field in insert_fields]
                        insert_query = text(f"""
                            INSERT INTO apartments ({', '.join(insert_fields)})
                            VALUES ({', '.join(placeholders)})
                        """)
                        connection.execute(insert_query, insert_values)
                        logger.info("Inserted new apartment without unit_code")
                
                connection.commit()
                return True
                
        except Exception as e:
            logger.error(f"Error inserting/updating apartment: {e}")
            return False
        finally:
            if connection:
                connection.close()
    
    def update_message_status(self, message_id: int, status: str = 'PUSHED') -> bool:
        """
        Cập nhật trạng thái tin nhắn sau khi xử lý với retry mechanism
        
        Args:
            message_id: ID của tin nhắn
            status: Trạng thái mới ('PUSHED' hoặc 'NOT_YET')
            
        Returns:
            True nếu cập nhật thành công, False nếu lỗi
        """
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            connection = None
            try:
                logger.info(f"Updating message {message_id} status to {status} (attempt {attempt + 1}/{max_retries})")
                
                with zalo_app.app_context():
                    connection = self.get_zalo_db_connection()
                    if not connection:
                        logger.error(f"No database connection available (attempt {attempt + 1})")
                        continue
                    
                    from sqlalchemy import text
                    query = text("""
                    UPDATE received_messages 
                    SET status_push_warehouse = :status 
                    WHERE id = :message_id
                    """)
                    
                    connection.execute(query, {"status": status, "message_id": message_id})
                    connection.commit()
                    
                    logger.info(f"✅ Updated message {message_id} status to {status}")
                    return True
                    
            except Exception as e:
                logger.error(f"❌ Error updating message status (attempt {attempt + 1}): {e}")
                logger.error(f"Error type: {type(e)}")
                
                if attempt < max_retries - 1:
                    logger.info(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    logger.error("❌ Failed to update message status after all retries")
                    return False
                    
            finally:
                if connection:
                    try:
                        connection.close()
                    except Exception as close_error:
                        logger.warning(f"Warning: Error closing connection: {close_error}")
        
        return False
    
    def process_messages_batch(self, limit: int = 20):
        """Xử lý một batch tin nhắn"""
        logger.info(f"Starting message batch processing (limit: {limit})...")
        
        # Lấy tin nhắn chưa xử lý
        messages = self.get_unprocessed_messages(limit=limit)
        
        if not messages:
            logger.info("No unprocessed messages found")
            return 0, 0
        
        processed_count = 0
        error_count = 0
        
        for message in messages:
            try:
                message_id = message['id']
                content = message['content']
                
                logger.info(f"Processing message {message_id}")
                
                # Gửi tới Groq để bóc tách thông tin
                groq_result = self.process_message_with_groq(content)
                
                if groq_result:
                    logger.info(f"Groq result for message {message_id}: {groq_result[:100]}...")
                    
                    # Parse JSON từ Groq response
                    apartment_data = self.parse_groq_response(groq_result)
                    
                    if apartment_data:
                        # Insert/update vào warehouse database
                        warehouse_success = self.insert_apartment_via_api(apartment_data)
                        
                        if warehouse_success:
                            # Chỉ cập nhật trạng thái tin nhắn sau khi xử lý warehouse thành công
                            if self.update_message_status(message_id, 'PUSHED'):
                                processed_count += 1
                                logger.info(f"Successfully processed message {message_id}")
                            else:
                                error_count += 1
                                logger.error(f"Failed to update message {message_id} status")
                        else:
                            error_count += 1
                            logger.error(f"Failed to insert/update apartment for message {message_id}")
                    else:
                        error_count += 1
                        logger.error(f"Failed to parse Groq response for message {message_id}")
                else:
                    logger.error(f"Failed to process message {message_id} with Groq")
                    error_count += 1
                    
            except Exception as e:
                logger.error(f"Error processing message {message.get('id', 'unknown')}: {e}")
                error_count += 1
        
        logger.info(f"Batch processing completed. Processed: {processed_count}, Errors: {error_count}")
        return processed_count, error_count
    
    def run_test_mode(self, limit: int = 50):
        """Chế độ test - chạy một số tin nhắn đầu để thử"""
        logger.info(f"🧪 Running in TEST mode - processing {limit} messages")
        
        start_time = time.time()
        processed_count, error_count = self.process_messages_batch(limit=limit)
        elapsed_time = time.time() - start_time
        
        logger.info(f"✅ TEST mode completed in {elapsed_time:.2f}s")
        logger.info(f"📊 Results: {processed_count} processed, {error_count} errors")
        
        return processed_count, error_count
    
    def get_message_by_id(self, message_id: int) -> Optional[Dict]:
        """
        Lấy tin nhắn theo ID
        
        Args:
            message_id: ID của tin nhắn cần lấy
            
        Returns:
            Dict chứa thông tin tin nhắn hoặc None nếu không tìm thấy
        """
        try:
            logger.info(f"🔍 Fetching message with ID: {message_id}")
            
            with zalo_app.app_context():
                connection = self.get_zalo_db_connection()
                if not connection:
                    logger.error("❌ No database connection available")
                    return None
                
                from sqlalchemy import text
                
                query = text("""
                SELECT id, session_id, config_id, sender_id, sender_name, 
                       content, thread_id, thread_type, received_at, 
                       status_push_kafka, status_push_warehouse, reply_quote
                FROM received_messages 
                WHERE id = :message_id
                """)
                
                result = connection.execute(query, {"message_id": message_id})
                row = result.fetchone()
                
                if row:
                    message_data = dict(row._mapping)
                    logger.info(f"✅ Found message {message_id}: {message_data.get('content', '')[:100]}...")
                    return message_data
                else:
                    logger.warning(f"❌ Message with ID {message_id} not found")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Error fetching message {message_id}: {e}")
            return None
        finally:
            if connection:
                connection.close()
    
    def run_test_one_mode(self, message_id: int):
        """
        Chế độ test one - test một tin nhắn cụ thể theo ID
        
        Args:
            message_id: ID của tin nhắn cần test
        """
        logger.info(f"🧪 Running in TEST-ONE mode - processing message ID: {message_id}")
        
        start_time = time.time()
        
        try:
            # Lấy tin nhắn theo ID
            message = self.get_message_by_id(message_id)
            
            if not message:
                logger.error(f"❌ Message with ID {message_id} not found")
                return None, "Message not found"
            
            content = message['content']
            logger.info(f"📝 Message content: {content}")
            
            # Gửi tới Groq để bóc tách thông tin
            logger.info("🤖 Processing with Groq...")
            groq_result = self.process_message_with_groq(content)
            
            
            if groq_result:
                logger.info(f"✅ Groq result: {groq_result}")
                
                # Parse JSON từ Groq response
                apartment_data = self.parse_groq_response(groq_result)
                
                if apartment_data:
                    logger.info(f"📊 Parsed apartment data: {apartment_data}")
                    
                    # Test insert/update vào warehouse database (không commit thật)
                    logger.info("🏠 Testing warehouse insert/update...")
                    warehouse_success = self.insert_apartment_via_api(apartment_data)
                    
                    if warehouse_success:
                        logger.info("✅ Warehouse insert/update successful")
                        result = {
                            'message_id': message_id,
                            'message_content': content,
                            'groq_result': groq_result,
                            'parsed_data': apartment_data,
                            'warehouse_success': True
                        }
                    else:
                        logger.error("❌ Warehouse insert/update failed")
                        result = {
                            'message_id': message_id,
                            'message_content': content,
                            'groq_result': groq_result,
                            'parsed_data': apartment_data,
                            'warehouse_success': False,
                            'error': 'Warehouse insert/update failed'
                        }
                else:
                    logger.error("❌ Failed to parse Groq response")
                    result = {
                        'message_id': message_id,
                        'message_content': content,
                        'groq_result': groq_result,
                        'parsed_data': None,
                        'warehouse_success': False,
                        'error': 'Failed to parse Groq response'
                    }
            else:
                logger.error("❌ Failed to process message with Groq")
                result = {
                    'message_id': message_id,
                    'message_content': content,
                    'groq_result': None,
                    'parsed_data': None,
                    'warehouse_success': False,
                    'error': 'Failed to process with Groq'
                }
            
            elapsed_time = time.time() - start_time
            logger.info(f"✅ TEST-ONE mode completed in {elapsed_time:.2f}s")
            
            return result, None
            
        except Exception as e:
            logger.error(f"❌ Error in test-one mode: {e}")
            return None, str(e)
    
    def run_batch_mode(self):
        """Chế độ batch - chạy tất cả tin nhắn từ trước đến nay"""
        logger.info("📦 Running in BATCH mode - processing ALL unprocessed messages")
        
        total_processed = 0
        total_errors = 0
        batch_size = 100  # Xử lý từng batch 100 tin nhắn
        batch_count = 0
        
        start_time = time.time()
        
        while True:
            batch_count += 1
            logger.info(f"Processing batch {batch_count} (size: {batch_size})")
            
            processed_count, error_count = self.process_messages_batch(limit=batch_size)
            
            total_processed += processed_count
            total_errors += error_count
            
            # Nếu không có tin nhắn nào được xử lý, dừng lại
            if processed_count == 0:
                break
                
            logger.info(f"Batch {batch_count} completed: {processed_count} processed, {error_count} errors")
        
        elapsed_time = time.time() - start_time
        
        logger.info(f"✅ BATCH mode completed in {elapsed_time:.2f}s")
        logger.info(f"📊 Total results: {total_processed} processed, {total_errors} errors across {batch_count} batches")
        
        return total_processed, total_errors
    
    def run_scheduler_mode(self):
        """Chế độ scheduler - chạy định kỳ như hiện tại"""
        logger.info(f"⏰ Running in SCHEDULER mode (interval: {self.interval//60} minutes)")
        
        while self.is_running:
            try:
                start_time = time.time()
                
                # Xử lý batch tin nhắn
                self.process_messages_batch(limit=20)
                
                # Tính thời gian còn lại để sleep
                elapsed_time = time.time() - start_time
                sleep_time = max(0, self.interval - elapsed_time)
                
                logger.info(f"Processing completed in {elapsed_time:.2f}s. Sleeping for {sleep_time/60:.1f} minutes")
                
                # Sleep với kiểm tra is_running để có thể dừng nhanh
                for _ in range(int(sleep_time)):
                    if not self.is_running:
                        break
                    time.sleep(1)
                    
            except Exception as e:
                logger.error(f"Error in scheduler: {e}")
                # Sleep 60 giây nếu có lỗi để tránh spam
                time.sleep(60)
    
    def run_scheduler(self):
        """Chạy scheduler định kỳ (legacy method)"""
        self.run_scheduler_mode()
    
    def start(self):
        """Bắt đầu service"""
        if self.is_running:
            logger.warning("Service is already running")
            return
        
        # Kiểm tra xem schedule có được enable không
        if not self.schedule_enabled:
            logger.info("ZaloMessageProcessor schedule is disabled (ZALO_MESSAGE_PROCESSOR_SCHEDULE=0)")
            return
        
        self.is_running = True
        self.thread = threading.Thread(target=self.run_scheduler, daemon=True)
        self.thread.start()
        
        logger.info(f"ZaloMessageProcessor service started (interval: {self.interval//60} minutes)")
    
    def stop(self):
        """Dừng service"""
        if not self.is_running:
            logger.warning("Service is not running")
            return
        
        self.is_running = False
        
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=5)
        
        logger.info("ZaloMessageProcessor service stopped")
    
    def get_status(self) -> Dict:
        """Lấy trạng thái service"""
        return {
            'is_running': self.is_running,
            'thread_alive': self.thread.is_alive() if self.thread else False,
            'interval': self.interval,
            'interval_minutes': self.interval // 60,
            'schedule_enabled': self.schedule_enabled,
            'started_at': datetime.now().isoformat() if self.is_running else None
        }


# Global instance
zalo_processor = ZaloMessageProcessor()

def main():
    """Main function với command line arguments"""
    parser = argparse.ArgumentParser(description='Zalo Message Processor Service')
    parser.add_argument('--mode', choices=['test', 'test-one', 'batch', 'scheduler'], default='scheduler',
                       help='Chế độ chạy: test (50 tin nhắn), test-one (1 tin nhắn theo ID), batch (tất cả), scheduler (định kỳ)')
    parser.add_argument('--limit', type=int, default=50,
                       help='Số lượng tin nhắn cho chế độ test (default: 50)')
    parser.add_argument('--message-id', type=int,
                       help='ID của tin nhắn cần test (chỉ dùng với mode test-one)')
    
    args = parser.parse_args()
    
    try:
        if args.mode == 'test':
            logger.info(f"🧪 Starting ZaloMessageProcessor in TEST mode (limit: {args.limit})")
            zalo_processor.run_test_mode(limit=args.limit)
            
        elif args.mode == 'test-one':
            if not args.message_id:
                logger.error("❌ --message-id is required for test-one mode")
                return
            logger.info(f"🧪 Starting ZaloMessageProcessor in TEST-ONE mode (message ID: {args.message_id})")
            result, error = zalo_processor.run_test_one_mode(args.message_id)
            
            if error:
                logger.error(f"❌ Test failed: {error}")
            else:
                logger.info("✅ Test completed successfully")
                logger.info(f"📊 Result: {result}")
            
        elif args.mode == 'batch':
            logger.info("📦 Starting ZaloMessageProcessor in BATCH mode")
            zalo_processor.run_batch_mode()
            
        elif args.mode == 'scheduler':
            logger.info("⏰ Starting ZaloMessageProcessor in SCHEDULER mode")
            zalo_processor.start()
            
            # Giữ service chạy
            while zalo_processor.is_running:
                time.sleep(1)
                
    except KeyboardInterrupt:
        logger.info("Received interrupt signal, stopping service...")
        if args.mode == 'scheduler':
            zalo_processor.stop()
    except Exception as e:
        logger.error(f"Service error: {e}")
        if args.mode == 'scheduler':
            zalo_processor.stop()

if __name__ == "__main__":
    main()
