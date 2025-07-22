#!/usr/bin/env python3
"""
Script để migrate cột link từ int sang string
"""

from app import app

def migrate_link_column():
    """Migrate cột link từ int sang string"""
    print("🔄 Migrating link column from int to string...")
    
    with app.app_context():
        try:
            # Thay đổi kiểu dữ liệu của cột link
            sql = "ALTER TABLE link_crawls MODIFY COLUMN link VARCHAR(500) NOT NULL"
            with app.db.engine.connect() as conn:
                conn.execute(app.db.text(sql))
                conn.commit()
            print("✅ Successfully migrated link column to VARCHAR(500)")
            
            # Kiểm tra cấu trúc bảng
            with app.db.engine.connect() as conn:
                result = conn.execute(app.db.text("DESCRIBE link_crawls"))
                print("\n📋 Table structure after migration:")
                for row in result:
                    print(f"  {row[0]}: {row[1]}")
                
            return True
            
        except Exception as e:
            print(f"❌ Error during migration: {str(e)}")
            return False

if __name__ == "__main__":
    print("🚀 Starting link column migration...")
    success = migrate_link_column()
    
    if success:
        print("\n🎉 Migration completed successfully!")
    else:
        print("\n❌ Migration failed!") 