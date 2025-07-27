import os
import uuid
import numpy as np
from sentence_transformers import SentenceTransformer
from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType, utility
from flask import current_app
import logging

logger = logging.getLogger(__name__)

class VectorService:
    def __init__(self):
        self.model = None
        self.collection = None
        self._init_embedding_model()
        self._init_milvus_connection()
        self._init_collection()
    
    def _init_embedding_model(self):
        """Khởi tạo embedding model"""
        try:
            model_name = current_app.config.get('EMBEDDING_MODEL', 'sentence-transformers/all-MiniLM-L6-v2')
            self.model = SentenceTransformer(model_name)
            logger.info(f"✅ Embedding model loaded: {model_name}")
        except Exception as e:
            logger.error(f"❌ Error loading embedding model: {e}")
            raise
    
    def _init_milvus_connection(self):
        """Kết nối đến Milvus server"""
        try:
            host = current_app.config.get('MILVUS_HOST', 'localhost')
            port = current_app.config.get('MILVUS_PORT', '19530')
            
            connections.connect("default", host=host, port=port)
            logger.info(f"✅ Connected to Milvus at {host}:{port}")
        except Exception as e:
            logger.error(f"❌ Error connecting to Milvus: {e}")
            raise
    
    def _init_collection(self):
        """Khởi tạo collection trong Milvus"""
        try:
            collection_name = current_app.config.get('MILVUS_COLLECTION_NAME', 'document_chunks')
            dimension = current_app.config.get('MILVUS_DIMENSION', 768)
            
            # Kiểm tra collection đã tồn tại chưa
            if utility.has_collection(collection_name):
                self.collection = Collection(collection_name)
                logger.info(f"✅ Collection '{collection_name}' already exists")
            else:
                # Tạo collection mới
                fields = [
                    FieldSchema(name="id", dtype=DataType.VARCHAR, is_primary=True, max_length=100),
                    FieldSchema(name="document_id", dtype=DataType.INT64),
                    FieldSchema(name="chunk_index", dtype=DataType.INT64),
                    FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=dimension)
                ]
                schema = CollectionSchema(fields, description="Document chunks with embeddings")
                self.collection = Collection(collection_name, schema)
                
                # Tạo index cho vector field
                index_params = {
                    "metric_type": "COSINE",
                    "index_type": "IVF_FLAT",
                    "params": {"nlist": 1024}
                }
                self.collection.create_index("embedding", index_params)
                logger.info(f"✅ Created collection '{collection_name}' with index")
            
            # Load collection
            self.collection.load()
            logger.info(f"✅ Collection '{collection_name}' loaded")
            
        except Exception as e:
            logger.error(f"❌ Error initializing collection: {e}")
            raise
    
    def create_embedding(self, text):
        """Tạo embedding vector từ text"""
        try:
            # Encode text thành vector
            embedding = self.model.encode(text)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"❌ Error creating embedding: {e}")
            raise
    
    def insert_chunk(self, document_id, chunk_index, content):
        """Thêm chunk vào Milvus collection"""
        try:
            logger.debug(f"Starting insert for doc_id={document_id}, chunk_index={chunk_index}")
            
            # Tạo embedding
            logger.debug("Creating embedding...")
            embedding = self.create_embedding(content)
            logger.debug(f"Embedding created, length: {len(embedding)}")
            
            # Kiểm tra dimension
            expected_dim = self.collection.schema.fields[-1].params['dim']
            if len(embedding) != expected_dim:
                raise ValueError(f"Embedding dimension {len(embedding)} != expected {expected_dim}")
            
            # Tạo unique ID
            chunk_id = str(uuid.uuid4())
            logger.debug(f"Generated ID: {chunk_id}")
            
            # Insert vào Milvus
            data = [
                [chunk_id],
                [document_id],
                [chunk_index],
                [embedding]
            ]
            
            logger.debug("Inserting into Milvus...")
            self.collection.insert(data)
            logger.debug("Insert completed")
            
            # Flush để đảm bảo data được lưu
            self.collection.flush()
            logger.debug("Flush completed")
            
            logger.info(f"✅ Inserted chunk {chunk_id} into Milvus")
            return chunk_id
            
        except Exception as e:
            logger.error(f"❌ Error inserting chunk: {e}")
            logger.error(f"Document ID: {document_id}, Chunk Index: {chunk_index}")
            logger.error(f"Content length: {len(content)}")
            raise
    
    def search_similar(self, query, top_k=5, document_ids=None):
        """Tìm kiếm chunks tương tự"""
        try:
            logger.debug(f"Searching for: {query}")
            logger.debug(f"Top k: {top_k}")
            logger.debug(f"Document IDs filter: {document_ids}")
            
            # Tạo embedding cho query
            query_embedding = self.create_embedding(query)
            
            # Tạo search parameters
            search_params = {
                "metric_type": "COSINE",
                "params": {"nprobe": 10}
            }
            
            # Tạo filter nếu có document_ids
            expr = None
            if document_ids:
                expr = f"document_id in {document_ids}"
            
            # Thực hiện search
            results = self.collection.search(
                data=[query_embedding],
                anns_field="embedding",
                param=search_params,
                limit=top_k,
                expr=expr,
                output_fields=["document_id", "chunk_index"]
            )
            
            # Format kết quả
            search_results = []
            for hits in results:
                for hit in hits:
                    search_results.append({
                        'id': hit.id,
                        'document_id': hit.entity.get('document_id'),
                        'chunk_index': hit.entity.get('chunk_index'),
                        'score': hit.score
                    })
            
            logger.debug(f"Search results: {len(search_results)}")
            return search_results
            
        except Exception as e:
            logger.error(f"❌ Error searching: {e}")
            raise
    
    def delete_chunk(self, chunk_id):
        """Xóa chunk khỏi Milvus"""
        try:
            expr = f'id == "{chunk_id}"'
            self.collection.delete(expr)
            logger.info(f"✅ Deleted chunk {chunk_id} from Milvus")
        except Exception as e:
            logger.error(f"❌ Error deleting chunk: {e}")
            raise
    
    def delete_document_chunks(self, document_id):
        """Xóa tất cả chunks của một document"""
        try:
            expr = f"document_id == {document_id}"
            self.collection.delete(expr)
            logger.info(f"✅ Deleted all chunks for document {document_id}")
        except Exception as e:
            logger.error(f"❌ Error deleting document chunks: {e}")
            raise

# Global instance
vector_service = None

def get_vector_service():
    """Lấy instance của VectorService"""
    global vector_service
    if vector_service is None:
        vector_service = VectorService()
    return vector_service 