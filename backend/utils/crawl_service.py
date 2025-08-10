import json
import requests
from datetime import datetime
from models import User, LinkCrawl, Document, DocumentChunk, db
from utils.groq_service import GroqChat
from utils.vector_service import get_vector_service
from flask import current_app


class CrawlService:
    def __init__(self):
        self.groq_chat = GroqChat(
            max_tokens=32768,
            temperature=0.8,
            model="llama-3.3-70b-versatile",
            stream=False
        )
    
    def call_firecrawl_api(self, link):
        """Gọi API firecrawl để crawl nội dung từ link"""
        try:
            # Lấy cấu hình từ app config
            firecrawl_url = current_app.config.get('FIRECRAWL_API_URL', 'https://api.firecrawl.dev/scrape')
            api_key = current_app.config.get('FIRECRAWL_API_KEY', '')
            
            # Headers cho API request
            headers = {
                'Content-Type': 'application/json'
            }
            
            # Thêm API key nếu có
            if api_key:
                headers['Authorization'] = f'Bearer {api_key}'
            
            # Payload cho API request
            payload = {
                'url': link,
                "formats": [ "markdown" ],
                "onlyMainContent": True,
                "parsePDF": True,
            }

            # Gọi API
            response = requests.post(firecrawl_url, json=payload, headers=headers, timeout=30)
            
            # Kiểm tra response
            if response.status_code != 200:
                raise Exception(f"API returned status {response.status_code}: {response.text}")
            
            # Kiểm tra response content
            if not response.text.strip():
                raise Exception("API returned empty response")
            
            try:
                result = response.json()
            except json.JSONDecodeError as e:
                raise Exception(f"Invalid JSON response: {response.text[:200]}")
            
            # Trả về nội dung đã crawl
            content = result.get('data', {}).get('markdown', '')
            if not content:
                # Fallback: sử dụng HTML content nếu có
                content = result.get('data', {}).get('html', '')
                if not content:
                    content = f"Content crawled from {link} (no markdown/html content available)"
            
            return {
                'content': content,
                'status': 'success'
            }
            
        except requests.exceptions.RequestException as e:
            # Fallback: trả về mock content nếu API không khả dụng
            print(f"Warning: Firecrawl API not available: {str(e)}")
            return {
                'content': f"Mock content for {link}\n\nThis is a fallback response when the firecrawl API is not available. The actual content would be crawled from the provided URL.",
                'status': 'fallback'
            }
        except Exception as e:
            # Fallback cho các lỗi khác
            print(f"Warning: Error calling firecrawl API: {str(e)}")
            return {
                'content': f"Error content for {link}\n\nError occurred while crawling: {str(e)}",
                'status': 'error'
            }
    
    def chunk_content(self, content):
        """Chia content thành các chunks sử dụng Groq"""
        prompt = f'''
        Hãy chia nội dung trong <content></content> thành các chunk dưới 300 từ và trả về dưới dạng json array có schema như sau:

        {{
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "array",
        "title": "Danh sách các chunk",
        "items": {{
            "type": "string",
            "title": "Đoạn văn",
            "minLength": 1
        }},
        "minItems": 1,
        "uniqueItems": false
        }}

        <content>
        {content}
        </content>

        Quy tắc bắt buộc:
        - Chỉ trả về kết quả cuối cùng, không diễn giải cách làm.
        - Không nói về cặp thẻ <content></content> trong câu trả lời.
        '''
        
        response = self.groq_chat.chat(prompt, "Hãy chia chunk").clean()
        return json.loads(response)
    
    def process_chunks_to_milvus(self, document_id, chunks):
        """Xử lý chunks và lưu vào database + Milvus"""
        vector_service = get_vector_service()
        chunk_index = 0
        successful_milvus_inserts = 0
        failed_milvus_inserts = 0
        
        print(f"🔄 Processing {len(chunks)} chunks...")
        
        for chunk_content in chunks:
            print(f"📝 Processing chunk {chunk_index + 1}/{len(chunks)}")
            
            # Tạo document chunk trong database
            document_chunk = DocumentChunk(
                document_id=document_id,
                chunk_index=chunk_index,
                content=chunk_content,
            )
            db.session.add(document_chunk)
            db.session.flush()  # Để lấy ID của document_chunk
            
            # Tạo embedding và lưu vào Milvus
            try:
                print(f"🔗 Inserting chunk {chunk_index} into Milvus...")
                milvus_id = vector_service.insert_chunk(
                    document_id=document_id,
                    chunk_index=chunk_index,
                    content=chunk_content
                )
                
                # Cập nhật milvus_id trong database
                document_chunk.milvus_id = milvus_id
                print(f"✅ Chunk {chunk_index} inserted into Milvus with ID: {milvus_id}")
                successful_milvus_inserts += 1
                
            except Exception as e:
                print(f"⚠️ Warning: Failed to insert chunk {chunk_index} into Milvus: {e}")
                # Chunk vẫn được lưu trong database nhưng không có milvus_id
                document_chunk.milvus_id = None
                failed_milvus_inserts += 1
            
            # Commit từng chunk để tránh mất dữ liệu
            db.session.commit()
            chunk_index += 1
        
        print(f"📊 Milvus insertion summary:")
        print(f"   ✅ Successful: {successful_milvus_inserts}")
        print(f"   ❌ Failed: {failed_milvus_inserts}")
        print(f"   📝 Total chunks: {chunk_index}")
        
        return {
            'successful': successful_milvus_inserts,
            'failed': failed_milvus_inserts,
            'total': chunk_index
        }
    
    def get_or_create_document(self, user_id, link, title=None):
        """Lấy hoặc tạo document cho một crawl"""
        if not title:
            title = f"Crawl {link}"
        
        document = Document.query.filter_by(
            user_id=user_id,
            source_type='web',
            source_path=link
        ).first()
        
        if not document:
            print(f"📄 Creating new document for link {link}")
            document = Document(
                user_id=user_id,
                category_id=1,  # Default category
                title=title,
                source_type='web',
                source_path=link,
            )
            db.session.add(document)
            db.session.flush()  # Để lấy ID của document
            print(f"✅ Created document with ID: {document.id}")
        
        return document
    
    def clear_document_chunks(self, document_id):
        """Xóa tất cả chunks của document từ database và Milvus"""
        old_chunks = DocumentChunk.query.filter_by(document_id=document_id).all()
        vector_service = get_vector_service()
        
        for chunk in old_chunks:
            # Xóa khỏi Milvus nếu có milvus_id
            if chunk.milvus_id:
                try:
                    vector_service.delete_chunk(chunk.milvus_id)
                except Exception as e:
                    print(f"Warning: Failed to delete chunk {chunk.milvus_id} from Milvus: {e}")
            db.session.delete(chunk)
        
        return len(old_chunks)
    
    def create_crawl(self, user_id, link, crawl_tool='firecrawl'):
        """Tạo crawl request và xử lý content"""
        # Ghi lại thời gian bắt đầu
        started_at = datetime.utcnow()
        
        # Gọi API firecrawl
        firecrawl_response = self.call_firecrawl_api(link)
        
        # Ghi lại thời gian kết thúc
        done_at = datetime.utcnow()
        
        # Lưu vào database
        link_crawl = LinkCrawl(
            link=link,
            content=firecrawl_response.get('content', ''),
            crawl_tool=crawl_tool,
            user_id=user_id,
            started_at=started_at,
            done_at=done_at
        )
        
        db.session.add(link_crawl)
        db.session.commit()
        
        # Xử lý content thành chunks
        content = firecrawl_response.get('content', '')
        chunks = self.chunk_content(content)
        
        # Tạo document
        document = self.get_or_create_document(user_id, link)
        
        # Xử lý chunks và lưu vào Milvus
        milvus_results = self.process_chunks_to_milvus(document.id, chunks)
        
        return {
            'crawl_id': link_crawl.id,
            'document_id': document.id,
            'link': link,
            'crawl_tool': crawl_tool,
            'started_at': started_at.isoformat(),
            'done_at': done_at.isoformat(),
            'content_length': len(content),
            'chunks_processed': len(chunks),
            'milvus_inserts': milvus_results
        }
    
    def update_crawl_content(self, crawl_id, new_content, user_id):
        """Cập nhật content của crawl và tái tạo chunks"""
        # Lấy crawl record
        crawl = LinkCrawl.query.get(crawl_id)
        if not crawl:
            raise Exception('Crawl not found')
        
        # Cập nhật content trong bảng link_crawls
        crawl.content = new_content
        crawl.done_at = datetime.utcnow()
        
        # Lấy hoặc tạo document
        document = self.get_or_create_document(crawl.user_id, crawl.link)
        
        # Xóa chunks cũ
        self.clear_document_chunks(document.id)
        
        # Tạo chunks mới từ content đã cập nhật
        chunks = self.chunk_content(new_content)
        
        # Xử lý chunks và lưu vào Milvus
        milvus_results = self.process_chunks_to_milvus(document.id, chunks)
        
        return {
            'crawl_id': crawl.id,
            'document_id': document.id,
            'content_length': len(new_content),
            'chunks_processed': len(chunks),
            'milvus_inserts': milvus_results
        }
    
    def recrawl_content(self, crawl_id, user_id):
        """Crawl lại content từ URL và cập nhật chunks"""
        # Lấy crawl record
        crawl = LinkCrawl.query.get(crawl_id)
        if not crawl:
            raise Exception('Crawl not found')
        
        # Ghi lại thời gian bắt đầu
        started_at = datetime.utcnow()
        
        # Gọi API firecrawl để crawl lại
        firecrawl_response = self.call_firecrawl_api(crawl.link)
        
        # Ghi lại thời gian kết thúc
        done_at = datetime.utcnow()
        
        # Cập nhật content và thời gian
        new_content = firecrawl_response.get('content', '')
        crawl.content = new_content
        crawl.started_at = started_at
        crawl.done_at = done_at
        
        # Lấy hoặc tạo document
        document = self.get_or_create_document(crawl.user_id, crawl.link)
        
        # Xóa chunks cũ
        self.clear_document_chunks(document.id)
        
        # Tạo chunks mới từ content đã crawl lại
        chunks = self.chunk_content(new_content)
        
        # Xử lý chunks và lưu vào Milvus
        milvus_results = self.process_chunks_to_milvus(document.id, chunks)
        
        return {
            'crawl_id': crawl.id,
            'document_id': document.id,
            'link': crawl.link,
            'crawl_tool': crawl.crawl_tool,
            'started_at': started_at.isoformat(),
            'done_at': done_at.isoformat(),
            'content_length': len(new_content),
            'chunks_processed': len(chunks),
            'milvus_inserts': milvus_results
        } 