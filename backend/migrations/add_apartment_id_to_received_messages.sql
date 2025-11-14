-- Migration script để thêm cột apartment_id vào bảng received_messages
-- File: backend/migrations/add_apartment_id_to_received_messages.sql

-- Thêm cột apartment_id vào bảng received_messages
ALTER TABLE received_messages 
ADD COLUMN apartment_id INT NULL COMMENT 'ID của apartment được tạo từ message này';

-- Thêm index để tối ưu query
ALTER TABLE received_messages 
ADD INDEX idx_apartment_id (apartment_id);

-- Thêm foreign key constraint (optional - có thể bỏ qua nếu không muốn constraint)
-- ALTER TABLE received_messages 
-- ADD CONSTRAINT fk_received_messages_apartment_id 
-- FOREIGN KEY (apartment_id) REFERENCES warehouse.apartments(id) 
-- ON DELETE SET NULL ON UPDATE CASCADE;






