-- Migration: Đổi cột warehouse_id (BIGINT) thành warehouse_ids (JSON set)
-- Database: easychat
-- Bảng: zalo_received_messages
--
-- Chạy trong database easychat. Backup trước khi chạy.

-- Bước 1: Thêm cột mới warehouse_ids (JSON)
ALTER TABLE `zalo_received_messages`
ADD COLUMN `warehouse_ids` JSON DEFAULT NULL COMMENT 'Mảng ID apartment trong warehouse (set)'
AFTER `status_push_kafka`;

-- Bước 2: Copy dữ liệu cũ: mỗi warehouse_id khác NULL -> JSON array một phần tử
UPDATE `zalo_received_messages`
SET `warehouse_ids` = JSON_ARRAY(`warehouse_id`)
WHERE `warehouse_id` IS NOT NULL;

-- Bước 3: Xóa cột warehouse_id (index trên cột này sẽ tự bị xóa)
ALTER TABLE `zalo_received_messages`
DROP COLUMN `warehouse_id`;

-- Bước 4 (tùy chọn) Index cho tìm kiếm theo id trong JSON - MySQL 5.7+
-- CREATE INDEX idx_warehouse_ids ON zalo_received_messages ( (CAST(warehouse_ids AS CHAR(255) ARRAY)) );  -- không hỗ trợ trực tiếp
-- Có thể dùng generated column: ALTER TABLE zalo_received_messages ADD COLUMN warehouse_ids_contains_id ... GENERATED ...
-- Bỏ qua index JSON nếu không cần tối ưu filter theo warehouse_id cụ thể.

-- Kiểm tra sau migration:
-- SELECT id, warehouse_ids, JSON_LENGTH(warehouse_ids) FROM zalo_received_messages WHERE warehouse_ids IS NOT NULL LIMIT 5;
-- SELECT COUNT(*) FROM zalo_received_messages WHERE warehouse_ids IS NULL OR JSON_LENGTH(warehouse_ids) = 0;
-- SELECT COUNT(*) FROM zalo_received_messages WHERE warehouse_ids IS NOT NULL AND JSON_LENGTH(warehouse_ids) > 0;
