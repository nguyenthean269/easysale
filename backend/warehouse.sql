-- Adminer 5.3.0 MySQL 8.0.27 dump

SET NAMES utf8;
SET time_zone = '+00:00';
SET foreign_key_checks = 0;
SET sql_mode = 'NO_AUTO_VALUE_ON_ZERO';

SET NAMES utf8mb4;

DROP TABLE IF EXISTS `apartments`;
CREATE TABLE `apartments` (
  `id` int NOT NULL AUTO_INCREMENT,
  `property_group` int DEFAULT NULL COMMENT 'Thuộc unit cha nào',
  `unit_type` int DEFAULT NULL COMMENT 'Loại căn hộ',
  `unit_code` char(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT 'Mã căn',
  `unit_axis` char(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT 'Trục căn',
  `unit_floor_number` char(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT 'Tầng',
  `area_land` decimal(10,2) DEFAULT NULL COMMENT 'Diện tích đất',
  `area_construction` decimal(10,2) DEFAULT NULL COMMENT 'Diện tích phần xây dựng trên đất',
  `area_net` decimal(10,2) DEFAULT NULL COMMENT 'Diện tích thông thủy: diện tích sử dụng thực tế (không tính tường, cột)',
  `area_gross` decimal(10,2) DEFAULT NULL COMMENT 'Diện tích tim tường: diện tích tính cả tường bao, tường ngăn',
  `num_bedrooms` int DEFAULT NULL,
  `num_bathrooms` int DEFAULT NULL,
  `type_view` int DEFAULT NULL,
  `position_latitude` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `position_longitude` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `direction_door` enum('D','T','N','B','DB','DN','TB','TN') CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT 'Hướng cửa chính',
  `direction_balcony` enum('D','T','N','B','DB','DN','TB','TN') CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT 'Hướng ban công',
  `price` decimal(18,0) DEFAULT NULL COMMENT 'Giá niêm yết',
  `price_early` decimal(18,0) DEFAULT NULL COMMENT 'Giá thanh toán sớm',
  `price_schedule` decimal(18,0) DEFAULT NULL COMMENT 'Giá thanh toán theo tiến độ',
  `price_loan` decimal(18,0) DEFAULT NULL COMMENT 'Giá nếu vay ngân hàng',
  `notes` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci,
  `status` enum('CHUA_BAN','DA_LOCK','DA_COC','DA_BAN') CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT 'Trạng thái giao dịch của căn hộ: CHUA_BAN, DA_LOCK, DA_COC, DA_BAN',
  `unit_allocation` set('QUY_DOC_QUYEN','QUY_AN','QUY_CHEO','QUY_THUONG') CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT 'Loại quỹ căn: Quỹ độc quyền, Quỹ ẩn, Quỹ chéo, Quỹ thưởng',
  `images_marker` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin COMMENT 'Ảnh chỉ căn',
  `images_pricing_sheet` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin COMMENT 'Ảnh phiếu tính giá',
  `images_floor_plan` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin COMMENT 'Ảnh mặt bằng căn hộ',
  `images_sales_policy` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin COMMENT 'Ảnh chính sách bán hàng của căn',
  PRIMARY KEY (`id`),
  KEY `property_group` (`property_group`),
  KEY `type_apartment` (`unit_type`),
  KEY `view` (`type_view`),
  KEY `num_bedrooms` (`num_bedrooms`),
  CONSTRAINT `apartments_ibfk_1` FOREIGN KEY (`property_group`) REFERENCES `property_groups` (`id`),
  CONSTRAINT `apartments_ibfk_2` FOREIGN KEY (`unit_type`) REFERENCES `types_unit` (`id`),
  CONSTRAINT `apartments_ibfk_3` FOREIGN KEY (`unit_type`) REFERENCES `types_unit` (`id`),
  CONSTRAINT `apartments_ibfk_4` FOREIGN KEY (`type_view`) REFERENCES `types_view` (`id`),
  CONSTRAINT `apartments_chk_1` CHECK (json_valid(`images_marker`))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


DROP TABLE IF EXISTS `apartments_preview`;
CREATE TABLE `apartments_preview` (
  `id` int NOT NULL AUTO_INCREMENT,
  `preview_import_id` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `property_group` int DEFAULT NULL COMMENT 'Thuộc unit cha nào',
  `unit_type` int DEFAULT NULL COMMENT 'Loại căn hộ',
  `unit_code` char(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT 'Mã căn',
  `unit_axis` char(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT 'Trục căn',
  `unit_floor_number` char(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT 'Tầng',
  `area_land` decimal(10,2) DEFAULT NULL COMMENT 'Diện tích đất',
  `area_construction` decimal(10,2) DEFAULT NULL COMMENT 'Diện tích phần xây dựng trên đất',
  `area_net` decimal(10,2) DEFAULT NULL COMMENT 'Diện tích thông thủy: diện tích sử dụng thực tế (không tính tường, cột)',
  `area_gross` decimal(10,2) DEFAULT NULL COMMENT 'Diện tích tim tường: diện tích tính cả tường bao, tường ngăn',
  `num_bedrooms` int DEFAULT NULL,
  `num_bathrooms` int DEFAULT NULL,
  `type_view` int DEFAULT NULL,
  `position_latitude` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `position_longitude` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `direction_door` enum('D','T','N','B','DB','DN','TB','TN') CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT 'Hướng cửa chính',
  `direction_balcony` enum('D','T','N','B','DB','DN','TB','TN') CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT 'Hướng ban công',
  `price` decimal(18,0) DEFAULT NULL COMMENT 'Giá niêm yết',
  `price_early` decimal(18,0) DEFAULT NULL COMMENT 'Giá thanh toán sớm',
  `price_schedule` decimal(18,0) DEFAULT NULL COMMENT 'Giá thanh toán theo tiến độ',
  `price_loan` decimal(18,0) DEFAULT NULL COMMENT 'Giá nếu vay ngân hàng',
  `notes` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci,
  `status` enum('CHUA_BAN','DA_LOCK','DA_COC','DA_BAN') CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT 'Trạng thái giao dịch của căn hộ: CHUA_BAN, DA_LOCK, DA_COC, DA_BAN',
  `status_sync` enum('CHUA_DONG_BO','DA_DONG_BO','DA_HUY') CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT 'Trạng thái được phê duyệt vào apartments hay chưa',
  `unit_allocation` set('QUY_DOC_QUYEN','QUY_AN','QUY_CHEO','QUY_THUONG') CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT 'Loại quỹ căn: Quỹ độc quyền, Quỹ ẩn, Quỹ chéo, Quỹ thưởng',
  `images_marker` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin COMMENT 'Ảnh chỉ căn',
  `images_pricing_sheet` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin COMMENT 'Ảnh phiếu tính giá',
  `images_floor_plan` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin COMMENT 'Ảnh mặt bằng căn hộ',
  `images_sales_policy` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin COMMENT 'Ảnh chính sách bán hàng của căn',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `property_group` (`property_group`),
  KEY `type_apartment` (`unit_type`),
  KEY `view` (`type_view`),
  KEY `num_bedrooms` (`num_bedrooms`),
  CONSTRAINT `apartments_preview_ibfk_1` FOREIGN KEY (`property_group`) REFERENCES `property_groups` (`id`),
  CONSTRAINT `apartments_preview_ibfk_2` FOREIGN KEY (`unit_type`) REFERENCES `types_unit` (`id`),
  CONSTRAINT `apartments_preview_ibfk_3` FOREIGN KEY (`unit_type`) REFERENCES `types_unit` (`id`),
  CONSTRAINT `apartments_preview_ibfk_4` FOREIGN KEY (`type_view`) REFERENCES `types_view` (`id`),
  CONSTRAINT `apartments_preview_chk_1` CHECK (json_valid(`images_marker`))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


DROP TABLE IF EXISTS `category_tags`;
CREATE TABLE `category_tags` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `slug` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `type` enum('tag','category') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `slug` (`slug`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


DROP TABLE IF EXISTS `contractors`;
CREATE TABLE `contractors` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci,
  `website` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


DROP TABLE IF EXISTS `deal_deposits`;
CREATE TABLE `deal_deposits` (
  `id` int NOT NULL AUTO_INCREMENT,
  `property_group_id` int NOT NULL COMMENT 'Dự án chứa căn hộ được cọc',
  `unit_id` int NOT NULL COMMENT 'Căn hộ được cọc',
  `user_id` int NOT NULL,
  `lock_id` int DEFAULT NULL COMMENT 'ID của lần lock liên quan (nếu có)',
  `deposit_amount` decimal(18,0) NOT NULL COMMENT 'Số tiền cọc',
  `deposit_date` datetime DEFAULT CURRENT_TIMESTAMP,
  `status` enum('requested','pending','completed','cancelled','refunded') CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT 'requested',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `cccd_front_image` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT 'Link ảnh căn cước công dân mặt trước',
  `cccd_back_image` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT 'Link ảnh căn cước công dân mặt sau',
  `authorization_image` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT 'Link ảnh ủy nhiệm chi',
  `customer_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT 'Họ và tên khách hàng',
  `customer_cccd_number` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT 'Số căn cước công dân của khách hàng',
  PRIMARY KEY (`id`),
  KEY `property_group_id` (`property_group_id`),
  KEY `unit_id` (`unit_id`),
  KEY `user_id` (`user_id`),
  KEY `lock_id` (`lock_id`),
  CONSTRAINT `deal_deposits_ibfk_1` FOREIGN KEY (`property_group_id`) REFERENCES `property_groups` (`id`),
  CONSTRAINT `deal_deposits_ibfk_2` FOREIGN KEY (`unit_id`) REFERENCES `apartments` (`id`),
  CONSTRAINT `deal_deposits_ibfk_3` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `deal_deposits_ibfk_4` FOREIGN KEY (`lock_id`) REFERENCES `deal_locks` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


DROP TABLE IF EXISTS `deal_locks`;
CREATE TABLE `deal_locks` (
  `id` int NOT NULL AUTO_INCREMENT,
  `property_group_id` int NOT NULL COMMENT 'Dự án chứa căn hộ',
  `unit_id` int NOT NULL COMMENT 'Căn hộ được lock',
  `user_id` int NOT NULL,
  `lock_count` int DEFAULT '1' COMMENT 'Thứ tự lock liên tiếp của user trên cùng căn hộ',
  `lock_start` datetime NOT NULL,
  `lock_end` datetime NOT NULL,
  `status` enum('active','expired','cancelled') CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT 'active',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `property_group_id` (`property_group_id`),
  KEY `unit_id` (`unit_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `deal_locks_ibfk_1` FOREIGN KEY (`property_group_id`) REFERENCES `property_groups` (`id`),
  CONSTRAINT `deal_locks_ibfk_2` FOREIGN KEY (`unit_id`) REFERENCES `apartments` (`id`),
  CONSTRAINT `deal_locks_ibfk_3` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


DROP TABLE IF EXISTS `deal_property_settings`;
CREATE TABLE `deal_property_settings` (
  `id` int NOT NULL AUTO_INCREMENT,
  `property_group_id` int NOT NULL COMMENT 'Dự án áp dụng cài đặt',
  `lock_duration_minutes` int DEFAULT '60' COMMENT 'Thời gian lock mặc định (phút)',
  `max_consecutive_locks_per_property` int DEFAULT '3' COMMENT 'Số lần lock liên tiếp tối đa cho cùng một căn hộ',
  `max_active_locks_per_user` int DEFAULT '5' COMMENT 'Số căn tối đa mà 1 user có thể lock cùng lúc. NULL là không giới hạn',
  `allow_deposit_without_lock` tinyint(1) DEFAULT '0' COMMENT 'Cho phép cọc mà không cần lock hay không',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `deposit_account_number` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT 'Số tài khoản nhận tiền cọc',
  `deposit_account_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT 'Tên chủ tài khoản nhận tiền cọc',
  `deposit_amount` decimal(18,0) DEFAULT NULL COMMENT 'Số tiền cọc quy định mặc định',
  `deposit_transfer_note` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT 'Nội dung chuyển khoản gợi ý khi đặt cọc',
  `deposit_bank_code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT 'Mã ngân hàng hoặc định danh ngân hàng nhận cọc',
  `deposit_bank_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT 'Tên ngân hàng và chi nhánh',
  PRIMARY KEY (`id`),
  KEY `property_group_id` (`property_group_id`),
  CONSTRAINT `deal_property_settings_ibfk_1` FOREIGN KEY (`property_group_id`) REFERENCES `property_groups` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


DROP TABLE IF EXISTS `developers`;
CREATE TABLE `developers` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci,
  `website` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


DROP TABLE IF EXISTS `news`;
CREATE TABLE `news` (
  `id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `content` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `thumbnail` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `active` tinyint(1) DEFAULT '1',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `project_id` int DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


DROP TABLE IF EXISTS `news_category_tags`;
CREATE TABLE `news_category_tags` (
  `news_id` int NOT NULL,
  `category_tag_id` int NOT NULL,
  PRIMARY KEY (`news_id`,`category_tag_id`),
  KEY `category_tag_id` (`category_tag_id`),
  CONSTRAINT `news_category_tags_ibfk_1` FOREIGN KEY (`news_id`) REFERENCES `news` (`id`) ON DELETE CASCADE,
  CONSTRAINT `news_category_tags_ibfk_2` FOREIGN KEY (`category_tag_id`) REFERENCES `category_tags` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;


DROP TABLE IF EXISTS `permissions`;
CREATE TABLE `permissions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `description` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


DROP TABLE IF EXISTS `property_group_background_images`;
CREATE TABLE `property_group_background_images` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `property_group_id` int NOT NULL,
  `image_url` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `tile_prefix` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `corners` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `zoom_level` int NOT NULL,
  `opacity` decimal(3,2) DEFAULT '0.70',
  `is_active` tinyint(1) DEFAULT '1',
  `version` int DEFAULT '1',
  `created_by` int DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_property_group_active` (`property_group_id`,`is_active`),
  KEY `idx_property_group_version` (`property_group_id`,`version`),
  CONSTRAINT `property_group_background_images_ibfk_1` FOREIGN KEY (`property_group_id`) REFERENCES `property_groups` (`id`),
  CONSTRAINT `property_group_background_images_chk_1` CHECK (json_valid(`corners`))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


DROP TABLE IF EXISTS `property_group_policy`;
CREATE TABLE `property_group_policy` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `property_group_id` int NOT NULL,
  `title` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Tiêu đề tiến độ',
  `link_image` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Link ảnh',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `fk_property_group_policy_group` (`property_group_id`),
  CONSTRAINT `fk_property_group_policy_group` FOREIGN KEY (`property_group_id`) REFERENCES `property_groups` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


DROP TABLE IF EXISTS `property_group_processes`;
CREATE TABLE `property_group_processes` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `property_group_id` int NOT NULL,
  `title` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `drive_link` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Loại tiến độ hay loại tài liệu',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_property_group_id` (`property_group_id`),
  CONSTRAINT `fk_process_property_group` FOREIGN KEY (`property_group_id`) REFERENCES `property_groups` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


DROP TABLE IF EXISTS `property_groups`;
CREATE TABLE `property_groups` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT 'Tên nhóm (VD: Vinhomes Smart City, Sapphire 1, Tòa S1.01)',
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT 'Mô tả',
  `thumbnail` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `image_list` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin,
  `banner` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin COMMENT 'Danh sách URL banner',
  `build_density` decimal(5,2) DEFAULT NULL,
  `group_type` int NOT NULL,
  `property_type` enum('lowrise','highrise') CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `parent_id` int DEFAULT NULL COMMENT '-- Nhóm cha (VD: Tòa có parent là Block hoặc Dự án)',
  `developer_id` bigint NOT NULL,
  `contractor_id` bigint DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `green_area` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `project_scale` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `content` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci,
  `discovery_title` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `discovery_content` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci,
  `discovery_image` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `discovery_video_url` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `entertainment_title` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `entertainment_content` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci,
  `entertainment_image` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `entertainment_video_url` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `floor_plan` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin,
  `products` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin,
  `amenities` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin,
  PRIMARY KEY (`id`),
  KEY `fk_property_groups_parent` (`parent_id`),
  KEY `developer_id` (`developer_id`),
  KEY `contractor_id` (`contractor_id`),
  KEY `group_type` (`group_type`),
  CONSTRAINT `fk_property_groups_parent` FOREIGN KEY (`parent_id`) REFERENCES `property_groups` (`id`),
  CONSTRAINT `property_groups_ibfk_1` FOREIGN KEY (`developer_id`) REFERENCES `developers` (`id`),
  CONSTRAINT `property_groups_ibfk_2` FOREIGN KEY (`contractor_id`) REFERENCES `contractors` (`id`),
  CONSTRAINT `property_groups_ibfk_3` FOREIGN KEY (`group_type`) REFERENCES `types_group` (`id`),
  CONSTRAINT `property_groups_chk_1` CHECK (json_valid(`image_list`)),
  CONSTRAINT `property_groups_chk_2` CHECK (json_valid(`banner`)),
  CONSTRAINT `property_groups_chk_3` CHECK (json_valid(`floor_plan`)),
  CONSTRAINT `property_groups_chk_4` CHECK (json_valid(`products`)),
  CONSTRAINT `property_groups_chk_5` CHECK (json_valid(`amenities`))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


DROP TABLE IF EXISTS `role_permissions`;
CREATE TABLE `role_permissions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `role_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_role_permission` (`role_id`,`permission_id`),
  KEY `permission_id` (`permission_id`),
  CONSTRAINT `role_permissions_ibfk_1` FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`),
  CONSTRAINT `role_permissions_ibfk_2` FOREIGN KEY (`permission_id`) REFERENCES `permissions` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


DROP TABLE IF EXISTS `roles`;
CREATE TABLE `roles` (
  `id` int NOT NULL AUTO_INCREMENT,
  `code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `description` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


DROP TABLE IF EXISTS `types_group`;
CREATE TABLE `types_group` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


DROP TABLE IF EXISTS `types_unit`;
CREATE TABLE `types_unit` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `created_at` datetime NOT NULL DEFAULT '0000-00-00 00:00:00' ON UPDATE CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


DROP TABLE IF EXISTS `types_view`;
CREATE TABLE `types_view` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `property_group_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `property_group_id` (`property_group_id`),
  CONSTRAINT `types_view_ibfk_1` FOREIGN KEY (`property_group_id`) REFERENCES `property_groups` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


DROP TABLE IF EXISTS `user_property_groups`;
CREATE TABLE `user_property_groups` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `property_group_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_user_pg` (`user_id`,`property_group_id`),
  KEY `fk_upg_pg` (`property_group_id`),
  CONSTRAINT `fk_upg_pg` FOREIGN KEY (`property_group_id`) REFERENCES `property_groups` (`id`),
  CONSTRAINT `fk_upg_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


DROP TABLE IF EXISTS `user_roles`;
CREATE TABLE `user_roles` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `role_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_user_role` (`user_id`,`role_id`),
  KEY `fk_ur_role` (`role_id`),
  CONSTRAINT `fk_ur_role` FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`),
  CONSTRAINT `fk_ur_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `sso_user_id` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `employee_code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `full_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `status` enum('active','inactive') CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT 'active',
  PRIMARY KEY (`id`),
  UNIQUE KEY `sso_user_id` (`sso_user_id`),
  UNIQUE KEY `employee_code` (`employee_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


DROP VIEW IF EXISTS `view_tree`;
CREATE TABLE `view_tree` (`root_id` int, `root_name` varchar(150), `tree_structure` text);


DROP VIEW IF EXISTS `view_types_unit`;
CREATE TABLE `view_types_unit` (`result` text);


DROP TABLE IF EXISTS `view_tree`;
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `view_tree` AS with recursive `property_hierarchy` as (select `property_groups`.`id` AS `id`,`property_groups`.`name` AS `name`,`property_groups`.`parent_id` AS `parent_id`,0 AS `level`,concat('(ID:',`property_groups`.`id`,') ',`property_groups`.`name`) AS `line`,`property_groups`.`id` AS `root_id`,cast(lpad(`property_groups`.`id`,5,'0') as char(1000) charset utf8mb4) AS `path_order` from `property_groups` where (`property_groups`.`parent_id` is null) union all select `pg`.`id` AS `id`,`pg`.`name` AS `name`,`pg`.`parent_id` AS `parent_id`,(`ph`.`level` + 1) AS `level`,concat(repeat('- ',(`ph`.`level` + 1)),'(ID:',`pg`.`id`,') ',`pg`.`name`) AS `line`,`ph`.`root_id` AS `root_id`,concat(`ph`.`path_order`,'-',lpad(`pg`.`id`,5,'0')) AS `path_order` from (`property_groups` `pg` join `property_hierarchy` `ph` on((`pg`.`parent_id` = `ph`.`id`)))) select `ph`.`root_id` AS `root_id`,(select `property_groups`.`name` from `property_groups` where (`property_groups`.`id` = `ph`.`root_id`)) AS `root_name`,group_concat(`ph`.`line` order by `ph`.`path_order` ASC separator '\n') AS `tree_structure` from `property_hierarchy` `ph` group by `ph`.`root_id`;

DROP TABLE IF EXISTS `view_types_unit`;
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `view_types_unit` AS select group_concat(concat('(ID:',`types_unit`.`id`,') ',`types_unit`.`name`) separator '\n') AS `result` from `types_unit`;

-- 2025-10-26 03:48:55 UTC