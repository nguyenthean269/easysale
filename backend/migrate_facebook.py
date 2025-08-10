#!/usr/bin/env python3
"""
Migration script to add Facebook integration tables
"""

import sys
import os
from sqlalchemy import create_engine, text

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(__file__))

from config import Config

def migrate_facebook_tables():
    """Migrate Facebook-related tables"""
    
    # Create database engine
    engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
    
    try:
        with engine.connect() as connection:
            print("🔄 Starting Facebook tables migration...")
            
            # 1. Create agent_facebook_pages table
            print("📋 Creating agent_facebook_pages table...")
            create_facebook_pages_table = """
            CREATE TABLE IF NOT EXISTS `agent_facebook_pages` (
              `id` int NOT NULL AUTO_INCREMENT,
              `chatbot_id` int DEFAULT NULL,
              `page_id` varchar(255) DEFAULT NULL,
              `page_name` text,
              `page_access_token` text,
              `status` tinyint(1) DEFAULT '1',
              `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
              `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
              PRIMARY KEY (`id`),
              KEY `idx_page_id` (`page_id`),
              KEY `idx_status` (`status`)
            ) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb3
            """
            
            connection.execute(text(create_facebook_pages_table))
            print("✅ agent_facebook_pages table created successfully")
            
            # 2. Add facebook_message_id column to messages table if it doesn't exist
            print("📝 Adding facebook_message_id column to messages table...")
            
            # Check if column exists
            check_column_query = """
            SELECT COUNT(*) as count 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'messages' 
            AND COLUMN_NAME = 'facebook_message_id'
            """
            
            result = connection.execute(text(check_column_query))
            column_exists = result.fetchone()[0] > 0
            
            if not column_exists:
                add_facebook_message_id = """
                ALTER TABLE `messages` 
                ADD COLUMN `facebook_message_id` varchar(255) DEFAULT NULL AFTER `zalo_message_id`,
                ADD KEY `idx_facebook_message_id` (`facebook_message_id`)
                """
                
                connection.execute(text(add_facebook_message_id))
                print("✅ facebook_message_id column added to messages table")
            else:
                print("ℹ️  facebook_message_id column already exists in messages table")
            
            # 3. Add some sample data to agent_facebook_pages table
            print("📊 Adding sample data to agent_facebook_pages table...")
            
            # Check if sample data already exists
            check_sample_data = "SELECT COUNT(*) as count FROM agent_facebook_pages"
            result = connection.execute(text(check_sample_data))
            existing_count = result.fetchone()[0]
            
            if existing_count == 0:
                insert_sample_data = """
                INSERT INTO `agent_facebook_pages` 
                (`chatbot_id`, `page_id`, `page_name`, `page_access_token`, `status`) 
                VALUES 
                (1, '123456789012345', 'Sample Facebook Page', 'your-page-access-token-here', 1)
                """
                
                connection.execute(text(insert_sample_data))
                print("✅ Sample data added to agent_facebook_pages table")
            else:
                print(f"ℹ️  Sample data already exists ({existing_count} records)")
            
            # Commit all changes
            connection.commit()
            
            print("🎉 Facebook tables migration completed successfully!")
            
            # Show table structure
            print("\n📋 Table structure:")
            show_tables = "SHOW TABLES LIKE '%facebook%'"
            result = connection.execute(text(show_tables))
            tables = result.fetchall()
            
            for table in tables:
                table_name = table[0]
                print(f"\n📊 Table: {table_name}")
                
                # Show table structure
                describe_table = f"DESCRIBE {table_name}"
                result = connection.execute(text(describe_table))
                columns = result.fetchall()
                
                for column in columns:
                    print(f"  - {column[0]}: {column[1]} ({column[2]})")
            
            # Show messages table structure
            print(f"\n📊 Table: messages (updated)")
            describe_messages = "DESCRIBE messages"
            result = connection.execute(text(describe_messages))
            columns = result.fetchall()
            
            for column in columns:
                print(f"  - {column[0]}: {column[1]} ({column[2]})")
                
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        return False
    
    return True

def rollback_facebook_tables():
    """Rollback Facebook-related tables (for testing)"""
    
    engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
    
    try:
        with engine.connect() as connection:
            print("🔄 Rolling back Facebook tables...")
            
            # Remove facebook_message_id column from messages table
            print("📝 Removing facebook_message_id column from messages table...")
            remove_column = """
            ALTER TABLE `messages` 
            DROP COLUMN IF EXISTS `facebook_message_id`
            """
            
            connection.execute(text(remove_column))
            print("✅ facebook_message_id column removed from messages table")
            
            # Drop agent_facebook_pages table
            print("📋 Dropping agent_facebook_pages table...")
            drop_table = "DROP TABLE IF EXISTS `agent_facebook_pages`"
            
            connection.execute(text(drop_table))
            print("✅ agent_facebook_pages table dropped")
            
            connection.commit()
            print("🎉 Facebook tables rollback completed successfully!")
            
    except Exception as e:
        print(f"❌ Error during rollback: {e}")
        return False
    
    return True

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Facebook tables migration script')
    parser.add_argument('--rollback', action='store_true', help='Rollback Facebook tables')
    
    args = parser.parse_args()
    
    if args.rollback:
        print("🔄 Starting Facebook tables rollback...")
        success = rollback_facebook_tables()
    else:
        print("🔄 Starting Facebook tables migration...")
        success = migrate_facebook_tables()
    
    if success:
        print("✅ Migration completed successfully!")
        sys.exit(0)
    else:
        print("❌ Migration failed!")
        sys.exit(1) 