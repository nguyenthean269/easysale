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