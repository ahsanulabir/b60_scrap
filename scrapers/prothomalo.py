"""
Prothom Alo News Scraper
Scrapes news from Prothom Alo RSS feed
"""

import feedparser
from typing import List, Dict, Tuple

from utils import (
    config,
    fetch_url,
    parse_html,
    extract_og_image,
    extract_paragraphs,
    sleep_random,
    generate_summary_with_gemini,
    db_handler,
    send_to_telegram
)

RSS_URL = "https://prod-qt-images.s3.amazonaws.com/production/prothomalo-bangla/feed.xml"
SOURCE_NAME = "Prothom Alo"
VIDEO_SUBSTRING = "https://www.prothomalo.com/video"
PHOTO_SUBSTRING = "https://www.prothomalo.com/photo"


def get_image_and_content(article_url: str) -> Tuple[str, str]:
    """Extract image and content from article page"""
    try:
        html = fetch_url(article_url)
        if not html:
            return "NO IMAGE", "NO CONTENT"
        
        soup = parse_html(html)
        image_url = extract_og_image(soup)
        full_article = extract_paragraphs(soup)
        
        return image_url, full_article
    except Exception as e:
        print(f"   ❌ Failed to extract content: {e}")
        return "Error", "Error"


def scrape_prothomalo() -> List[Dict]:
    """Main scraper function"""
    print(f"\n🚀 Starting Prothom Alo scraper...")
    print(f"📡 Fetching RSS feed: {RSS_URL}\n")
    
    try:
        feed = feedparser.parse(RSS_URL)
        articles = []
        processed_count = 0
        
        for entry in feed.entries:
            if processed_count >= config.MAX_ARTICLES:
                break
            
            entry_link = entry.get("link", "")
            
            # Skip videos and photos
            if VIDEO_SUBSTRING in entry_link or PHOTO_SUBSTRING in entry_link:
                print(f"⏭️  Skipping video/photo: {entry_link}")
                continue
            
            title = entry.get("title", "")
            
            # Check if exists
            if db_handler.check_article_exists(entry_link):
                print(f"⏭️  Already exists: {title[:50]}...")
                continue
            
            print(f"\n📰 Processing [{processed_count + 1}]: {title[:60]}...")
            
            try:
                # Fetch content
                print(f"   🔍 Fetching article content...")
                image_url, full_text = get_image_and_content(entry_link)
                
                article_data = {
                    "title": title,
                    "link": entry_link,
                    "image": image_url,
                    "full_text": full_text,
                    "source": SOURCE_NAME,
                    "published": entry.get("published", "")
                }
                
                # Generate AI summary
                print(f"   🤖 Generating AI analysis...")
                ai_analysis = generate_summary_with_gemini(title, full_text)
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
                
                # Random delay
                sleep_random(2, 6)
                
            except Exception as e:
                print(f"   ❌ ERROR: {e}\n")
                continue
        
        print(f"\n{'='*60}")
        print(f"✅ Scraping completed!")
        print(f"📊 Total processed: {len(articles)} articles")
        print(f"{'='*60}\n")
        
        return articles
        
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}\n")
        raise
