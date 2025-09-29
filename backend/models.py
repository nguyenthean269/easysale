from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Tạo db instance riêng
db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(120), unique=True)
    full_name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    role = db.Column(db.String(20), nullable=False, default='user')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'phone': self.phone,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    documents = db.relationship('Document', backref='category')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class LinkCrawl(db.Model):
    __tablename__ = 'link_crawls'
    
    id = db.Column(db.Integer, primary_key=True)
    link = db.Column(db.String(500), nullable=False)  # URL string
    content = db.Column(db.Text, nullable=False)
    crawl_tool = db.Column(db.String(20), nullable=False)  # 'firecrawl' or 'watercrawl'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    started_at = db.Column(db.DateTime, nullable=False)
    done_at = db.Column(db.DateTime, nullable=False)
    
    # Relationship
    user = db.relationship('User', backref='link_crawls')
    
    def to_dict(self):
        return {
            'id': self.id,
            'link': self.link,
            'content': self.content,
            'crawl_tool': self.crawl_tool,
            'user_id': self.user_id,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'done_at': self.done_at.isoformat() if self.done_at else None
        }

class Document(db.Model):
    __tablename__ = 'documents'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    source_type = db.Column(db.String(50), nullable=False)  # 'web', 'file', etc.
    source_path = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', backref='documents')
    chunks = db.relationship('DocumentChunk', backref='document', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'category_id': self.category_id,
            'title': self.title,
            'source_type': self.source_type,
            'source_path': self.source_path,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class DocumentChunk(db.Model):
    __tablename__ = 'document_chunks'
    
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id'), nullable=False)
    chunk_index = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text, nullable=False)
    milvus_id = db.Column(db.String(100), nullable=True)  # ID của vector trong Milvus
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'document_id': self.document_id,
            'chunk_index': self.chunk_index,
            'content': self.content,
            'milvus_id': self.milvus_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Conversation(db.Model):
    __tablename__ = 'conversations'
    
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    thread_id = db.Column(db.String(255), nullable=False)  # Zalo thread ID
    thread_type = db.Column(db.String(50), nullable=False)  # 'user', 'group', etc.
    title = db.Column(db.String(255))  # Optional conversation title
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    messages = db.relationship('Message', backref='conversation', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'thread_id': self.thread_id,
            'thread_type': self.thread_type,
            'title': self.title,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Message(db.Model):
    __tablename__ = 'messages'
    
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    conversation_id = db.Column(db.BigInteger, db.ForeignKey('conversations.id'), nullable=False)
    sender_id = db.Column(db.String(128), nullable=False, default='user')
    content = db.Column(db.Text, nullable=False)
    message_type = db.Column(db.String(50), default='text')  # 'text', 'image', 'file', etc.
    zalo_message_id = db.Column(db.String(255))  # Original Zalo message ID
    facebook_message_id = db.Column(db.String(255))  # Original Facebook message ID
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'conversation_id': self.conversation_id,
            'sender_id': self.sender_id,
            'content': self.content,
            'message_type': self.message_type,
            'zalo_message_id': self.zalo_message_id,
            'facebook_message_id': self.facebook_message_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class FacebookPage(db.Model):
    __tablename__ = 'agent_facebook_pages'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    page_id = db.Column(db.String(255), nullable=True)
    page_name = db.Column(db.Text, nullable=True)
    page_access_token = db.Column(db.Text, nullable=True)
    status = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'page_id': self.page_id,
            'page_name': self.page_name,
            'page_access_token': self.page_access_token,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Post(db.Model):
    __tablename__ = 'posts'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.Text, nullable=False)
    staus = db.Column(db.Enum('draft', 'posted', name='post_status'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'staus': self.staus,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }