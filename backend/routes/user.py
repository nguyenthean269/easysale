from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.permissions import require_roles, require_permissions, require_ownership
from utils.rate_limit import apply_rate_limit
from utils.groq_service import GroqChat
from utils.vector_service import get_vector_service
from models import User, LinkCrawl, Document, DocumentChunk, db
import requests
import json
from datetime import datetime
import time

user_bp = Blueprint('user', __name__)

@user_bp.route('/profile')
@require_roles('user', 'manager', 'admin')
@apply_rate_limit("30 per minute")
def user_profile():
    identity = get_jwt_identity()
    return jsonify({
        'message': f"Welcome, {identity['username']}!",
        'role': identity['role'],
        'user_id': identity['user_id']
    })

@user_bp.route('/profile', methods=['PUT'])
@require_roles('user', 'manager', 'admin')
@require_permissions('user:write')
@apply_rate_limit("20 per minute")
def update_profile():
    """Cập nhật thông tin profile của chính mình"""
    identity = get_jwt_identity()
    user_id = identity['user_id']
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    
    # Chỉ cho phép cập nhật một số trường
    if 'full_name' in data:
        user.full_name = data['full_name']
    if 'phone' in data:
        user.phone = data['phone']
    if 'email' in data:
        # Kiểm tra email không trùng lặp
        existing_email = User.query.filter_by(email=data['email']).first()
        if existing_email and existing_email.id != user_id:
            return jsonify({'error': 'Email đã được sử dụng'}), 400
        user.email = data['email']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Cập nhật profile thành công',
        'user': user.to_dict()
    })

@user_bp.route('/users/<int:user_id>')
@require_ownership('user')
@apply_rate_limit("30 per minute")
def get_own_profile(user_id):
    """Lấy thông tin profile của chính mình hoặc admin có thể xem tất cả"""
    current_user_id = int(get_jwt_identity())
    # Lấy user để biết role
    current_user = User.query.get(current_user_id)
    if not current_user:
        return jsonify({'error': 'User not found'}), 404
    user_role = current_user.role
    
    # Admin có thể xem tất cả
    if user_role == 'admin':
        user = User.query.get(user_id)
    else:
        # User thường chỉ xem được thông tin của chính mình
        user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'message': 'Thông tin profile',
        'user': user.to_dict()
    })

def retry_failed_milvus_inserts(document_id):
    """Retry insert các chunks bị fail vào Milvus"""
    try:
        from models import DocumentChunk
        from utils.vector_service import get_vector_service
        
        # Lấy các chunks không có milvus_id
        failed_chunks = DocumentChunk.query.filter_by(
            document_id=document_id,
            milvus_id=None
        ).all()
        
        if not failed_chunks:
            print(f"✅ No failed chunks to retry for document {document_id}")
            return {'successful': 0, 'failed': 0}
        
        print(f"🔄 Retrying {len(failed_chunks)} failed chunks for document {document_id}")
        
        vector_service = get_vector_service()
        successful = 0
        failed = 0
        
        for chunk in failed_chunks:
            try:
                print(f"🔗 Retrying chunk {chunk.chunk_index}...")
                milvus_id = vector_service.insert_chunk(
                    document_id=chunk.document_id,
                    chunk_index=chunk.chunk_index,
                    content=chunk.content
                )
                
                chunk.milvus_id = milvus_id
                db.session.commit()
                print(f"✅ Chunk {chunk.chunk_index} retry successful: {milvus_id}")
                successful += 1
                
            except Exception as e:
                print(f"❌ Chunk {chunk.chunk_index} retry failed: {e}")
                failed += 1
        
        print(f"📊 Retry summary: {successful} successful, {failed} failed")
        return {'successful': successful, 'failed': failed}
        
    except Exception as e:
        print(f"❌ Error in retry_failed_milvus_inserts: {e}")
        return {'successful': 0, 'failed': len(failed_chunks)}

@user_bp.route('/crawls', methods=['POST'])
@require_roles('user', 'manager', 'admin')
@apply_rate_limit("10 per minute")
def create_crawl():
    """Tạo crawl request và gọi API firecrawl"""
    user_id = int(get_jwt_identity())
    
    data = request.get_json()
    
    # Validate input
    if not data or 'link' not in data:
        return jsonify({'error': 'Link is required'}), 400
    
    link = data['link']
    crawl_tool = data.get('crawl_tool', 'firecrawl')  # Default to firecrawl
    
    # Validate crawl_tool
    if crawl_tool not in ['firecrawl', 'watercrawl']:
        return jsonify({'error': 'crawl_tool must be either "firecrawl" or "watercrawl"'}), 400
    
    try:
        # Ghi lại thời gian bắt đầu
        started_at = datetime.utcnow()
        
        # Gọi API firecrawl
        firecrawl_response = call_firecrawl_api(link)
        
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

        groq_chat = GroqChat(
            # max_tokens=8192,
            max_tokens=32768,
            temperature=0.8,
            # model="deepseek-r1-distill-llama-70b",
            model="llama-3.3-70b-versatile",
            # model="gemma2-9b-it",
            # model="qwen-qwq-32b",
            # response_format={
            #     "type": "json_object"
            # }
            stream=False
        )

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
        {firecrawl_response.get('content', '')}
        </content>

        Quy tắc bắt buộc:
        - Chỉ trả về kết quả cuối cùng, không diễn giải cách làm.
        - Không nói về cặp thẻ <content></content> trong câu trả lời.
        '''
        print(prompt)
        response = groq_chat.chat(prompt, "Hãy chia chunk").clean()
        print(response)
        print(json.loads(response))



        # Thêm dữ liệu crawl vào bảng document
        document = Document(
            user_id=user_id,
            category_id=1,
            title=f"Crawl {link}",
            source_type="web",
            source_path=link,
        )
        db.session.add(document)
        db.session.commit()

        # Thêm dữ liệu chunk vào bảng document_chunks
        vector_service = get_vector_service()
        chunk_index = 0
        successful_milvus_inserts = 0
        failed_milvus_inserts = 0
        
        print(f"🔄 Processing {len(json.loads(response))} chunks...")
        
        for chunk in json.loads(response):
            print(f"📝 Processing chunk {chunk_index + 1}/{len(json.loads(response))}")
            
            # Tạo document chunk trong database
            document_chunk = DocumentChunk(
                document_id=document.id,
                chunk_index=chunk_index,
                content=chunk,
            )
            db.session.add(document_chunk)
            db.session.flush()  # Để lấy ID của document_chunk
            
            # Tạo embedding và lưu vào Milvus
            try:
                print(f"🔗 Inserting chunk {chunk_index} into Milvus...")
                milvus_id = vector_service.insert_chunk(
                    document_id=document.id,
                    chunk_index=chunk_index,
                    content=chunk
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

            
        return jsonify({
            'message': 'Crawl completed successfully',
            'crawl_id': link_crawl.id,
            'document_id': document.id,
            'link': link,
            'crawl_tool': crawl_tool,
            'started_at': started_at.isoformat(),
            'done_at': done_at.isoformat(),
            'content_length': len(firecrawl_response.get('content', '')),
            'chunks_processed': chunk_index,
            'milvus_inserts': {
                'successful': successful_milvus_inserts,
                'failed': failed_milvus_inserts,
                'total': chunk_index
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Crawl failed: {str(e)}'}), 500

def call_firecrawl_api(link):
    """Gọi API firecrawl để crawl nội dung từ link"""
    try:
        from flask import current_app
        
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

@user_bp.route('/crawls', methods=['GET'])
@require_roles('user', 'manager', 'admin')
@apply_rate_limit("30 per minute")
def get_crawls():
    """Lấy danh sách crawls của user"""
    user_id = int(get_jwt_identity())
    # Lấy user để biết role
    current_user = User.query.get(user_id)
    if not current_user:
        return jsonify({'error': 'User not found'}), 404
    user_role = current_user.role
    
    # Admin có thể xem tất cả crawls
    if user_role == 'admin':
        crawls = LinkCrawl.query.all()
    else:
        # User thường chỉ xem crawls của chính mình
        crawls = LinkCrawl.query.filter_by(user_id=user_id).all()
    
    return jsonify({
        'message': 'Danh sách crawls',
        'crawls': [crawl.to_dict() for crawl in crawls]
    })

@user_bp.route('/crawls/<int:crawl_id>', methods=['GET'])
@require_roles('user', 'manager', 'admin')
@apply_rate_limit("30 per minute")
def get_crawl_detail(crawl_id):
    """Lấy chi tiết một crawl cụ thể"""
    user_id = int(get_jwt_identity())
    # Lấy user để biết role
    current_user = User.query.get(user_id)
    if not current_user:
        return jsonify({'error': 'User not found'}), 404
    user_role = current_user.role
    
    crawl = LinkCrawl.query.get(crawl_id)
    if not crawl:
        return jsonify({'error': 'Crawl not found'}), 404
    
    # Kiểm tra quyền truy cập
    if user_role != 'admin' and crawl.user_id != user_id:
        return jsonify({'error': 'Access denied'}), 403
    
    return jsonify({
        'message': 'Chi tiết crawl',
        'crawl': crawl.to_dict()
    }) 

@user_bp.route('/documents/<int:document_id>/retry-milvus', methods=['POST'])
@require_roles('user', 'manager', 'admin')
@apply_rate_limit("5 per minute")
def retry_milvus_inserts(document_id):
    """Retry insert các chunks bị fail vào Milvus cho một document"""
    try:
        # Kiểm tra document tồn tại
        document = Document.query.get(document_id)
        if not document:
            return jsonify({'error': 'Document not found'}), 404
        
        # Kiểm tra quyền sở hữu
        current_user_id = int(get_jwt_identity())
        if document.user_id != current_user_id:
            return jsonify({'error': 'Access denied'}), 403
        
        # Thực hiện retry
        result = retry_failed_milvus_inserts(document_id)
        
        return jsonify({
            'message': 'Retry completed',
            'document_id': document_id,
            'retry_results': result
        })
        
    except Exception as e:
        return jsonify({'error': f'Retry failed: {str(e)}'}), 500

@user_bp.route('/search', methods=['POST'])
@require_roles('user', 'manager', 'admin')
@apply_rate_limit("20 per minute")
def search_documents():
    """Tìm kiếm documents bằng vector search"""
    user_id = int(get_jwt_identity())
    
    data = request.get_json()
    
    # Validate input
    if not data or 'query' not in data:
        return jsonify({'error': 'Query is required'}), 400
    
    query = data['query']
    top_k = data.get('top_k', 5)
    document_ids = data.get('document_ids', None)  # Filter theo document IDs
    
    try:
        vector_service = get_vector_service()
        
        # Thực hiện vector search
        search_results = vector_service.search_similar(
            query=query,
            top_k=top_k,
            document_ids=document_ids
        )
        
        # Lấy thông tin chi tiết của chunks từ database
        detailed_results = []
        for result in search_results:
            chunk = DocumentChunk.query.filter_by(milvus_id=result['id']).first()
            if chunk:
                document = Document.query.get(chunk.document_id)
                if document:
                    detailed_results.append({
                        'chunk_id': chunk.id,
                        'document_id': chunk.document_id,
                        'document_title': document.title,
                        'chunk_index': chunk.chunk_index,
                        'content': chunk.content,
                        'similarity_score': result['score'],
                        'source_path': document.source_path
                    })
        
        return jsonify({
            'message': 'Search completed successfully',
            'query': query,
            'total_results': len(detailed_results),
            'results': detailed_results
        })
        
    except Exception as e:
        return jsonify({'error': f'Search failed: {str(e)}'}), 500 

@user_bp.route('/documents', methods=['GET'])
@require_roles('user', 'manager', 'admin')
@apply_rate_limit("30 per minute")
def get_documents():
    """Lấy danh sách documents của user"""
    user_id = int(get_jwt_identity())
    # Lấy user để biết role
    current_user = User.query.get(user_id)
    if not current_user:
        return jsonify({'error': 'User not found'}), 404
    user_role = current_user.role
    
    # Admin có thể xem tất cả documents
    if user_role == 'admin':
        documents = Document.query.all()
    else:
        # User thường chỉ xem documents của chính mình
        documents = Document.query.filter_by(user_id=user_id).all()
    
    return jsonify({
        'message': 'Danh sách documents',
        'documents': [doc.to_dict() for doc in documents]
    })

@user_bp.route('/documents/<int:document_id>', methods=['GET'])
@require_roles('user', 'manager', 'admin')
@apply_rate_limit("30 per minute")
def get_document_detail(document_id):
    """Lấy chi tiết một document cụ thể"""
    user_id = int(get_jwt_identity())
    # Lấy user để biết role
    current_user = User.query.get(user_id)
    if not current_user:
        return jsonify({'error': 'User not found'}), 404
    user_role = current_user.role
    
    document = Document.query.get(document_id)
    if not document:
        return jsonify({'error': 'Document not found'}), 404
    
    # Kiểm tra quyền truy cập
    if user_role != 'admin' and document.user_id != user_id:
        return jsonify({'error': 'Access denied'}), 403
    
    # Lấy thông tin chunks
    chunks = DocumentChunk.query.filter_by(document_id=document_id).all()
    
    return jsonify({
        'message': 'Chi tiết document',
        'document': document.to_dict(),
        'chunks_count': len(chunks),
        'chunks': [chunk.to_dict() for chunk in chunks]
    })

@user_bp.route('/documents/<int:document_id>', methods=['DELETE'])
@require_roles('user', 'manager', 'admin')
@apply_rate_limit("10 per minute")
def delete_document(document_id):
    """Xóa document và tất cả chunks liên quan từ database và Milvus"""
    try:
        # Kiểm tra document tồn tại
        document = Document.query.get(document_id)
        if not document:
            return jsonify({'error': 'Document not found'}), 404
        
        # Kiểm tra quyền sở hữu
        current_user_id = int(get_jwt_identity())
        if document.user_id != current_user_id:
            return jsonify({'error': 'Access denied'}), 403
        
        # Lấy tất cả chunks của document
        chunks = DocumentChunk.query.filter_by(document_id=document_id).all()
        
        # Xóa từ Milvus trước
        vector_service = get_vector_service()
        milvus_deleted = 0
        milvus_failed = 0
        
        try:
            vector_service.delete_document_chunks(document_id)
            milvus_deleted = len(chunks)
            print(f"✅ Deleted all {len(chunks)} chunks from Milvus for document {document_id}")
        except Exception as e:
            milvus_failed = len(chunks)
            print(f"⚠️ Warning: Failed to delete chunks from Milvus: {e}")
        
        # Xóa chunks từ database
        DocumentChunk.query.filter_by(document_id=document_id).delete()
        
        # Xóa document từ database
        db.session.delete(document)
        db.session.commit()
        
        return jsonify({
            'message': 'Document deleted successfully',
            'document_id': document_id,
            'chunks_deleted': len(chunks),
            'milvus_deletion': {
                'successful': milvus_deleted,
                'failed': milvus_failed,
                'total': len(chunks)
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Delete failed: {str(e)}'}), 500 