# ================================
# config.py
import os
from datetime import timedelta

class Config:
    """Base configuration class"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///case_management.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
    SESSION_COOKIE_SECURE = True  # Set to False for development without HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # WTF configuration
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600
    
    # File upload configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Pagination
    ITEMS_PER_PAGE = 20

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SESSION_COOKIE_SECURE = False  # Allow HTTP in development

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    # Additional production settings
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}