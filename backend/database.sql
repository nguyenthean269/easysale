-- EasySale Database Schema
-- Tạo cơ sở dữ liệu
CREATE DATABASE IF NOT EXISTS easysale_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE easysale_db;

-- Bảng Users (Người dùng)
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(120) UNIQUE,
    full_name VARCHAR(100),
    phone VARCHAR(20),
    role ENUM('admin', 'user', 'manager') NOT NULL DEFAULT 'user',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_email (email),
    INDEX idx_role (role)
);

-- Thêm dữ liệu mẫu

-- Thêm admin user (password: admin123)
INSERT INTO users (username, password, email, full_name, role) VALUES 
('admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.i8mG', 'admin@easysale.com', 'Administrator', 'admin');

-- Thêm user thường (password: user123)
INSERT INTO users (username, password, email, full_name, role) VALUES 
('user', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.i8mG', 'user@easysale.com', 'Regular User', 'user');

CREATE TABLE link_crawls (
  id int NOT NULL AUTO_INCREMENT,
  link int NOT NULL,
  content longtext CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  crawl_tool enum('firecrawl','watercrawl') NOT NULL,
  user_id int NOT NULL,
  started_at datetime NOT NULL,
  done_at datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY user_id (`user_id`),
  CONSTRAINT link_crawls_ibfk_1 FOREIGN KEY (`user_id`) REFERENCES users (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;



CREATE TABLE documents (
  id int NOT NULL AUTO_INCREMENT,
  title varchar(255) NOT NULL,
  source_type enum('pdf','docx','web','text') NOT NULL,
  source_path text,
  created_by varchar(100) DEFAULT NULL,
  created_at datetime DEFAULT CURRENT_TIMESTAMP,
  updated_at datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  status enum('active','inactive','pending') DEFAULT 'active',
  description text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


CREATE TABLE document_chunks (
  id int NOT NULL AUTO_INCREMENT,
  document_id int NOT NULL,
  chunk_index int NOT NULL,
  content text NOT NULL,
  milvus_id varchar(100) DEFAULT NULL,
  created_at datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY document_id (`document_id`),
  CONSTRAINT document_chunks_ibfk_1 FOREIGN KEY (`document_id`) REFERENCES documents (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;