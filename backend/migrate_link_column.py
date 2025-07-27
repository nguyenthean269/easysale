#!/usr/bin/env python3
"""
Migration script to add milvus_id column to document_chunks table
"""

import MySQLdb
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def migrate_milvus_id():
    """Add milvus_id column to document_chunks table"""
    try:
        # Database configuration from environment variables
        db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', '3306')),
            'user': os.getenv('DB_USER', 'root'),
            'passwd': os.getenv('DB_PASSWORD', ''),
            'db': os.getenv('DB_NAME', 'easysale_db'),
            'charset': 'utf8mb4'
        }
        
        # Connect to database
        conn = MySQLdb.connect(**db_config)
        cursor = conn.cursor()
        
        print("Connected to database successfully")
        
        # Check if milvus_id column exists
        cursor.execute("SHOW COLUMNS FROM document_chunks LIKE 'milvus_id'")
        column_exists = cursor.fetchone()
        
        if column_exists:
            print("✅ Column 'milvus_id' already exists in document_chunks table")
        else:
            # Add milvus_id column
            cursor.execute("""
                ALTER TABLE document_chunks 
                ADD COLUMN milvus_id VARCHAR(100) NULL 
                COMMENT 'ID of vector in Milvus'
            """)
            conn.commit()
            print("✅ Added 'milvus_id' column to document_chunks table")
        
        cursor.close()
        conn.close()
        print("Migration completed successfully")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    migrate_milvus_id() 