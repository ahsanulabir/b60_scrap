"""
Telegram Integration
Send notifications to Telegram channel
"""

import requests
from typing import Dict

from .config import config


def send_to_telegram(article_data: Dict) -> bool:
    """Send article notification to Telegram"""
    bot_token = config.TELEGRAM_BOT_TOKEN
    chat_id = config.TELEGRAM_CHAT_ID
    
    # Skip if Telegram not configured
    if not bot_token or not chat_id:
        print("   ⏭️  Telegram not configured - skipping notification")
        return False
    
    try:
        banner = article_data.get("image", "")
        source_name = article_data.get("source", "")
        title = article_data.get("title", "")
        summary_bn = article_data.get("summary_60_bn", "")
        category = article_data.get("category", "").lower()
        
        # Prepare caption
        caption = f"📰 *{title}*\n\n"
        caption += f"📌 {source_name}\n\n"
        caption += f"{summary_bn}\n\n"
        caption += f"#{category}"
        
        # Send with image if available
        if banner and banner != "NO IMAGE":
            # Send photo with caption
            url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
            payload = {
                "chat_id": chat_id,
                "photo": banner,
                "caption": caption,
                "parse_mode": "Markdown"
            }
        else:
            # Send text message only
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": caption,
                "parse_mode": "Markdown"
            }
        
        response = requests.post(url, json=payload, timeout=config.REQUEST_TIMEOUT)
        response.raise_for_status()
        
        print(f"   ✓ Sent to Telegram")
        return True
        
    except Exception as e:
        print(f"   ⚠️  Telegram notification failed: {e}")
        return False
