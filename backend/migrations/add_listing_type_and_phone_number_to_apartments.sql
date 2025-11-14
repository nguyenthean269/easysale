-- Migration: Add listing_type and phone_number columns to apartments table
-- Date: 2025-01-XX
-- Description: Add listing_type (enum) and phone_number (varchar) columns to support Zalo message processing

-- Add listing_type column (enum for listing purpose)
ALTER TABLE `apartments` 
ADD COLUMN `listing_type` enum('CAN_THUE','CAN_CHO_THUE','CAN_BAN','CAN_MUA','KHAC') 
CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL 
COMMENT 'Mục đích tin đăng: cần thuê, cần cho thuê, cần bán, cần mua, khác' 
AFTER `price_rent`;

-- Add phone_number column (varchar for contact phone)
ALTER TABLE `apartments` 
ADD COLUMN `phone_number` varchar(50) 
CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL 
COMMENT 'Số điện thoại liên hệ' 
AFTER `listing_type`;

