#!/usr/bin/env python3
"""
Migration script to add conversations and messages tables
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from models import db, Conversation, Message
from config import Config

def migrate_messages_tables():
    """Add conversations and messages tables to database"""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = Config.SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    
    with app.app_context():
        try:
            print("Creating conversations and messages tables...")
            db.create_all()
            print("✅ Migration completed successfully!")
            print("Tables created:")
            print("  - conversations")
            print("  - messages")
            
            # Test the tables
            print("\nTesting tables...")
            conv_count = Conversation.query.count()
            msg_count = Message.query.count()
            print(f"  - Conversations: {conv_count}")
            print(f"  - Messages: {msg_count}")
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            return False
    
    return True

if __name__ == "__main__":
    print("Starting messages tables migration...")
    success = migrate_messages_tables()
    if success:
        print("\n🎉 Migration completed successfully!")
    else:
        print("\n💥 Migration failed!")
        sys.exit(1) 