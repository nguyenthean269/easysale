# Messages Database Guide

## Overview

This guide explains how the Zalo bot now saves incoming messages to the database using the new `conversations` and `messages` tables.

## Database Schema

### Conversations Table
```sql
CREATE TABLE conversations (
  id bigint unsigned NOT NULL AUTO_INCREMENT,
  thread_id varchar(255) NOT NULL,
  thread_type varchar(50) NOT NULL,
  title varchar(255) DEFAULT NULL,
  created_at timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY thread_id (thread_id),
  KEY thread_type (thread_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
```

### Messages Table
```sql
CREATE TABLE messages (
  id bigint unsigned NOT NULL AUTO_INCREMENT,
  conversation_id bigint unsigned NOT NULL,
  sender_id varchar(128) NOT NULL DEFAULT 'user',
  content text NOT NULL,
  message_type varchar(50) DEFAULT 'text',
  zalo_message_id varchar(255) DEFAULT NULL,
  created_at timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY conversation_id (conversation_id),
  KEY sender_id (sender_id),
  KEY zalo_message_id (zalo_message_id),
  CONSTRAINT messages_ibfk_1 FOREIGN KEY (conversation_id) REFERENCES conversations (id)
) ENGINE=InnoDB AUTO_INCREMENT=1223 DEFAULT CHARSET=utf8mb3;
```

## Features

### 1. Automatic Conversation Management
- Creates new conversations automatically when receiving messages from new threads
- Reuses existing conversations for ongoing chats
- Stores thread ID and thread type for easy identification

### 2. Message Storage
- Saves all incoming messages with sender information
- Prevents duplicate messages using Zalo message ID
- Supports different message types (text, image, file, etc.)
- Maintains conversation history

### 3. Database Integration
- Uses SQLAlchemy ORM for database operations
- Proper error handling and logging
- Transaction management for data consistency

## Usage

### Running the Migration
```bash
cd backend
python migrate_messages.py
```

### Testing the Database
```bash
cd backend
python test_messages_db.py
```

### Running the Zalo Bot
```bash
cd backend
python utils/zalo_service.py
```

## Code Structure

### Models (`models.py`)
- `Conversation`: Represents a chat conversation
- `Message`: Represents individual messages within conversations

### Zalo Service (`utils/zalo_service.py`)
- `AutoReplyOnceBot`: Enhanced bot class with database integration
- `get_or_create_conversation()`: Manages conversation creation/retrieval
- `save_message_to_db()`: Saves messages to database
- `onMessage()`: Enhanced message handler with database operations

## Database Operations

### Creating a Conversation
```python
conversation = Conversation(
    thread_id="zalo_thread_123",
    thread_type="user",
    title="Chat with User"
)
db.session.add(conversation)
db.session.commit()
```

### Saving a Message
```python
message = Message(
    conversation_id=conversation.id,
    sender_id="user_456",
    content="Hello, how can I help you?",
    message_type="text",
    zalo_message_id="zalo_msg_789"
)
db.session.add(message)
db.session.commit()
```

### Querying Messages
```python
# Get all messages in a conversation
messages = Message.query.filter_by(conversation_id=conversation.id).all()

# Get conversation by thread ID
conversation = Conversation.query.filter_by(thread_id="zalo_thread_123").first()

# Get messages by sender
user_messages = Message.query.filter_by(sender_id="user_456").all()
```

## Error Handling

The system includes comprehensive error handling:
- Database connection errors
- Duplicate message prevention
- Transaction rollback on failures
- Detailed logging for debugging

## Logging

The bot provides detailed logging for:
- Database initialization
- Conversation creation/retrieval
- Message saving operations
- Error conditions

## Future Enhancements

Potential improvements:
1. Message search functionality
2. Conversation analytics
3. Message sentiment analysis
4. Integration with AI response generation
5. Message export capabilities
6. Real-time message notifications

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Check database configuration in `config.py`
   - Ensure database server is running
   - Verify database credentials

2. **Migration Failed**
   - Run migration script with proper permissions
   - Check for existing table conflicts
   - Review database logs

3. **Messages Not Saving**
   - Check database connection in bot initialization
   - Verify table structure matches schema
   - Review error logs for specific issues

### Debug Commands

```bash
# Check database tables
mysql -u username -p easysale_db -e "SHOW TABLES;"

# Check conversation data
mysql -u username -p easysale_db -e "SELECT * FROM conversations LIMIT 5;"

# Check message data
mysql -u username -p easysale_db -e "SELECT * FROM messages LIMIT 5;"
``` 