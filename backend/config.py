"""
Configuration management cho EasySale
"""

import os
from dotenv import load_dotenv

# Load environment variables từ file .env
load_dotenv()

class Config:
    """Base configuration class"""
    
    # Database Configuration
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '3306')
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_NAME = os.getenv('DB_NAME', 'easysale_db')
    
    # SQLAlchemy Configuration
    SQLALCHEMY_DATABASE_URI = f"mysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT Configuration
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-jwt-secret-key')
    
    # Flask Configuration
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    # Rate Limiting Configuration
    RATE_LIMIT_STORAGE_URI = os.getenv('RATE_LIMIT_STORAGE_URI', 'memory://')
    
    # Redis Configuration
    REDIS_URL = os.getenv('REDIS_URL', None)
    
    # Server Configuration
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', '5000'))
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # Firecrawl API Configuration
    FIRECRAWL_API_KEY = os.getenv('FIRECRAWL_API_KEY', '')
    FIRECRAWL_API_URL = os.getenv('FIRECRAWL_API_URL', 'https://api.firecrawl.dev/scrape')
    
    # Milvus Configuration
    MILVUS_HOST = os.getenv('MILVUS_HOST', 'localhost')
    MILVUS_PORT = os.getenv('MILVUS_PORT', '19530')
    MILVUS_COLLECTION_NAME = os.getenv('MILVUS_COLLECTION_NAME', 'document_chunks')
    MILVUS_DIMENSION = int(os.getenv('MILVUS_DIMENSION', '768'))  # Dimension của embedding vector
    
    # Embedding Model Configuration
    EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'sentence-transformers/all-MiniLM-L6-v2')

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Sử dụng Redis cho rate limiting trong production
    RATE_LIMIT_STORAGE_URI = os.getenv('REDIS_URL', 'memory://')

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    # Sử dụng SQLite cho testing
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Lấy configuration dựa trên environment"""
    env = os.getenv('FLASK_ENV', 'development')
    return config.get(env, config['default'])

def get_database_url():
    """Lấy database URL từ environment variables"""
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '3306')
    db_user = os.getenv('DB_USER', 'root')
    db_password = os.getenv('DB_PASSWORD', '')
    db_name = os.getenv('DB_NAME', 'easysale_db')
    
    return f"mysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

def validate_config():
    """Validate configuration"""
    required_vars = ['DB_USER', 'DB_PASSWORD', 'DB_NAME']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️  Warning: Missing environment variables: {', '.join(missing_vars)}")
        print("   Please check your .env file or set these variables.")
        return False
    
    return True 