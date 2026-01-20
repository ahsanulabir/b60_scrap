"""
MongoDB Database Integration
Handle database connections and operations
"""

from datetime import datetime
from typing import Dict, Optional
from pymongo import MongoClient

from .config import config
from .helpers import convert_to_utc_plus_6


class MongoDBHandler:
    """MongoDB connection and operations"""
    
    def __init__(self):
        self.client = None
        self.db = None
        self.articles_collection = None
        self._connect()
    
    def _connect(self):
        """Initialize MongoDB connection"""
        try:
            self.client = MongoClient(config.MONGODB_URI)
            self.db = self.client[config.MONGODB_DATABASE]
            self.articles_collection = self.db['articles']
            print("✓ MongoDB connection established")
        except Exception as e:
            print(f"❌ MongoDB connection failed: {e}")
            self.client = None
    
    def check_article_exists(self, source_url: str) -> bool:
        """Check if article already exists in MongoDB"""
        if not self.client:
            print("⚠️  MongoDB not connected")
            return False
        
        try:
            existing = self.articles_collection.find_one({"source_url": source_url})
            return existing is not None
        except Exception as e:
            print(f"⚠️  Error checking existence: {e}")
            return False
    
    def create_article(self, article_data: Dict) -> Dict:
        """Create article in MongoDB"""
        if not self.client:
            raise ValueError("MongoDB not connected")
        
        try:
            # Prepare document according to Article model
            document = {
                "status": "published",
                "source_name": article_data.get("source", ""),
                "source_url": article_data.get("link", ""),
                "title": article_data.get("title", ""),
                "corrected_title": article_data.get("corrected_title") or None,
                "content": article_data.get("full_text", ""),
                "banner": article_data.get("image") if article_data.get("image") != "NO IMAGE" else None,
                "published_at": datetime.fromisoformat(convert_to_utc_plus_6(article_data.get("published", ""))),
                
                # Summaries
                "summary_60_bn": article_data.get("summary_60_bn", ""),
                "summary_60_en": article_data.get("summary_60_en", ""),
                
                # Classification
                "category": article_data.get("category", ""),
                "importance": article_data.get("importance", 5),
                "keywords": article_data.get("keywords", []),
                "clickbait_score": article_data.get("clickbait_score", 0),
                "clickbait_reason": article_data.get("clickbait_reason") or None,
                
                # Quiz questions
                "quiz_questions": article_data.get("mcqs", []),
                
                # Timestamps
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow(),
            }
            
            # Insert into MongoDB
            result = self.articles_collection.insert_one(document)
            article_id = str(result.inserted_id)
            
            print(f"   ✓ Created in MongoDB (ID: {article_id})")
            return {"data": {"id": article_id}}
            
        except Exception as e:
            print(f"   ❌ Failed to create article: {e}")
            raise


# Global database handler instance
db_handler = MongoDBHandler()
