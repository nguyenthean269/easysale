#!/usr/bin/env python3
"""
Migration script to add categories table and initial data
"""

import MySQLdb
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def migrate_categories():
    """Add categories table and initial data"""
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
        
        # Check if categories table exists
        cursor.execute("SHOW TABLES LIKE 'categories'")
        table_exists = cursor.fetchone()
        
        if not table_exists:
            print("Creating categories table...")
            
            # Create categories table
            create_table_sql = """
            CREATE TABLE categories (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
            """
            cursor.execute(create_table_sql)
            
            # Insert initial categories
            insert_categories_sql = """
            INSERT INTO categories (id, name, description) VALUES 
            (1, 'General', 'General documents and content'),
            (2, 'Real Estate', 'Real estate related documents'),
            (3, 'Business', 'Business documents and reports'),
            (4, 'News', 'News articles and updates')
            """
            cursor.execute(insert_categories_sql)
            
            print("Categories table created and populated successfully")
        else:
            print("Categories table already exists")
            
            # Check if categories have data
            cursor.execute("SELECT COUNT(*) FROM categories")
            count = cursor.fetchone()[0]
            
            if count == 0:
                print("Adding initial categories data...")
                insert_categories_sql = """
                INSERT INTO categories (id, name, description) VALUES 
                (1, 'General', 'General documents and content'),
                (2, 'Real Estate', 'Real estate related documents'),
                (3, 'Business', 'Business documents and reports'),
                (4, 'News', 'News articles and updates')
                """
                cursor.execute(insert_categories_sql)
                print("Categories data added successfully")
            else:
                print(f"Categories table already has {count} records")
        
        # Commit changes
        conn.commit()
        print("Migration completed successfully")
        
    except MySQLdb.Error as err:
        print(f"Database error: {err}")
        if conn:
            conn.rollback()
    except Exception as e:
        print(f"Error: {e}")
        if conn:
            conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            print("Database connection closed")

if __name__ == "__main__":
    migrate_categories() 