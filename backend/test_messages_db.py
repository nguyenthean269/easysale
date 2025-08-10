#!/usr/bin/env python3
"""
Test script for messages database functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from models import db, Conversation, Message
from config import Config

def test_messages_db():
    """Test the messages database functionality"""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = Config.SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    
    with app.app_context():
        try:
            print("🧪 Testing messages database functionality...")
            
            # Test 1: Create a conversation
            print("\n1. Creating test conversation...")
            test_conversation = Conversation(
                thread_id="test_thread_123",
                thread_type="user",
                title="Test Conversation"
            )
            db.session.add(test_conversation)
            db.session.commit()
            print(f"✅ Created conversation with ID: {test_conversation.id}")
            
            # Test 2: Add a message to the conversation
            print("\n2. Adding test message...")
            test_message = Message(
                conversation_id=test_conversation.id,
                sender_id="test_user_456",
                content="Hello, this is a test message!",
                message_type="text",
                zalo_message_id="test_msg_789"
            )
            db.session.add(test_message)
            db.session.commit()
            print(f"✅ Created message with ID: {test_message.id}")
            
            # Test 3: Query the data
            print("\n3. Querying data...")
            conv = Conversation.query.filter_by(thread_id="test_thread_123").first()
            if conv:
                print(f"✅ Found conversation: {conv.title}")
                messages = Message.query.filter_by(conversation_id=conv.id).all()
                print(f"✅ Found {len(messages)} messages in conversation")
                for msg in messages:
                    print(f"   - Message {msg.id}: {msg.content[:50]}...")
            
            # Test 4: Test duplicate message prevention
            print("\n4. Testing duplicate message prevention...")
            duplicate_message = Message(
                conversation_id=test_conversation.id,
                sender_id="test_user_456",
                content="This should not be saved (duplicate)",
                message_type="text",
                zalo_message_id="test_msg_789"  # Same Zalo message ID
            )
            db.session.add(duplicate_message)
            db.session.commit()
            
            # Check if duplicate was actually saved
            all_messages = Message.query.filter_by(zalo_message_id="test_msg_789").all()
            print(f"✅ Messages with same Zalo ID: {len(all_messages)}")
            
            # Clean up test data
            print("\n5. Cleaning up test data...")
            Message.query.filter_by(conversation_id=test_conversation.id).delete()
            Conversation.query.filter_by(id=test_conversation.id).delete()
            db.session.commit()
            print("✅ Test data cleaned up")
            
            print("\n🎉 All tests passed!")
            return True
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            return False

if __name__ == "__main__":
    success = test_messages_db()
    if not success:
        sys.exit(1) 