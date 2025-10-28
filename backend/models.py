from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import Enum, Index

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
    role = db.Column(db.Enum('admin', 'user', 'manager', name='user_role'), nullable=False, default='user')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_username', 'username'),
        Index('idx_email', 'email'),
        Index('idx_role', 'role'),
    )

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
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(1024), nullable=False)
    parents = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', backref='categories')
    documents = db.relationship('Document', backref='category_obj')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'parents': self.parents,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class LinkCrawl(db.Model):
    __tablename__ = 'link_crawls'
    
    id = db.Column(db.Integer, primary_key=True)
    schedule_id = db.Column(db.Integer, nullable=True)
    link = db.Column(db.String(500), nullable=False, unique=True)
    raw = db.Column(db.Text, nullable=True)
    content = db.Column(db.Text, nullable=False)
    crawl_tool = db.Column(db.Enum('firecrawl', 'watercrawl', 'local', name='crawl_tool_enum'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    started_at = db.Column(db.DateTime, nullable=False)
    done_at = db.Column(db.DateTime, nullable=False)
    
    # Relationship
    user = db.relationship('User', backref='link_crawls')
    
    def to_dict(self):
        return {
            'id': self.id,
            'schedule_id': self.schedule_id,
            'link': self.link,
            'raw': self.raw,
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
    source_type = db.Column(db.Enum('pdf', 'docx', 'web', 'text', name='source_type_enum'), nullable=False)
    source_path = db.Column(db.Text, nullable=True)
    created_by = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = db.Column(db.Enum('active', 'inactive', 'pending', name='document_status'), default='active')
    description = db.Column(db.Text, nullable=True)
    
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
            'created_by': self.created_by,
            'status': self.status,
            'description': self.description,
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
    source_type = db.Column(db.Enum('document', 'message', 'post', name='chunk_source_type'), default='document')
    source_ref = db.Column(db.BigInteger, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'document_id': self.document_id,
            'chunk_index': self.chunk_index,
            'content': self.content,
            'milvus_id': self.milvus_id,
            'source_type': self.source_type,
            'source_ref': self.source_ref,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Conversation(db.Model):
    __tablename__ = 'conversations'
    
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    agent_id = db.Column(db.Integer, nullable=True)
    created_by = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    source = db.Column(db.Enum('facebook_pages', 'zalo_personal', name='conversation_source'), nullable=True)
    chatbot_id = db.Column(db.Integer, nullable=True)
    conv_llm_flow_id = db.Column(db.String(255), nullable=True)
    sender_id = db.Column(db.String(255), nullable=True)
    chatbot_zalo_personal_id = db.Column(db.BigInteger, nullable=True)
    
    # Relationship
    messages = db.relationship('Message', backref='conversation', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'agent_id': self.agent_id,
            'created_by': self.created_by,
            'source': self.source,
            'chatbot_id': self.chatbot_id,
            'conv_llm_flow_id': self.conv_llm_flow_id,
            'sender_id': self.sender_id,
            'chatbot_zalo_personal_id': self.chatbot_zalo_personal_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Message(db.Model):
    __tablename__ = 'messages'
    
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    conversation_id = db.Column(db.BigInteger, db.ForeignKey('conversations.id'), nullable=False)
    sender_id = db.Column(db.String(128), nullable=False, default='user')
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'conversation_id': self.conversation_id,
            'sender_id': self.sender_id,
            'content': self.content,
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

# New models based on the updated schema

class AgentZaloPersonal(db.Model):
    __tablename__ = 'agent_zalo_personal'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    imei = db.Column(db.String(1000), nullable=True)
    cookies = db.Column(db.Text, nullable=True)
    phone_number = db.Column(db.String(20), nullable=True)
    username = db.Column(db.String(150), nullable=True)
    status = db.Column(db.Boolean, default=False)
    chatbot_id = db.Column(db.Integer, nullable=True)
    qr_code = db.Column(db.Text, nullable=True)
    login_status = db.Column(db.String(150), nullable=True)
    created_at = db.Column(db.DateTime(6), default=datetime.utcnow)
    updated_at = db.Column(db.DateTime(6), default=datetime.utcnow, onupdate=datetime.utcnow)
    avatar = db.Column(db.String(255), nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'imei': self.imei,
            'cookies': self.cookies,
            'phone_number': self.phone_number,
            'username': self.username,
            'status': self.status,
            'chatbot_id': self.chatbot_id,
            'qr_code': self.qr_code,
            'login_status': self.login_status,
            'avatar': self.avatar,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class CrawlLog(db.Model):
    __tablename__ = 'crawl_logs'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    schedule_id = db.Column(db.Integer, nullable=False)
    url = db.Column(db.String(4096), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    file_size = db.Column(db.Integer, default=0)
    error_message = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_schedule_id', 'schedule_id'),
        Index('idx_created_at', 'created_at'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'schedule_id': self.schedule_id,
            'url': self.url,
            'status': self.status,
            'file_size': self.file_size,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class LinkCrawlsSchedule(db.Model):
    __tablename__ = 'link_crawls_schedule'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    list_listening_url = db.Column(db.String(4096), nullable=False)
    frequency = db.Column(db.Integer, nullable=False)
    frequency_unit = db.Column(db.Enum('PHUT', 'GIO', 'NGAY', name='frequency_unit_enum'), nullable=False)
    status = db.Column(db.Enum('active', 'inactive', name='schedule_status'), nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'list_listening_url': self.list_listening_url,
            'frequency': self.frequency,
            'frequency_unit': self.frequency_unit,
            'status': self.status
        }

class ZaloConfig(db.Model):
    __tablename__ = 'zalo_configs'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    imei = db.Column(db.String(255), nullable=False)
    cookies = db.Column(db.Text, nullable=False)
    is_default = db.Column(db.Boolean, nullable=True)
    created_at = db.Column(db.DateTime, nullable=True)
    updated_at = db.Column(db.DateTime, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'imei': self.imei,
            'cookies': self.cookies,
            'is_default': self.is_default,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class ZaloSession(db.Model):
    __tablename__ = 'zalo_sessions'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    imei = db.Column(db.String(255), nullable=False)
    cookies = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, nullable=True)
    
    # Relationships
    contacts = db.relationship('ZaloContact', backref='session', cascade='all, delete-orphan')
    messages = db.relationship('ZaloMessage', backref='session', cascade='all, delete-orphan')
    received_messages = db.relationship('ZaloReceivedMessage', backref='session', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'imei': self.imei,
            'cookies': self.cookies,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class ZaloContact(db.Model):
    __tablename__ = 'zalo_contacts'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String(255), nullable=False, unique=True)
    name = db.Column(db.String(255), nullable=False)
    thread_type = db.Column(db.Enum('USER', 'GROUP', name='thread_type_enum'), nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey('zalo_sessions.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'thread_type': self.thread_type,
            'session_id': self.session_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class ZaloListenerConfig(db.Model):
    __tablename__ = 'zalo_listener_configs'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    config_id = db.Column(db.Integer, db.ForeignKey('zalo_configs.id'), nullable=False)
    status = db.Column(db.Enum('ACTIVE', 'INACTIVE', 'ERROR', name='listener_status'), nullable=True)
    is_enabled = db.Column(db.Boolean, nullable=True)
    listen_friends = db.Column(db.Boolean, nullable=True)
    listen_groups = db.Column(db.Boolean, nullable=True)
    last_error = db.Column(db.Text, nullable=True)
    last_activity = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, nullable=True)
    updated_at = db.Column(db.DateTime, nullable=True)
    
    # Relationship
    config = db.relationship('ZaloConfig', backref='listener_configs')
    
    def to_dict(self):
        return {
            'id': self.id,
            'config_id': self.config_id,
            'status': self.status,
            'is_enabled': self.is_enabled,
            'listen_friends': self.listen_friends,
            'listen_groups': self.listen_groups,
            'last_error': self.last_error,
            'last_activity': self.last_activity.isoformat() if self.last_activity else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class ZaloMessage(db.Model):
    __tablename__ = 'zalo_messages'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    session_id = db.Column(db.Integer, db.ForeignKey('zalo_sessions.id'), nullable=False)
    recipient_id = db.Column(db.String(255), nullable=False)
    recipient_name = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    media_url = db.Column(db.String(500), nullable=True)
    media_type = db.Column(db.String(50), nullable=True)
    status = db.Column(db.String(50), nullable=True)
    sent_at = db.Column(db.DateTime, nullable=True)
    response_data = db.Column(db.Text, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'recipient_id': self.recipient_id,
            'recipient_name': self.recipient_name,
            'content': self.content,
            'media_url': self.media_url,
            'media_type': self.media_type,
            'status': self.status,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'response_data': self.response_data
        }

class ZaloReceivedMessage(db.Model):
    __tablename__ = 'zalo_received_messages'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    session_id = db.Column(db.Integer, db.ForeignKey('zalo_sessions.id'), nullable=False)
    config_id = db.Column(db.Integer, db.ForeignKey('zalo_configs.id'), nullable=True)
    sender_id = db.Column(db.String(255), nullable=True)
    sender_name = db.Column(db.String(255), nullable=True)
    content = db.Column(db.Text, nullable=False)
    thread_id = db.Column(db.String(255), nullable=True)
    thread_type = db.Column(db.String(50), nullable=True)
    received_at = db.Column(db.DateTime, nullable=True)
    status_push_kafka = db.Column(db.Integer, default=0)
    warehouse_id = db.Column(db.BigInteger, nullable=True)  # ID của apartment trong warehouse database
    reply_quote = db.Column(db.Text, nullable=True)
    content_hash = db.Column(db.String(40), nullable=True)  # Generated column - SHA hash of content
    added_document_chunks = db.Column(db.Boolean, nullable=True)  # New field
    
    # Relationships
    config = db.relationship('ZaloConfig', backref='received_messages')
    
    # Note: content_hash is a generated column in the database
    # It will be automatically calculated by MySQL based on the content field
    
    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'config_id': self.config_id,
            'sender_id': self.sender_id,
            'sender_name': self.sender_name,
            'content': self.content,
            'thread_id': self.thread_id,
            'thread_type': self.thread_type,
            'received_at': self.received_at.isoformat() if self.received_at else None,
            'status_push_kafka': self.status_push_kafka,
            'warehouse_id': self.warehouse_id,
            'reply_quote': self.reply_quote,
            'content_hash': self.content_hash,
            'added_document_chunks': self.added_document_chunks
        }