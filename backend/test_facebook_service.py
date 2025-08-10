#!/usr/bin/env python3
"""
Test script for Facebook service
"""

import sys
import os
import json
from datetime import datetime

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(__file__))

from utils.facebook_service import FacebookService
from models import db, Conversation, Message, FacebookPage
from config import Config
from flask import Flask

def init_test_app():
    """Initialize Flask app for testing"""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = Config.SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    return app

def test_facebook_service():
    """Test Facebook service functionality"""
    
    app = init_test_app()
    
    with app.app_context():
        print("🧪 Testing Facebook Service...")
        
        # Initialize service
        fb_service = FacebookService()
        
        # Test 1: Get all active pages
        print("\n📋 Test 1: Get all active pages")
        pages = fb_service.get_all_active_pages()
        print(f"Active pages: {len(pages)}")
        for page in pages:
            print(f"  - {page['page_name']} (ID: {page['page_id']})")
        
        # Test 2: Get specific page info
        print("\n📋 Test 2: Get specific page info")
        if pages:
            page_id = pages[0]['page_id']
            page_info = fb_service.get_page_info(page_id)
            if page_info:
                print(f"Page info: {page_info['page_name']}")
            else:
                print("Page not found")
        
        # Test 3: Create conversation
        print("\n📋 Test 3: Create conversation")
        sender_id = "test_user_123"
        page_id = "test_page_456"
        conversation = fb_service.get_or_create_conversation(sender_id, page_id)
        if conversation:
            print(f"Conversation created/found: {conversation.id}")
            print(f"Thread ID: {conversation.thread_id}")
            print(f"Thread type: {conversation.thread_type}")
        else:
            print("Failed to create conversation")
        
        # Test 4: Save message to database
        print("\n📋 Test 4: Save message to database")
        if conversation:
            test_message = fb_service.save_message_to_db(
                conversation_id=conversation.id,
                sender_id=sender_id,
                content="Hello, this is a test message!",
                facebook_message_id="test_msg_123",
                message_type="text"
            )
            if test_message:
                print(f"Message saved: {test_message.id}")
                print(f"Content: {test_message.content}")
            else:
                print("Failed to save message")
        
        # Test 5: Process webhook message
        print("\n📋 Test 5: Process webhook message")
        webhook_data = {
            "object": "page",
            "entry": [
                {
                    "id": "test_page_456",
                    "time": int(datetime.now().timestamp()),
                    "messaging": [
                        {
                            "sender": {"id": "test_user_123"},
                            "recipient": {"id": "test_page_456"},
                            "timestamp": int(datetime.now().timestamp()),
                            "message": {
                                "mid": "test_webhook_msg_456",
                                "text": "Hello from webhook!"
                            }
                        }
                    ]
                }
            ]
        }
        
        result = fb_service.process_webhook_message(webhook_data)
        print(f"Webhook processing result: {result}")
        
        # Test 6: Verify webhook
        print("\n📋 Test 6: Verify webhook")
        verify_token = Config.FACEBOOK_VERIFY_TOKEN
        challenge = "test_challenge_123"
        
        result = fb_service.verify_webhook("subscribe", verify_token, challenge, verify_token)
        if result:
            print(f"Webhook verification successful: {result}")
        else:
            print("Webhook verification failed")
        
        # Test 7: Verify signature
        print("\n📋 Test 7: Verify signature")
        if hasattr(Config, 'FACEBOOK_APP_SECRET') and Config.FACEBOOK_APP_SECRET:
            body = "test_body"
            signature = "sha256=test_signature"
            result = fb_service.verify_signature(signature, body, Config.FACEBOOK_APP_SECRET)
            print(f"Signature verification result: {result}")
        else:
            print("Facebook app secret not configured")
        
        print("\n✅ Facebook service tests completed!")

def test_facebook_pages_crud():
    """Test Facebook pages CRUD operations"""
    
    app = init_test_app()
    
    with app.app_context():
        print("\n🧪 Testing Facebook Pages CRUD operations...")
        
        # Test 1: Create a new page
        print("\n📋 Test 1: Create a new page")
        new_page = FacebookPage(
            chatbot_id=1,
            page_id="test_page_crud_789",
            page_name="Test CRUD Page",
            page_access_token="test_access_token_789",
            status=True
        )
        
        db.session.add(new_page)
        db.session.commit()
        print(f"Created page: {new_page.page_id} (ID: {new_page.id})")
        
        # Test 2: Read page
        print("\n📋 Test 2: Read page")
        page = FacebookPage.query.filter_by(page_id="test_page_crud_789").first()
        if page:
            print(f"Found page: {page.page_name}")
            print(f"Status: {page.status}")
        else:
            print("Page not found")
        
        # Test 3: Update page
        print("\n📋 Test 3: Update page")
        if page:
            page.page_name = "Updated Test CRUD Page"
            page.status = False
            db.session.commit()
            print(f"Updated page: {page.page_name}")
            print(f"New status: {page.status}")
        
        # Test 4: Delete page (soft delete)
        print("\n📋 Test 4: Delete page (soft delete)")
        if page:
            page.status = False
            db.session.commit()
            print("Page soft deleted (status set to False)")
        
        # Test 5: Query active pages
        print("\n📋 Test 5: Query active pages")
        active_pages = FacebookPage.query.filter_by(status=True).all()
        print(f"Active pages: {len(active_pages)}")
        
        # Clean up test data
        print("\n🧹 Cleaning up test data...")
        if page:
            db.session.delete(page)
            db.session.commit()
            print("Test page deleted")
        
        print("✅ Facebook Pages CRUD tests completed!")

def test_conversation_messages():
    """Test conversation and messages functionality"""
    
    app = init_test_app()
    
    with app.app_context():
        print("\n🧪 Testing Conversation and Messages...")
        
        # Test 1: Create conversation
        print("\n📋 Test 1: Create conversation")
        conversation = Conversation(
            thread_id="test_thread_123",
            thread_type="facebook",
            title="Test Conversation"
        )
        db.session.add(conversation)
        db.session.commit()
        print(f"Created conversation: {conversation.id}")
        
        # Test 2: Add messages
        print("\n📋 Test 2: Add messages")
        messages_data = [
            {
                "sender_id": "user_123",
                "content": "Hello!",
                "facebook_message_id": "msg_1",
                "message_type": "text"
            },
            {
                "sender_id": "page_456",
                "content": "Hi there! How can I help you?",
                "facebook_message_id": "msg_2",
                "message_type": "text"
            },
            {
                "sender_id": "user_123",
                "content": "I have a question about your products.",
                "facebook_message_id": "msg_3",
                "message_type": "text"
            }
        ]
        
        for msg_data in messages_data:
            message = Message(
                conversation_id=conversation.id,
                sender_id=msg_data["sender_id"],
                content=msg_data["content"],
                facebook_message_id=msg_data["facebook_message_id"],
                message_type=msg_data["message_type"]
            )
            db.session.add(message)
        
        db.session.commit()
        print(f"Added {len(messages_data)} messages")
        
        # Test 3: Query messages
        print("\n📋 Test 3: Query messages")
        messages = Message.query.filter_by(conversation_id=conversation.id).order_by(Message.created_at.asc()).all()
        print(f"Total messages in conversation: {len(messages)}")
        
        for i, msg in enumerate(messages, 1):
            print(f"  {i}. [{msg.sender_id}] {msg.content}")
        
        # Test 4: Query by Facebook message ID
        print("\n📋 Test 4: Query by Facebook message ID")
        fb_message = Message.query.filter_by(facebook_message_id="msg_2").first()
        if fb_message:
            print(f"Found Facebook message: {fb_message.content}")
        else:
            print("Facebook message not found")
        
        # Clean up test data
        print("\n🧹 Cleaning up test data...")
        db.session.delete(conversation)  # This will cascade delete messages
        db.session.commit()
        print("Test conversation and messages deleted")
        
        print("✅ Conversation and Messages tests completed!")

if __name__ == "__main__":
    print("🚀 Starting Facebook Service Tests...")
    
    try:
        # Run tests
        test_facebook_service()
        test_facebook_pages_crud()
        test_conversation_messages()
        
        print("\n🎉 All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 