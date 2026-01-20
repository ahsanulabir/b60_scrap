"""
Jago News 24 Scraper
Scrapes news from Jago News 24 RSS feed
"""

import feedparser
from typing import List, Dict

from utils import (
    config,
    sleep_random,
    generate_summary_with_gemini,
    db_handler,
    send_to_telegram
)

RSS_URL = "https://www.jagonews24.com/rss/rss.xml"
SOURCE_NAME = "Jago News 24"


def scrape_jagonews24() -> List[Dict]:
    """Main scraper function for Jago News 24"""
    print(f"\n🚀 Starting Jago News 24 scraper...")
    print(f"📡 Fetching RSS feed: {RSS_URL}\n")
    
    try:
        feed = feedparser.parse(RSS_URL)
        articles = []
        processed_count = 0
        
        for entry in feed.entries:
            if processed_count >= config.MAX_ARTICLES:
                break
            
            title = entry.get("title", "")
            link = entry.get("link", "")
            
            # Check if exists
            if db_handler.check_article_exists(link):
                print(f"⏭️  Already exists: {title[:50]}...")
                continue
            
            print(f"\n📰 Processing [{processed_count + 1}]: {title[:60]}...")
            
            try:
                # Extract image from media_content
                imglist = entry.get("media_content", [])
                image_url = imglist[0].get("url") if imglist else "NO IMAGE"
                
                article_data = {
                    "title": title,
                    "link": link,
                    "image": image_url,
                    "full_text": entry.get("summary", entry.get("description", "")),
                    "source": SOURCE_NAME,
                    "published": entry.get("published", "")
                }
                
                # Generate AI summary
                print(f"   🤖 Generating AI analysis...")
                ai_analysis = generate_summary_with_gemini(title, article_data["full_text"])
                article_data.update(ai_analysis)
                
                # Save to MongoDB
                print(f"   💾 Saving to MongoDB...")
                db_handler.create_article(article_data)
                
                # Send to Telegram
                print(f"   📱 Sending to Telegram...")
                send_to_telegram(article_data)
                
                articles.append(article_data)
                processed_count += 1
                
                print(f"   ✅ SUCCESS - Article processed!\n")
                sleep_random(2, 6)
                
            except Exception as e:
                print(f"   ❌ ERROR: {e}\n")
                continue
        
        print(f"\n{'='*60}")
        print(f"✅ Jago News 24 scraping completed!")
        print(f"📊 Total processed: {len(articles)} articles")
        print(f"{'='*60}\n")
        
        return articles
        
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}\n")
        raise
