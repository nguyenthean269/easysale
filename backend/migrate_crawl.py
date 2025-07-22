#!/usr/bin/env python3
"""
Migration script cho bảng link_crawls
"""

from app import app, db
from models import LinkCrawl

def migrate_crawl_table():
    """Tạo bảng link_crawls nếu chưa tồn tại"""
    with app.app_context():
        try:
            # Tạo bảng link_crawls
            db.create_all()
            print("✅ Bảng link_crawls đã được tạo thành công!")
            
            # Kiểm tra xem bảng đã tồn tại chưa
            result = db.engine.execute("SHOW TABLES LIKE 'link_crawls'")
            if result.fetchone():
                print("✅ Bảng link_crawls đã tồn tại trong database")
            else:
                print("❌ Bảng link_crawls chưa được tạo")
                
        except Exception as e:
            print(f"❌ Lỗi khi tạo bảng: {str(e)}")

if __name__ == "__main__":
    print("🔄 Đang migrate database cho module crawl...")
    migrate_crawl_table()
    print("✅ Migration hoàn tất!") 