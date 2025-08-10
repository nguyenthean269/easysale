# testchatbot_async_override.py
from zlapi.models import Message
import nest_asyncio
nest_asyncio.apply()            # allow nested asyncio.run

import asyncio
from zlapi.Async import ZaloAPI
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from models import db, Conversation, Message as DBMessage
from config import Config

IMEI = "d5cf3050-b711-4cd9-91ec-77583339e091-a69b52f9d7f760edf3fd052bcda2542f"
COOKIES = {'_zlang': 'vn', 'zpsid': 'vim4.439120799.16.ZptykvR2ouW9iUUIciBBYEEnkRob-_gwflNoiPWgRRHElPxnbmmXs_x2ouW', 'zpw_sek': 'ntBP.439120799.a0.7N2aXOzIqWGG8VuUhbBI1FHmjs-jQF1ynG2ROierXM3_OgPrsogpOTmZlc_UR-ycybmwehEAhL7sKmBkt3hI10', 'app.event.zalo.me': '2554871109522422525'}

class AutoReplyOnceBot(ZaloAPI):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # tập lưu message IDs đã reply
        self._replied_msg_ids = set()
        
        # Initialize database connection
        self.init_database()

    def init_database(self):
        """Initialize database connection"""
        try:
            from flask import Flask
            app = Flask(__name__)
            app.config['SQLALCHEMY_DATABASE_URI'] = Config.SQLALCHEMY_DATABASE_URI
            app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
            db.init_app(app)
            
            with app.app_context():
                db.create_all()
                print("Database initialized successfully")
        except Exception as e:
            print(f"Database initialization error: {e}")

    def get_or_create_conversation(self, thread_id, thread_type):
        """Get existing conversation or create new one"""
        try:
            from flask import Flask
            app = Flask(__name__)
            app.config['SQLALCHEMY_DATABASE_URI'] = Config.SQLALCHEMY_DATABASE_URI
            app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
            db.init_app(app)
            
            with app.app_context():
                conversation = Conversation.query.filter_by(
                    thread_id=str(thread_id),
                    thread_type=thread_type.name
                ).first()
                
                if not conversation:
                    conversation = Conversation(
                        thread_id=str(thread_id),
                        thread_type=thread_type.name,
                        title=f"Conversation {thread_id}"
                    )
                    db.session.add(conversation)
                    db.session.commit()
                    print(f"Created new conversation: {conversation.id}")
                else:
                    print(f"Found existing conversation: {conversation.id}")
                
                return conversation
        except Exception as e:
            print(f"Error getting/creating conversation: {e}")
            return None

    def save_message_to_db(self, conversation_id, sender_id, content, zalo_message_id):
        """Save message to database"""
        try:
            from flask import Flask
            app = Flask(__name__)
            app.config['SQLALCHEMY_DATABASE_URI'] = Config.SQLALCHEMY_DATABASE_URI
            app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
            db.init_app(app)
            
            with app.app_context():
                # Check if message already exists
                existing_message = DBMessage.query.filter_by(
                    zalo_message_id=str(zalo_message_id)
                ).first()
                
                if existing_message:
                    print(f"Message {zalo_message_id} already exists in database")
                    return existing_message
                
                # Create new message
                message = DBMessage(
                    conversation_id=conversation_id,
                    sender_id=str(sender_id),
                    content=content,
                    message_type='text',
                    zalo_message_id=str(zalo_message_id)
                )
                
                db.session.add(message)
                db.session.commit()
                print(f"Saved message {zalo_message_id} to database with ID: {message.id}")
                return message
        except Exception as e:
            print(f"Error saving message to database: {e}")
            return None

    async def onMessage(self, mid, author_id, message, message_object, thread_id, thread_type):
        # 1) Bỏ qua tin nhắn do chính bot gửi
        if author_id == self.user_id:
            return

        # 2) Nếu đã reply rồi thì thôi
        if mid in self._replied_msg_ids:
            return
            
        # Log message đến
        print(f"[IN]  MessageID={mid} From={author_id} Thread={thread_type.name}({thread_id}): {message}")

        # 3) Lưu tin nhắn vào database
        try:
            # Get or create conversation
            conversation = self.get_or_create_conversation(thread_id, thread_type)
            if conversation:
                # Save message to database
                saved_message = self.save_message_to_db(
                    conversation_id=conversation.id,
                    sender_id=author_id,
                    content=message,
                    zalo_message_id=mid
                )
                if saved_message:
                    print(f"Message saved successfully to conversation {conversation.id}")
                else:
                    print("Failed to save message to database")
            else:
                print("Failed to get/create conversation")
        except Exception as e:
            print(f"Error processing message for database: {e}")

        # đánh dấu là đã reply
        self._replied_msg_ids.add(mid)

        # tạo Message object và gửi
        reply = Message(text="you are welcome")
        await self.send(reply, thread_id, thread_type)
        print(f"Replied once to message {mid} from {author_id}")
        print("------------------------------------")

async def mainapp():
    bot = AutoReplyOnceBot(
        phone="</>",           # or your phone if you want login via creds
        password="</>",        # otherwise zlapi will use the cookies/session
        imei=IMEI,
        cookies=COOKIES,      # note: `cookies`, _not_ `session_cookies`
        # type="websocket"      # or "requests" if websocket isn't working reliably
    )
    await bot.listen(thread=True)

if __name__ == "__main__":
    asyncio.run(mainapp())