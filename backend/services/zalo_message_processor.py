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
from .warehouse_database_service import warehouse_service

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
logger.info(f"DB_NAME: {os.getenv('DB_NAME', 'NOT_SET')}")
logger.info(f"DB_WAREHOUSE_HOST: {os.getenv('DB_WAREHOUSE_HOST', 'NOT_SET')}")
logger.info(f"DB_WAREHOUSE_PORT: {os.getenv('DB_WAREHOUSE_PORT', 'NOT_SET')}")
logger.info(f"DB_WAREHOUSE_USER: {os.getenv('DB_WAREHOUSE_USER', 'NOT_SET')}")
logger.info(f"DB_WAREHOUSE_PASSWORD: {'SET' if os.getenv('DB_WAREHOUSE_PASSWORD') else 'NOT_SET'}")
logger.info(f"DB_WAREHOUSE_NAME: {os.getenv('DB_WAREHOUSE_NAME', 'NOT_SET')}")

# Tạo Flask app cho easychat database
zalo_app = Flask(__name__)
zalo_app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql://{os.getenv('DB_CHAT_USER', 'easychat')}:{os.getenv('DB_CHAT_PASSWORD', '')}@{os.getenv('DB_CHAT_HOST', '103.6.234.59')}:{os.getenv('DB_CHAT_PORT', '6033')}/{os.getenv('DB_NAME', 'easychat')}"
zalo_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
zalo_db = SQLAlchemy(zalo_app)

# Warehouse database service được import từ warehouse_database_service.py

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
        
        # Warehouse service instance
        self.warehouse_service = warehouse_service
        
        logger.info(f"ZaloMessageProcessor initialized (schedule: {self.interval//60} minutes, enabled: {self.schedule_enabled})")
    
    def get_zalo_db_connection(self):
        """Tạo kết nối database easychat với retry mechanism"""
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Attempting to connect to easychat database... (attempt {attempt + 1}/{max_retries})")
                
                with zalo_app.app_context():
                    # Sử dụng SQLAlchemy engine với connection pooling
                    connection = zalo_db.engine.connect()
                    logger.info("✅ Easychat database connection successful")
                    return connection
                    
            except Exception as e:
                logger.error(f"❌ Easychat database connection error (attempt {attempt + 1}): {e}")
                logger.error(f"Error type: {type(e)}")
                
                if attempt < max_retries - 1:
                    logger.info(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    logger.error("❌ Failed to connect to easychat database after all retries")
        
        return None
    
    def get_warehouse_db_connection(self):
        """Tạo kết nối database warehouse với retry mechanism"""
        return self.warehouse_service.get_warehouse_db_connection()
    
    def get_unprocessed_messages(self, limit: int = 20, warehouse_id: str = 'NULL') -> List[Dict]:
        """
        Lấy danh sách tin nhắn từ bảng zalo_received_messages trong database easychat theo warehouse_id
        
        Args:
            limit: Số lượng tin nhắn tối đa cần lấy
            warehouse_id: Trạng thái warehouse_id ('NULL', 'NOT_NULL', 'ALL')
            
        Returns:
            List các tin nhắn theo warehouse_id
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
                        
                        # Xây dựng WHERE clause dựa trên warehouse_id
                        if warehouse_id == 'ALL':
                            where_clause = ""
                            params = {"limit": limit}
                        elif warehouse_id == 'NULL':
                            where_clause = "WHERE warehouse_id IS NULL"
                            params = {"limit": limit}
                        elif warehouse_id == 'NOT_NULL':
                            where_clause = "WHERE warehouse_id IS NOT NULL"
                            params = {"limit": limit}
                        else:
                            # Nếu warehouse_id là một số cụ thể
                            where_clause = "WHERE warehouse_id = :warehouse_id"
                            params = {"limit": limit, "warehouse_id": warehouse_id}
                        
                        query = text(f"""
                        SELECT id, session_id, config_id, sender_id, sender_name, 
                               content, thread_id, thread_type, received_at, 
                               status_push_kafka, warehouse_id, reply_quote,
                               content_hash, added_document_chunks
                        FROM zalo_received_messages 
                        {where_clause}
                        ORDER BY received_at ASC 
                        LIMIT :limit
                        """)
                        
                        logger.info(f"🔍 Query: {query}")
                        logger.info(f"🔍 Limit: {limit}")
                        logger.info(f"🔍 Warehouse ID filter: {warehouse_id}")
                        
                        result = connection.execute(query, params)
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
        return self.warehouse_service.get_property_tree_for_prompt(root_id)
    
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
            - Nếu bài đăng có giá tiền triệu thì đó là giá thuê, giá tiền tỷ thì đó là giá bán.
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
        return self.warehouse_service.map_unit_type_to_id(unit_type_name)
    
    def insert_apartment_via_api(self, apartment_data: Dict) -> bool:
        """
        Insert apartment vào warehouse database thông qua API
        
        Args:
            apartment_data: Dữ liệu căn hộ từ Groq
            
        Returns:
            True nếu thành công, False nếu lỗi
        """
        return self.warehouse_service.insert_apartment_via_api(apartment_data)
    
    def update_message_warehouse_id(self, message_id: int, warehouse_id: int) -> bool:
        """
        Cập nhật warehouse_id của tin nhắn sau khi xử lý với retry mechanism
        
        Args:
            message_id: ID của tin nhắn
            warehouse_id: ID của apartment trong warehouse database
            
        Returns:
            True nếu cập nhật thành công, False nếu lỗi
        """
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            connection = None
            try:
                logger.info(f"Updating message {message_id} warehouse_id to {warehouse_id} (attempt {attempt + 1}/{max_retries})")
                
                with zalo_app.app_context():
                    connection = self.get_zalo_db_connection()
                    if not connection:
                        logger.error(f"No database connection available (attempt {attempt + 1})")
                        continue
                
                from sqlalchemy import text
                query = text("""
                UPDATE zalo_received_messages 
                SET warehouse_id = :warehouse_id 
                WHERE id = :message_id
                """)
                
                connection.execute(query, {"warehouse_id": warehouse_id, "message_id": message_id})
                connection.commit()
                
                logger.info(f"✅ Updated message {message_id} warehouse_id to {warehouse_id}")
                return True
                
            except Exception as e:
                logger.error(f"❌ Error updating message warehouse_id (attempt {attempt + 1}): {e}")
                logger.error(f"Error type: {type(e)}")
                
                if attempt < max_retries - 1:
                    logger.info(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    logger.error("❌ Failed to update message warehouse_id after all retries")
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
                            # Chỉ cập nhật warehouse_id của tin nhắn sau khi xử lý warehouse thành công
                            if self.update_message_warehouse_id(message_id, warehouse_success):
                                processed_count += 1
                                logger.info(f"Successfully processed message {message_id} with warehouse_id {warehouse_success}")
                            else:
                                error_count += 1
                                logger.error(f"Failed to update message {message_id} warehouse_id")
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
                       status_push_kafka, warehouse_id, reply_quote,
                       content_hash, added_document_chunks
                FROM zalo_received_messages 
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
    
    def run_test_one_mode(self, message_id: int, real_insert: bool = False):
        """
        Chế độ test one - test một tin nhắn cụ thể theo ID
        
        Args:
            message_id: ID của tin nhắn cần test
            real_insert: Nếu True, sẽ thực sự insert vào warehouse và cập nhật warehouse_id
        """
        mode_text = "REAL INSERT" if real_insert else "TEST MODE"
        logger.info(f"🧪 Running in TEST-ONE mode ({mode_text}) - processing message ID: {message_id}")
        
        start_time = time.time()
        
        try:
            # Lấy tin nhắn theo ID
            message = self.get_message_by_id(message_id)
            
            if not message:
                logger.error(f"❌ Message with ID {message_id} not found")
                return None, "Message not found"
            
            content = message['content']
            current_warehouse_id = message.get('warehouse_id')
            
            logger.info(f"📝 Message content: {content}")
            if current_warehouse_id:
                logger.info(f"🔄 Message already has warehouse_id: {current_warehouse_id} - will replace")
            else:
                logger.info(f"🆕 Message has no warehouse_id - will create new")
            
            # Gửi tới Groq để bóc tách thông tin
            logger.info("🤖 Processing with Groq...")
            groq_result = self.process_message_with_groq(content)
            
            
            if groq_result:
                logger.info(f"✅ Groq result: {groq_result}")
                
                # Parse JSON từ Groq response
                apartment_data = self.parse_groq_response(groq_result)
                
                if apartment_data:
                    logger.info(f"📊 Parsed apartment data: {apartment_data}")
                    
                    # Insert/update vào warehouse database
                    if current_warehouse_id:
                        logger.info(f"🔄 Replacing existing apartment (ID: {current_warehouse_id})...")
                    else:
                        logger.info("🏠 Creating new apartment...")
                    
                    warehouse_result = self.insert_apartment_via_api(apartment_data)
                    
                    if warehouse_result:
                        logger.info("✅ Warehouse insert/update successful")
                        
                        # Chỉ cập nhật warehouse_id khi real_insert=True
                        if real_insert and isinstance(warehouse_result, int):
                            if current_warehouse_id:
                                logger.info(f"🔄 Replacing warehouse_id from {current_warehouse_id} to {warehouse_result} for message {message_id}")
                            else:
                                logger.info(f"🆕 Setting warehouse_id {warehouse_result} for message {message_id}")
                            
                            update_success = self.update_message_warehouse_id(message_id, warehouse_result)
                            
                            if update_success:
                                logger.info(f"✅ Successfully updated warehouse_id for message {message_id}")
                            else:
                                logger.error(f"❌ Failed to update warehouse_id for message {message_id}")
                        elif not real_insert:
                            logger.info("ℹ️  Test mode - warehouse_id not updated to database")
                        
                        result = {
                            'message_id': message_id,
                            'message_content': content,
                            'groq_result': groq_result,
                            'parsed_data': apartment_data,
                            'warehouse_success': True,
                            'apartment_id': warehouse_result if isinstance(warehouse_result, int) else None,
                            'real_insert': real_insert,
                            'replaced': current_warehouse_id is not None,
                            'previous_warehouse_id': current_warehouse_id
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
        
        logger.info("🛑 Stopping ZaloMessageProcessor service...")
        self.is_running = False
        
        if self.thread and self.thread.is_alive():
            logger.info("⏳ Waiting for thread to finish...")
            self.thread.join(timeout=10)  # Tăng timeout lên 10 giây
            
            if self.thread.is_alive():
                logger.warning("⚠️ Thread did not stop gracefully, forcing shutdown")
            else:
                logger.info("✅ Thread stopped gracefully")
        
        logger.info("🛑 ZaloMessageProcessor service stopped")
    
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
