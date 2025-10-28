from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, ZaloReceivedMessage, DocumentChunk, User
from utils.permissions import require_roles
from utils.rate_limit import apply_rate_limit
from utils.vector_service import VectorService
import logging
from datetime import datetime

zalo_chunks_bp = Blueprint('zalo_chunks', __name__)

@zalo_chunks_bp.route('/process-messages', methods=['POST'])
@jwt_required()
@require_roles(['admin', 'manager'])
@apply_rate_limit("10 per minute")
def process_zalo_messages():
    """
    Xử lý chunk nhóm 50 tin nhắn từ zalo_received_messages và thêm vào Milvus
    """
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        chunk_size = data.get('chunk_size', 50)  # Mặc định 50 tin nhắn mỗi chunk
        
        if not session_id:
            return jsonify({'error': 'session_id là bắt buộc'}), 400
        
        # Lấy user hiện tại
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        if not user:
            return jsonify({'error': 'User không tồn tại'}), 404
        
        # Lấy tin nhắn chưa được xử lý
        unprocessed_messages = ZaloReceivedMessage.query.filter(
            ZaloReceivedMessage.session_id == session_id,
            ZaloReceivedMessage.added_document_chunks.is_(None)  # Chưa được xử lý
        ).order_by(ZaloReceivedMessage.received_at.asc()).all()
        
        if not unprocessed_messages:
            return jsonify({
                'message': 'Không có tin nhắn nào cần xử lý',
                'processed_count': 0,
                'chunks_created': 0
            }), 200
        
        # Khởi tạo VectorService
        vector_service = VectorService()
        
        processed_count = 0
        chunks_created = 0
        
        # Xử lý từng nhóm tin nhắn
        for i in range(0, len(unprocessed_messages), chunk_size):
            chunk_messages = unprocessed_messages[i:i + chunk_size]
            
            # Tạo nội dung chunk từ các tin nhắn
            chunk_content = create_chunk_content(chunk_messages)
            
            if not chunk_content.strip():
                continue
            
            # Tạo document chunk mới
            document_chunk = DocumentChunk(
                document_id=None,  # Sẽ được cập nhật sau
                chunk_index=chunks_created,
                content=chunk_content,
                source_type='message',
                source_ref=chunk_messages[0].id,  # ID của tin nhắn đầu tiên trong chunk
                created_at=datetime.utcnow()
            )
            
            db.session.add(document_chunk)
            db.session.flush()  # Để lấy ID của document_chunk
            
            # Thêm vào Milvus
            try:
                milvus_id = vector_service.add_document_chunk(
                    content=chunk_content,
                    chunk_id=document_chunk.id,
                    source_type='message',
                    source_ref=document_chunk.source_ref
                )
                
                if milvus_id:
                    document_chunk.milvus_id = milvus_id
                    
                    # Đánh dấu các tin nhắn đã được xử lý
                    for message in chunk_messages:
                        message.added_document_chunks = True
                        processed_count += 1
                    
                    chunks_created += 1
                    logging.info(f"Created chunk {chunks_created} with {len(chunk_messages)} messages")
                else:
                    # Nếu thêm vào Milvus thất bại, xóa document_chunk
                    db.session.delete(document_chunk)
                    logging.error(f"Failed to add chunk to Milvus: {chunk_content[:100]}...")
                    
            except Exception as e:
                # Nếu có lỗi, xóa document_chunk và rollback
                db.session.delete(document_chunk)
                logging.error(f"Error adding chunk to Milvus: {str(e)}")
                continue
        
        # Commit tất cả thay đổi
        db.session.commit()
        
        return jsonify({
            'message': 'Xử lý tin nhắn thành công',
            'processed_count': processed_count,
            'chunks_created': chunks_created,
            'total_messages': len(unprocessed_messages)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error processing zalo messages: {str(e)}")
        return jsonify({'error': 'Lỗi server khi xử lý tin nhắn'}), 500

@zalo_chunks_bp.route('/stats', methods=['GET'])
@jwt_required()
@require_roles(['admin', 'manager'])
@apply_rate_limit("30 per minute")
def get_chunk_stats():
    """
    Lấy thống kê về tin nhắn đã xử lý và chưa xử lý
    """
    try:
        session_id = request.args.get('session_id')
        
        if not session_id:
            return jsonify({'error': 'session_id là bắt buộc'}), 400
        
        # Thống kê tin nhắn
        total_messages = ZaloReceivedMessage.query.filter(
            ZaloReceivedMessage.session_id == session_id
        ).count()
        
        processed_messages = ZaloReceivedMessage.query.filter(
            ZaloReceivedMessage.session_id == session_id,
            ZaloReceivedMessage.added_document_chunks == True
        ).count()
        
        unprocessed_messages = total_messages - processed_messages
        
        # Thống kê chunks
        total_chunks = DocumentChunk.query.filter(
            DocumentChunk.source_type == 'message',
            DocumentChunk.source_ref.in_(
                db.session.query(ZaloReceivedMessage.id).filter(
                    ZaloReceivedMessage.session_id == session_id
                )
            )
        ).count()
        
        # Thống kê tin nhắn đã push vào warehouse
        warehouse_processed_messages = ZaloReceivedMessage.query.filter(
            ZaloReceivedMessage.session_id == session_id,
            ZaloReceivedMessage.warehouse_id.isnot(None)
        ).count()
        
        return jsonify({
            'session_id': session_id,
            'total_messages': total_messages,
            'processed_messages': processed_messages,
            'unprocessed_messages': unprocessed_messages,
            'warehouse_processed_messages': warehouse_processed_messages,
            'total_chunks': total_chunks,
            'processing_percentage': round((processed_messages / total_messages * 100) if total_messages > 0 else 0, 2),
            'warehouse_processing_percentage': round((warehouse_processed_messages / total_messages * 100) if total_messages > 0 else 0, 2)
        }), 200
        
    except Exception as e:
        logging.error(f"Error getting chunk stats: {str(e)}")
        return jsonify({'error': 'Lỗi server khi lấy thống kê'}), 500

@zalo_chunks_bp.route('/sessions', methods=['GET'])
@jwt_required()
@require_roles(['admin', 'manager'])
@apply_rate_limit("30 per minute")
def get_zalo_sessions():
    """
    Lấy danh sách các session Zalo có tin nhắn
    """
    try:
        # Lấy danh sách session có tin nhắn
        sessions = db.session.query(
            ZaloReceivedMessage.session_id,
            db.func.count(ZaloReceivedMessage.id).label('total_messages'),
            db.func.count(db.case([(ZaloReceivedMessage.added_document_chunks == True, 1)])).label('processed_messages'),
            db.func.count(db.case([(ZaloReceivedMessage.warehouse_id.isnot(None), 1)])).label('warehouse_processed_messages')
        ).group_by(ZaloReceivedMessage.session_id).all()
        
        session_list = []
        for session in sessions:
            session_list.append({
                'session_id': session.session_id,
                'total_messages': session.total_messages,
                'processed_messages': session.processed_messages,
                'unprocessed_messages': session.total_messages - session.processed_messages,
                'warehouse_processed_messages': session.warehouse_processed_messages,
                'processing_percentage': round((session.processed_messages / session.total_messages * 100) if session.total_messages > 0 else 0, 2),
                'warehouse_processing_percentage': round((session.warehouse_processed_messages / session.total_messages * 100) if session.total_messages > 0 else 0, 2)
            })
        
        return jsonify({
            'sessions': session_list,
            'total_sessions': len(session_list)
        }), 200
        
    except Exception as e:
        logging.error(f"Error getting zalo sessions: {str(e)}")
        return jsonify({'error': 'Lỗi server khi lấy danh sách session'}), 500

def create_chunk_content(messages):
    """
    Tạo nội dung chunk từ danh sách tin nhắn
    """
    chunk_parts = []
    
    for message in messages:
        # Tạo timestamp
        timestamp = message.received_at.strftime('%Y-%m-%d %H:%M:%S') if message.received_at else 'Unknown time'
        
        # Tạo nội dung tin nhắn
        message_content = f"[{timestamp}] {message.sender_name or 'Unknown'}: {message.content}"
        
        # Thêm reply quote nếu có
        if message.reply_quote:
            message_content += f"\n  > Reply to: {message.reply_quote}"
        
        chunk_parts.append(message_content)
    
    return '\n\n'.join(chunk_parts)






