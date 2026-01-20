"""
Configuration Management
Load configuration from environment variables
"""

import os
from typing import List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application configuration"""
    
    # MongoDB Configuration
    MONGODB_URI: str = os.getenv("MONGODB_URI", "")
    MONGODB_DATABASE: str = os.getenv("MONGODB_DATABASE", "briefly60")
    
    # Telegram Configuration
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID: int = int(os.getenv("TELEGRAM_CHAT_ID", "0")) if os.getenv("TELEGRAM_CHAT_ID") else 0
    
    # Gemini API Keys (comma-separated in env)
    GEMINI_API_KEYS: List[str] = os.getenv("GEMINI_API_KEYS", "").split(",")
    GEMINI_API_KEYS = [key.strip() for key in GEMINI_API_KEYS if key.strip()]
    
    # Scraper Configuration
    MAX_ARTICLES: int = int(os.getenv("MAX_ARTICLES", "10"))
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "30"))
    USER_AGENT: str = os.getenv("USER_AGENT", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    
    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration"""
        errors = []
        
        if not cls.MONGODB_URI:
            errors.append("MONGODB_URI is required")
        
        if not cls.GEMINI_API_KEYS:
            errors.append("GEMINI_API_KEYS is required")
        
        if errors:
            for error in errors:
                print(f"❌ Config Error: {error}")
            return False
        
        print("✓ Configuration validated successfully")
        return True


# Export config instance
config = Config()
