# Migration Guide: Chuyển đổi từ received_messages sang zalo_received_messages

## Tổng quan

Migration này chuyển đổi từ bảng `received_messages` sang `zalo_received_messages` với các thay đổi chính:

1. **Thay đổi tên bảng**: `received_messages` → `zalo_received_messages`
2. **Thay đổi trường**: `status_push_warehouse` → `warehouse_id`
3. **Thêm trường mới**: `added_document_chunks`
4. **Cập nhật foreign keys**: Tham chiếu đến `zalo_sessions` và `zalo_configs`

## Schema Changes

### Bảng cũ (received_messages)
```sql
CREATE TABLE `received_messages` (
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
  `status_push_warehouse` enum('NOT_YET','PUSHED') DEFAULT 'NOT_YET',
  `reply_quote` text,
  `content_hash` char(40) GENERATED ALWAYS AS (sha(`content`)) STORED,
  PRIMARY KEY (`id`),
  KEY `session_id` (`session_id`),
  KEY `config_id` (`config_id`),
  CONSTRAINT `received_messages_ibfk_1` FOREIGN KEY (`session_id`) REFERENCES `sessions` (`id`),
  CONSTRAINT `received_messages_ibfk_2` FOREIGN KEY (`config_id`) REFERENCES `configs` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4701 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
```

### Bảng mới (zalo_received_messages)
```sql
CREATE TABLE `zalo_received_messages` (
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
  `warehouse_id` bigint DEFAULT NULL,  -- THAY ĐỔI CHÍNH
  `reply_quote` text,
  `content_hash` char(40) GENERATED ALWAYS AS (sha(`content`)) STORED,
  `added_document_chunks` tinyint DEFAULT NULL,  -- TRƯỜNG MỚI
  PRIMARY KEY (`id`),
  KEY `session_id` (`session_id`),
  KEY `config_id` (`config_id`),
  CONSTRAINT `zalo_received_messages_ibfk_1` FOREIGN KEY (`session_id`) REFERENCES `zalo_sessions` (`id`),
  CONSTRAINT `zalo_received_messages_ibfk_2` FOREIGN KEY (`config_id`) REFERENCES `zalo_configs` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5455 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
```

## Logic Mapping

### Trường status_push_warehouse → warehouse_id
- `status_push_warehouse = 'NOT_YET'` → `warehouse_id = NULL`
- `status_push_warehouse = 'PUSHED'` → `warehouse_id = [apartment_id]` (ID thực tế từ warehouse database)

## Code Changes

### Backend Changes

1. **ZaloMessageProcessor** (`backend/services/zalo_message_processor.py`):
   - `get_unprocessed_messages()`: Sử dụng `warehouse_id IS NULL` thay vì `status_push_warehouse = 'NOT_YET'`
   - `update_message_warehouse_id()`: Thay thế `update_message_status()`
   - Query: `FROM zalo_received_messages` thay vì `FROM received_messages`

2. **Model** (`backend/models.py`):
   - `ZaloReceivedMessage`: Thêm trường `warehouse_id`, loại bỏ `status_push_warehouse`

3. **Routes**:
   - `zalo_test.py`: Cập nhật parameter từ `status` sang `warehouse_id`
   - `zalo_chunks.py`: Thêm thống kê `warehouse_processed_messages`

### Frontend Changes

1. **Service** (`frontend/src/app/services/zalo-test.service.ts`):
   - Interface `UnprocessedMessage`: Thêm các trường mới, loại bỏ `status`
   - Method `getUnprocessedMessages()`: Sử dụng `warehouse_id` parameter

2. **Component** (`frontend/src/app/pages/zalo-test/zalo-test.component.ts`):
   - Filter: `messageWarehouseIdFilter` thay vì `messageStatusFilter`
   - Display: Hiển thị `warehouse_id` thay vì `status`
   - Options: "Chưa push vào Warehouse", "Đã push vào Warehouse", "Tất cả Messages"

## Migration Steps

1. **Backup dữ liệu**:
   ```sql
   CREATE TABLE received_messages_backup AS SELECT * FROM received_messages;
   ```

2. **Chạy migration script**:
   ```bash
   mysql -u username -p easychat < backend/migrations/migrate_to_zalo_received_messages.sql
   ```

3. **Kiểm tra dữ liệu**:
   ```sql
   SELECT COUNT(*) as total_messages FROM zalo_received_messages;
   SELECT COUNT(*) as messages_with_warehouse_id FROM zalo_received_messages WHERE warehouse_id IS NOT NULL;
   SELECT COUNT(*) as messages_without_warehouse_id FROM zalo_received_messages WHERE warehouse_id IS NULL;
   ```

4. **Cập nhật warehouse_id thực tế**:
   - Cần mapping giữa message_id và apartment_id từ warehouse database
   - Cập nhật `warehouse_id` cho các tin nhắn đã được xử lý

5. **Xóa bảng cũ** (sau khi kiểm tra):
   ```sql
   DROP TABLE received_messages;
   ```

## Testing

1. **Test API endpoints**:
   - `/api/zalo-test/unprocessed-messages?warehouse_id=NULL`
   - `/api/zalo-test/unprocessed-messages?warehouse_id=NOT_NULL`
   - `/api/zalo-test/unprocessed-messages?warehouse_id=ALL`

2. **Test frontend**:
   - Kiểm tra filter dropdown
   - Kiểm tra hiển thị warehouse_id
   - Kiểm tra thống kê

3. **Test processing**:
   - Chạy batch processing
   - Kiểm tra warehouse_id được cập nhật đúng

## Rollback Plan

Nếu cần rollback:
1. Restore từ backup: `received_messages_backup`
2. Revert code changes
3. Cập nhật lại environment variables nếu cần
