"""
Gemini AI Integration
Manages multiple API keys with rotation and provides AI analysis
"""

import json
import requests
from threading import Lock
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from typing import List, Dict, Optional

from .config import config


class GeminiAPIManager:
    """Manages multiple Gemini API keys with rotation"""
    
    def __init__(self, api_keys: List[str], tz: str = "Asia/Dhaka"):
        self.api_keys = api_keys or []
        self.models = [
            "gemini-2.5-flash-lite",
            "gemini-2.5-flash",
            "gemini-3-flash",
        ]
        self.current_index = 0
        self.lock = Lock()
        self.tz = ZoneInfo(tz)
        
        # key -> datetime until which it is disabled
        self.disabled_until: Dict[str, datetime] = {}
    
    def _now(self) -> datetime:
        return datetime.now(self.tz)
    
    def _is_disabled(self, key: str) -> bool:
        until = self.disabled_until.get(key)
        return until is not None and until > self._now()
    
    def disable_key_until_next_day(self, key: str) -> None:
        """Disable key until next day 00:00 (local tz)."""
        now = self._now()
        next_day_midnight = (now + timedelta(days=1)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        self.disabled_until[key] = next_day_midnight
    
    def get_all_keys(self) -> List[str]:
        return self.api_keys
    
    def get_all_models(self) -> List[str]:
        return self.models
    
    def get_next_key(self) -> str:
        """Return next available (not-disabled) key in round-robin order (thread-safe)."""
        with self.lock:
            if not self.api_keys:
                raise ValueError("No Gemini API keys configured")
            
            n = len(self.api_keys)
            
            # Try at most n keys to find a non-disabled one
            for _ in range(n):
                key = self.api_keys[self.current_index % n]
                self.current_index = (self.current_index + 1) % n
                
                if not self._is_disabled(key):
                    return key
            
            raise ValueError("All Gemini API keys are temporarily disabled")


# Initialize global manager
gemini_manager = GeminiAPIManager(config.GEMINI_API_KEYS)


def generate_summary_with_gemini(title: str, full_text: str) -> Dict:
    """Generate AI summary and analysis using Gemini API with key rotation"""
    
    prompt = f"""
You are a professional news analyst AI.

Analyze the following news and return ONLY a valid JSON object.
DO NOT add explanations, markdown, comments, or extra text.
STRICTLY follow the schema and rules.

General Rules:
- All summaries must be fact-based, neutral, and concise.
- If news language is Bangla, summary_60_bn must be Bangla and summary_60_en must be English.
- If news language is English, summary_60_en must be English and summary_60_bn must be Bangla.
- JSON must be valid and parsable.
- 3-4 MCQs must be relevant to the news content.

Fields Rules:
- category: one English word only (Politics, Sports, Tech, Crime, Economy, Entertainment, World, Health, Science, etc.)
- summary_60_bn: 55–60 words in strictly Bangla language
- summary_60_en: 55–60 words in English language
- importance: integer from 1 to 10
  - 1–3 = low public impact
  - 4–6 = moderate relevance
  - 7–8 = high national relevance
  - 9–10 = critical or major public impact
- clickbait_score: integer from 0 to 5
  - 0 = title fully accurate
  - 5 = highly misleading or exaggerated
- clickbait_reason: 8–15 words, English
- corrected_title:
  - If clickbait_score >= 3, provide a proper, factual title
  - If clickbait_score < 3, return an empty string ""
- keywords:
  - 2–4 main keywords
  - lowercase
  - no punctuation
  - array of strings
- mcqs:
  - 3–4 MCQs generated from the news
  - Each MCQ must have 4 options
  - Only one correct answer

MCQ Structure:
{{
  "question": "",
  "options": ["", "", "", ""],
  "correct_answer": ""
}}

Title:
"{title}"

News:
"{full_text}"

Return JSON in this EXACT format:
{{
  "category": "",
  "summary_60_bn": "",
  "summary_60_en": "",
  "importance": 0,
  "clickbait_score": 0,
  "clickbait_reason": "",
  "corrected_title": "",
  "keywords": [],
  "mcqs": []
}}
"""
    
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt}]
            }
        ]
    }
    
    models = gemini_manager.get_all_models()
    api_keys = gemini_manager.get_all_keys()
    
    if not api_keys:
        raise ValueError("No Gemini API keys configured")
    
    # Rotate keys in round-robin; for each key try all models
    for _ in range(len(api_keys)):
        key = gemini_manager.get_next_key()
        
        key_succeeded = False
        last_error: Optional[Exception] = None
        
        # For this key, try all models
        for model in models:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
                headers = {"x-goog-api-key": key, "Content-Type": "application/json"}
                
                response = requests.post(url, json=payload, headers=headers, timeout=60)
                response.raise_for_status()
                
                data = response.json()
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                clean_text = text.replace("```json", "").replace("```", "").strip()
                result = json.loads(clean_text)
                
                print(f"   ✓ AI analysis done (Model: {model}, Category: {result.get('category', 'N/A')})")
                key_succeeded = True
                return result
                
            except Exception as e:
                last_error = e
                print(f"   ⚠️  Model {model} failed: {e}")
                continue
        
        # If all models failed for this key -> disable until next day
        if not key_succeeded:
            gemini_manager.disable_key_until_next_day(key)
            print(f"   ⛔ Disabled key until next day (Dhaka time)")
    
    raise ValueError("All Gemini models and keys failed")
