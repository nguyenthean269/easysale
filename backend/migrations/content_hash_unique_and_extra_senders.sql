-- Migration: content_hash UNIQUE + bảng lưu sender_id trùng
-- Database: easychat
-- Chạy sau khi backup. Thứ tự: 1) Tạo bảng mới 2) Di chuyển sender trùng 3) Xóa bản ghi trùng 4) Thêm UNIQUE

-- ---------------------------------------------------------------------------
-- Bước 1a: Tạo bảng (không FK) để tránh lock
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `zalo_received_message_extra_senders` (
  `id` int NOT NULL AUTO_INCREMENT,
  `message_id` int NOT NULL COMMENT 'FK tới zalo_received_messages.id (bản ghi canonical cùng content_hash)',
  `sender_id` varchar(255) NOT NULL,
  `sender_name` varchar(255) DEFAULT NULL,
  `session_id` int NOT NULL,
  `config_id` int DEFAULT NULL,
  `received_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_message_sender` (`message_id`, `sender_id`),
  KEY `idx_message_id` (`message_id`),
  KEY `idx_sender_id` (`sender_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
COMMENT='Sender_id của các tin nhắn trùng content (insert sau bản ghi đầu theo content_hash)';

-- ---------------------------------------------------------------------------
-- Bước 1b: Thêm FK sau (giảm lock khi tạo bảng)
-- ---------------------------------------------------------------------------
ALTER TABLE `zalo_received_message_extra_senders`
  ADD CONSTRAINT `zalo_received_message_extra_senders_ibfk_1` FOREIGN KEY (`message_id`) REFERENCES `zalo_received_messages` (`id`) ON DELETE CASCADE;
ALTER TABLE `zalo_received_message_extra_senders`
  ADD CONSTRAINT `zalo_received_message_extra_senders_ibfk_2` FOREIGN KEY (`session_id`) REFERENCES `zalo_sessions` (`id`);
ALTER TABLE `zalo_received_message_extra_senders`
  ADD CONSTRAINT `zalo_received_message_extra_senders_ibfk_3` FOREIGN KEY (`config_id`) REFERENCES `zalo_configs` (`id`);

-- ---------------------------------------------------------------------------
-- Bước 2: Di chuyển thông tin sender từ các bản ghi trùng vào bảng extra_senders
-- (Giữ lại bản ghi có id nhỏ nhất cho mỗi content_hash; các bản ghi còn lại ghi sender vào extra)
-- ---------------------------------------------------------------------------
INSERT INTO `zalo_received_message_extra_senders` (`message_id`, `sender_id`, `sender_name`, `session_id`, `config_id`, `received_at`)
SELECT 
  canonical.keep_id AS message_id,
  z.sender_id,
  z.sender_name,
  z.session_id,
  z.config_id,
  z.received_at
FROM `zalo_received_messages` z
INNER JOIN (
  SELECT content_hash, MIN(id) AS keep_id
  FROM `zalo_received_messages`
  WHERE content_hash IS NOT NULL
  GROUP BY content_hash
) canonical ON z.content_hash = canonical.content_hash AND z.id <> canonical.keep_id
WHERE z.content_hash IS NOT NULL
ON DUPLICATE KEY UPDATE sender_name = VALUES(sender_name), received_at = VALUES(received_at);

-- ---------------------------------------------------------------------------
-- Bước 3: Xóa các bản ghi trùng (chỉ giữ 1 bản ghi per content_hash)
-- ---------------------------------------------------------------------------
DELETE z FROM `zalo_received_messages` z
INNER JOIN (
  SELECT content_hash, MIN(id) AS keep_id
  FROM `zalo_received_messages`
  WHERE content_hash IS NOT NULL
  GROUP BY content_hash
) canonical ON z.content_hash = canonical.content_hash AND z.id <> canonical.keep_id;

-- ---------------------------------------------------------------------------
-- Bước 4: Thêm UNIQUE cho content_hash
-- ---------------------------------------------------------------------------
ALTER TABLE `zalo_received_messages`
  ADD UNIQUE KEY `uq_content_hash` (`content_hash`);
