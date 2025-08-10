from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.permissions import require_roles
from utils.rate_limit import apply_rate_limit
from utils.groq_service import GroqChat
from utils.vector_service import get_vector_service
from models import DocumentChunk, Document
import json

content_bp = Blueprint('content', __name__)

@content_bp.route('/generate', methods=['POST'])
@jwt_required()
@require_roles('user', 'manager', 'admin')
@apply_rate_limit("10 per minute")
def generate_content():
    """
    Tạo nội dung dựa trên chủ đề sử dụng GroqChat
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Dữ liệu không được cung cấp'}), 400
        
        topic = data.get('topic')
        if not topic:
            return jsonify({'error': 'Chủ đề (topic) là bắt buộc'}), 400
        
        # Các tham số tùy chọn
        loai_bai_viet = data.get('loai_bai_viet', '')
        khach_hang_so_thich = data.get('khach_hang_so_thich', '')
        khach_hang_noi_so = data.get('khach_hang_noi_so', '')
        khach_hang_noi_dau = data.get('khach_hang_noi_dau', '')
        giong_dieu = data.get('giong_dieu', '')
        muc_tieu = data.get('muc_tieu', '')
        
        # Tìm kiếm tri thức liên quan trong vector database
        knowledge_context = search_knowledge(topic)
        
        # Tạo system prompt dựa trên các tham số và ngữ cảnh tri thức
        system_prompt = create_system_prompt(loai_bai_viet, khach_hang_so_thich, khach_hang_noi_so, khach_hang_noi_dau, giong_dieu, muc_tieu, knowledge_context)
        
        # Khởi tạo GroqChat
        groq_chat = GroqChat(
            model="llama-3.3-70b-versatile",
            max_tokens=2000,
            temperature=0.7
        )
        
        # Tạo user prompt
        user_prompt = f"Tạo nội dung về chủ đề: {topic}"
        
        # Gọi GroqChat
        response = groq_chat.chat(system_prompt, user_prompt)
        
        # Làm sạch response
        cleaned_content = response.clean()
        
        return jsonify({
            'success': True,
            'content': cleaned_content,
            'topic': topic,
            'loai_bai_viet': loai_bai_viet,
            'khach_hang_so_thich': khach_hang_so_thich,
            'khach_hang_noi_so': khach_hang_noi_so,
            'khach_hang_noi_dau': khach_hang_noi_dau,
            'giong_dieu': giong_dieu,
            'muc_tieu': muc_tieu,
            'knowledge_sources': [{'source': chunk['source'], 'score': chunk['similarity_score']} for chunk in knowledge_context] if knowledge_context else []
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Lỗi khi tạo nội dung',
            'message': str(e)
        }), 500

def search_knowledge(topic):
    """
    Tìm kiếm tri thức liên quan trong vector database
    """
    try:
        vector_service = get_vector_service()
        
        # Thực hiện vector search với topic
        search_results = vector_service.search_similar(
            query=topic,
            top_k=5,  # Lấy top 5 kết quả liên quan nhất
            document_ids=None
        )
        
        # Lấy nội dung chi tiết từ database
        knowledge_chunks = []
        for result in search_results:
            chunk = DocumentChunk.query.filter_by(milvus_id=result['id']).first()
            if chunk:
                document = Document.query.get(chunk.document_id)
                if document:
                    knowledge_chunks.append({
                        'content': chunk.content,
                        'source': document.title,
                        'similarity_score': result['score']
                    })
        
        return knowledge_chunks
        
    except Exception as e:
        print(f"Warning: Failed to search knowledge: {e}")
        return []

def create_system_prompt(loai_bai_viet, khach_hang_so_thich, khach_hang_noi_so, khach_hang_noi_dau, giong_dieu, muc_tieu, knowledge_context=None):
    """
    Tạo system prompt dựa trên các tham số và ngữ cảnh tri thức
    """
    
    # Tạo phần ngữ cảnh tri thức
    knowledge_section = ""
    if knowledge_context and len(knowledge_context) > 0:
        knowledge_section = "\nTRI THỨC THAM KHẢO:\n"
        for i, chunk in enumerate(knowledge_context, 1):
            knowledge_section += f"[Nguồn {i}: {chunk['source']}]\n{chunk['content'][:500]}{'...' if len(chunk['content']) > 500 else ''}\n\n"
        knowledge_section += "Hãy sử dụng tri thức tham khảo trên để làm phong phú nội dung, nhưng đừng copy nguyên văn. Hãy diễn giải và kết hợp một cách tự nhiên.\n"
    
    prompt = f"""
    Bạn là một chuyên gia tạo nội dung marketing chuyên nghiệp. Hãy tạo nội dung dựa trên thông tin sau:
    
    THÔNG TIN KHÁCH HÀNG:
    - Sở thích: {khach_hang_so_thich if khach_hang_so_thich else 'Chưa xác định'}
    - Nỗi sợ/Lo lắng: {khach_hang_noi_so if khach_hang_noi_so else 'Chưa xác định'}
    - Điểm đau/Vấn đề: {khach_hang_noi_dau if khach_hang_noi_dau else 'Chưa xác định'}
    
    YÊU CẦU NỘI DUNG:
    - Loại bài viết: {loai_bai_viet if loai_bai_viet else 'Bài viết thông tin'}
    - Giọng điệu: {giong_dieu if giong_dieu else 'Chuyên nghiệp và thân thiện'}
    - Mục tiêu: {muc_tieu if muc_tieu else 'Cung cấp giá trị và thu hút khách hàng'}
    {knowledge_section}
    HƯỚNG DẪN TẠO NỘI DUNG:
    1. Hiểu rõ đối tượng khách hàng dựa trên sở thích, nỗi sợ và điểm đau
    2. Sử dụng tri thức tham khảo (nếu có) để làm phong phú nội dung
    3. Tạo nội dung phù hợp với loại bài viết được yêu cầu
    4. Sử dụng giọng điệu phù hợp
    5. Hướng tới mục tiêu đã đặt ra
    6. Nội dung phải có giá trị, hữu ích và thu hút
    7. Cấu trúc rõ ràng, dễ đọc
    8. Không sử dụng markdown hoặc định dạng đặc biệt
    9. Chỉ trả về nội dung văn bản thuần túy
    10. Nội dung bằng tiếng Việt
    11. Chèn câu chuyện hoặc trải nghiệm cá nhân
    12. Dùng từ gần gũi, ít sáo rỗng
    13. Thêm chi tiết cụ thể, độc đáo
    14. Giảm bớt câu kêu gọi bán hàng, tập trung vào cảm xúc và hình ảnh cuộc sống
    
    Hãy tạo nội dung chất lượng cao, phù hợp với thông tin khách hàng và yêu cầu đã đưa ra.
    """
    
    return prompt.strip()

@content_bp.route('/generate/stream', methods=['POST'])
@jwt_required()
@require_roles('user', 'manager', 'admin')
@apply_rate_limit("5 per minute")
def generate_content_stream():
    """
    Tạo nội dung dưới dạng stream
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Dữ liệu không được cung cấp'}), 400
        
        topic = data.get('topic')
        if not topic:
            return jsonify({'error': 'Chủ đề (topic) là bắt buộc'}), 400
        
        # Các tham số tùy chọn
        loai_bai_viet = data.get('loai_bai_viet', '')
        khach_hang_so_thich = data.get('khach_hang_so_thich', '')
        khach_hang_noi_so = data.get('khach_hang_noi_so', '')
        khach_hang_noi_dau = data.get('khach_hang_noi_dau', '')
        giong_dieu = data.get('giong_dieu', '')
        muc_tieu = data.get('muc_tieu', '')
        
        # Tìm kiếm tri thức liên quan trong vector database
        knowledge_context = search_knowledge(topic)
        
        # Tạo system prompt
        system_prompt = create_system_prompt(loai_bai_viet, khach_hang_so_thich, khach_hang_noi_so, khach_hang_noi_dau, giong_dieu, muc_tieu, knowledge_context)
        
        # Khởi tạo GroqChat với stream=True
        groq_chat = GroqChat(
            model="llama-3.3-70b-versatile",
            max_tokens=2000,
            temperature=0.7,
            stream=True
        )
        
        # Tạo user prompt
        user_prompt = f"Tạo nội dung về chủ đề: {topic}"
        
        # Trả về response dưới dạng stream
        from flask import Response, stream_with_context
        
        def generate():
            try:
                for chunk in groq_chat.chat_stream(system_prompt, user_prompt):
                    yield f"data: {json.dumps({'chunk': chunk}, ensure_ascii=False)}\n\n"
                yield f"data: {json.dumps({'done': True}, ensure_ascii=False)}\n\n"
            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"
        
        return Response(
            stream_with_context(generate()),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Cache-Control'
            }
        )
        
    except Exception as e:
        return jsonify({
            'error': 'Lỗi khi tạo nội dung stream',
            'message': str(e)
        }), 500 