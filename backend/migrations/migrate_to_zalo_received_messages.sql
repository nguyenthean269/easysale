-- Migration script để chuyển đổi từ bảng received_messages sang zalo_received_messages
-- File: backend/migrations/migrate_to_zalo_received_messages.sql
-- 
-- LƯU Ý: Chạy script này trong database easychat
-- 
-- Bước 1: Backup dữ liệu hiện tại (khuyến nghị)
-- CREATE TABLE received_messages_backup AS SELECT * FROM received_messages;

-- Bước 2: Tạo bảng zalo_received_messages mới (nếu chưa có)
CREATE TABLE IF NOT EXISTS `zalo_received_messages` (
  `id` int NOT NULL AUTO_INCREMENT,
  `session_id` int NOT NULL,
  `config_id` int DEFAULT NULL,
  `sender_id` varchar(255) DEFAULT NULL,
  `sender_name` varchar(255) DEFAULT NULL,
  `content` text NOT NULL,
  `thread_id` varchar(255) DEFAULT NULL,
  `thread_type` varchar(50) DEFAULT NULL,
  `received_at` datetime DEFAULT NULL,
  `status_push_kafka` int DEFAULT '0',
  `warehouse_id` bigint DEFAULT NULL,
  `reply_quote` text,
  `content_hash` char(40) GENERATED ALWAYS AS (sha(`content`)) STORED,
  `added_document_chunks` tinyint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `session_id` (`session_id`),
  KEY `config_id` (`config_id`),
  KEY `warehouse_id` (`warehouse_id`),
  CONSTRAINT `zalo_received_messages_ibfk_1` FOREIGN KEY (`session_id`) REFERENCES `zalo_sessions` (`id`),
  CONSTRAINT `zalo_received_messages_ibfk_2` FOREIGN KEY (`config_id`) REFERENCES `zalo_configs` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Bước 3: Copy dữ liệu từ bảng cũ sang bảng mới
-- Chuyển đổi status_push_warehouse = 'PUSHED' thành warehouse_id = NULL (tạm thời)
-- Vì chúng ta không có thông tin warehouse_id thực tế từ dữ liệu cũ
INSERT INTO zalo_received_messages (
    id, session_id, config_id, sender_id, sender_name, content, 
    thread_id, thread_type, received_at, status_push_kafka, 
    warehouse_id, reply_quote, content_hash, added_document_chunks
)
SELECT 
    id, session_id, config_id, sender_id, sender_name, content,
    thread_id, thread_type, received_at, status_push_kafka,
    NULL as warehouse_id,  -- Tạm thời set NULL, cần cập nhật sau
    reply_quote, content_hash, NULL as added_document_chunks
FROM received_messages
WHERE NOT EXISTS (
    SELECT 1 FROM zalo_received_messages zrm WHERE zrm.id = received_messages.id
);

-- Bước 4: Cập nhật warehouse_id cho các tin nhắn đã được push
-- LƯU Ý: Cần cập nhật warehouse_id thực tế dựa trên dữ liệu warehouse database
-- Ví dụ: Nếu có mapping giữa message_id và apartment_id trong warehouse
-- UPDATE zalo_received_messages zrm
-- SET warehouse_id = (
--     SELECT apartment_id 
--     FROM warehouse.apartments wa 
--     WHERE wa.message_id = zrm.id  -- Giả sử có trường message_id trong warehouse
-- )
-- WHERE zrm.id IN (
--     SELECT id FROM received_messages 
--     WHERE status_push_warehouse = 'PUSHED'
-- );

-- Bước 5: Xóa bảng cũ (CHỈ CHẠY SAU KHI ĐÃ KIỂM TRA DỮ LIỆU)
-- DROP TABLE received_messages;

-- Bước 6: Kiểm tra dữ liệu
-- SELECT COUNT(*) as total_messages FROM zalo_received_messages;
-- SELECT COUNT(*) as messages_with_warehouse_id FROM zalo_received_messages WHERE warehouse_id IS NOT NULL;
-- SELECT COUNT(*) as messages_without_warehouse_id FROM zalo_received_messages WHERE warehouse_id IS NULL;

-- Bước 7: Cập nhật AUTO_INCREMENT
-- ALTER TABLE zalo_received_messages AUTO_INCREMENT = (SELECT MAX(id) + 1 FROM zalo_received_messages);
