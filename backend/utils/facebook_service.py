import requests
import json
import hashlib
import hmac
import time
from typing import Dict, Any, Optional, List
import logging
from flask import current_app

# Add the backend directory to the Python path
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from models import db, Conversation, Message, FacebookPage
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FacebookService:
    def __init__(self):
        self.api_version = "v18.0"  # Facebook API version
        self.base_url = f"https://graph.facebook.com/{self.api_version}"
        
    def verify_webhook(self, mode: str, token: str, challenge: str, verify_token: str) -> Optional[str]:
        """
        Verify Facebook webhook
        """
        try:
            if mode == "subscribe" and token == verify_token:
                logger.info("Webhook verified successfully")
                return challenge
            else:
                logger.error("Webhook verification failed")
                return None
        except Exception as e:
            logger.error(f"Error verifying webhook: {e}")
            return None
    
    def verify_signature(self, signature: str, body: str, app_secret: str) -> bool:
        """
        Verify webhook signature for security
        """
        try:
            expected_signature = "sha256=" + hmac.new(
                app_secret.encode('utf-8'),
                body.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(signature, expected_signature)
        except Exception as e:
            logger.error(f"Error verifying signature: {e}")
            return False
    
    def get_page_access_token(self, page_id: str) -> Optional[str]:
        """
        Get page access token from database
        """
        try:
            page = FacebookPage.query.filter_by(
                page_id=page_id,
                status=True
            ).first()
            
            if page and page.page_access_token:
                return page.page_access_token
            else:
                logger.error(f"No active page found for page_id: {page_id}")
                return None
        except Exception as e:
            logger.error(f"Error getting page access token: {e}")
            return None
    
    def get_or_create_conversation(self, sender_id: str, page_id: str) -> Optional[Conversation]:
        """
        Get existing conversation or create new one for Facebook
        """
        try:
            # Create a unique thread_id combining sender_id and page_id
            thread_id = f"fb_{page_id}_{sender_id}"
            
            conversation = Conversation.query.filter_by(
                thread_id=thread_id,
                thread_type='facebook'
            ).first()
            
            if not conversation:
                conversation = Conversation(
                    thread_id=thread_id,
                    thread_type='facebook',
                    title=f"Facebook Conversation - {sender_id}"
                )
                db.session.add(conversation)
                db.session.commit()
                logger.info(f"Created new Facebook conversation: {conversation.id}")
            else:
                logger.info(f"Found existing Facebook conversation: {conversation.id}")
            
            return conversation
        except Exception as e:
            logger.error(f"Error getting/creating conversation: {e}")
            return None
    
    def save_message_to_db(self, conversation_id: int, sender_id: str, content: str, 
                          facebook_message_id: str, message_type: str = 'text') -> Optional[Message]:
        """
        Save Facebook message to database
        """
        try:
            # Check if message already exists
            existing_message = Message.query.filter_by(
                facebook_message_id=facebook_message_id
            ).first()
            
            if existing_message:
                logger.info(f"Message {facebook_message_id} already exists in database")
                return existing_message
            
            # Create new message
            message = Message(
                conversation_id=conversation_id,
                sender_id=sender_id,
                content=content,
                message_type=message_type,
                facebook_message_id=facebook_message_id
            )
            
            db.session.add(message)
            db.session.commit()
            logger.info(f"Saved Facebook message {facebook_message_id} to database with ID: {message.id}")
            return message
        except Exception as e:
            logger.error(f"Error saving Facebook message to database: {e}")
            return None
    
    def process_webhook_message(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process incoming webhook message from Facebook
        """
        try:
            result = {
                'success': False,
                'message': '',
                'processed_messages': 0
            }
            
            if 'entry' not in data:
                result['message'] = 'No entry data found'
                return result
            
            processed_count = 0
            
            for entry in data['entry']:
                if 'messaging' in entry:
                    for messaging_event in entry['messaging']:
                        try:
                            # Extract message data
                            sender_id = messaging_event.get('sender', {}).get('id')
                            page_id = messaging_event.get('recipient', {}).get('id')
                            
                            if not sender_id or not page_id:
                                logger.warning("Missing sender_id or page_id in messaging event")
                                continue
                            
                            # Handle different types of messages
                            if 'message' in messaging_event:
                                message_data = messaging_event['message']
                                message_id = message_data.get('mid')
                                text = message_data.get('text', '')
                                
                                if text and message_id:
                                    # Get or create conversation
                                    conversation = self.get_or_create_conversation(sender_id, page_id)
                                    if conversation:
                                        # Save message to database
                                        saved_message = self.save_message_to_db(
                                            conversation_id=conversation.id,
                                            sender_id=sender_id,
                                            content=text,
                                            facebook_message_id=message_id,
                                            message_type='text'
                                        )
                                        if saved_message:
                                            processed_count += 1
                                            logger.info(f"Processed incoming message from {sender_id}: {text}")
                                        else:
                                            logger.error(f"Failed to save message from {sender_id}")
                                    else:
                                        logger.error(f"Failed to get/create conversation for {sender_id}")
                            
                            elif 'postback' in messaging_event:
                                # Handle postback events
                                postback_data = messaging_event['postback']
                                payload = postback_data.get('payload', '')
                                
                                if payload:
                                    conversation = self.get_or_create_conversation(sender_id, page_id)
                                    if conversation:
                                        saved_message = self.save_message_to_db(
                                            conversation_id=conversation.id,
                                            sender_id=sender_id,
                                            content=f"[POSTBACK] {payload}",
                                            facebook_message_id=f"postback_{int(time.time())}",
                                            message_type='postback'
                                        )
                                        if saved_message:
                                            processed_count += 1
                                            logger.info(f"Processed postback from {sender_id}: {payload}")
                            
                        except Exception as e:
                            logger.error(f"Error processing individual messaging event: {e}")
                            continue
            
            result['success'] = True
            result['processed_messages'] = processed_count
            result['message'] = f"Successfully processed {processed_count} messages"
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing webhook message: {e}")
            return {
                'success': False,
                'message': f'Error processing webhook: {str(e)}',
                'processed_messages': 0
            }
    
    def send_message(self, page_id: str, recipient_id: str, message_text: str, 
                    conversation_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Send message via Facebook Messenger API
        """
        try:
            # Get page access token
            page_access_token = self.get_page_access_token(page_id)
            if not page_access_token:
                return {
                    'success': False,
                    'message': 'No valid page access token found',
                    'facebook_message_id': None
                }
            
            # Prepare message data
            message_data = {
                'recipient': {'id': recipient_id},
                'message': {'text': message_text}
            }
            
            # Send message to Facebook
            url = f"{self.base_url}/{page_id}/messages"
            params = {'access_token': page_access_token}
            
            response = requests.post(url, json=message_data, params=params)
            response_data = response.json()
            
            if response.status_code == 200 and 'message_id' in response_data:
                facebook_message_id = response_data['message_id']
                
                # Save message to database if conversation_id is provided
                if conversation_id:
                    saved_message = self.save_message_to_db(
                        conversation_id=conversation_id,
                        sender_id=page_id,  # Bot is the sender
                        content=message_text,
                        facebook_message_id=facebook_message_id,
                        message_type='text'
                    )
                    if saved_message:
                        logger.info(f"Saved outgoing message to database: {saved_message.id}")
                
                logger.info(f"Message sent successfully to {recipient_id}: {message_text}")
                return {
                    'success': True,
                    'message': 'Message sent successfully',
                    'facebook_message_id': facebook_message_id
                }
            else:
                error_msg = response_data.get('error', {}).get('message', 'Unknown error')
                logger.error(f"Failed to send message: {error_msg}")
                return {
                    'success': False,
                    'message': f'Failed to send message: {error_msg}',
                    'facebook_message_id': None
                }
                
        except Exception as e:
            logger.error(f"Error sending Facebook message: {e}")
            return {
                'success': False,
                'message': f'Error sending message: {str(e)}',
                'facebook_message_id': None
            }
    
    def send_typing_indicator(self, page_id: str, recipient_id: str, typing: bool = True) -> Dict[str, Any]:
        """
        Send typing indicator to show bot is typing
        """
        try:
            page_access_token = self.get_page_access_token(page_id)
            if not page_access_token:
                return {
                    'success': False,
                    'message': 'No valid page access token found'
                }
            
            action = 'typing_on' if typing else 'typing_off'
            message_data = {
                'recipient': {'id': recipient_id},
                'sender_action': action
            }
            
            url = f"{self.base_url}/{page_id}/messages"
            params = {'access_token': page_access_token}
            
            response = requests.post(url, json=message_data, params=params)
            
            if response.status_code == 200:
                logger.info(f"Typing indicator sent successfully to {recipient_id}")
                return {
                    'success': True,
                    'message': 'Typing indicator sent successfully'
                }
            else:
                error_msg = response.json().get('error', {}).get('message', 'Unknown error')
                logger.error(f"Failed to send typing indicator: {error_msg}")
                return {
                    'success': False,
                    'message': f'Failed to send typing indicator: {error_msg}'
                }
                
        except Exception as e:
            logger.error(f"Error sending typing indicator: {e}")
            return {
                'success': False,
                'message': f'Error sending typing indicator: {str(e)}'
            }
    
    def get_page_info(self, page_id: str) -> Optional[Dict[str, Any]]:
        """
        Get Facebook page information
        """
        try:
            page = FacebookPage.query.filter_by(
                page_id=page_id,
                status=True
            ).first()
            
            if page:
                return page.to_dict()
            else:
                logger.error(f"No active page found for page_id: {page_id}")
                return None
        except Exception as e:
            logger.error(f"Error getting page info: {e}")
            return None
    
    def get_all_active_pages(self) -> List[Dict[str, Any]]:
        """
        Get all active Facebook pages
        """
        try:
            pages = FacebookPage.query.filter_by(status=True).all()
            return [page.to_dict() for page in pages]
        except Exception as e:
            logger.error(f"Error getting active pages: {e}")
            return [] 