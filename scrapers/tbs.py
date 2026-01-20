"""
TBS (The Business Standard) News Scraper
Scrapes news from TBS RSS feed
"""

import feedparser
from typing import List, Dict

from utils import (
    config,
    fetch_url,
    parse_html,
    sleep_random,
    generate_summary_with_gemini,
    db_handler,
    send_to_telegram
)

RSS_URL = "https://www.tbsnews.net/top-news/rss.xml"
SOURCE_NAME = "The Business Standard"


def get_text(url: str) -> str:
    """Extract full text from TBS article page"""
    try:
        html = fetch_url(url)
        if not html:
            return "NO CONTENT"
        
        soup = parse_html(html)
        
        # TBS uses specific classes for content
        selector = "p.rtejustify, li.rtejustify"
        raw_text = soup.select(selector)
        
        article_text = [data.text.strip() for data in raw_text if data.text.strip()]
        full_text = '\n\n'.join(article_text)
        
        return full_text if full_text else "NO CONTENT"
        
    except Exception as e:
        print(f"   ❌ Failed to extract text: {e}")
        return f"Error: {e}"


def scrape_tbs() -> List[Dict]:
    """Main scraper function for TBS News"""
    print(f"\n🚀 Starting TBS News scraper...")
    print(f"📡 Fetching RSS feed: {RSS_URL}\n")
    
    try:
        feed = feedparser.parse(RSS_URL)
        articles = []
        processed_count = 0
        
        for entry in feed.entries:
            if processed_count >= config.MAX_ARTICLES:
                break
            
            title = entry.get("title", "")
            entry_link = entry.link
            
            # Check if exists
            if db_handler.check_article_exists(entry_link):
                print(f"⏭️  Already exists: {title[:50]}...")
                continue
            
            print(f"\n📰 Processing [{processed_count + 1}]: {title[:60]}...")
            
            try:
                # Extract image from media_content
                image_details = entry.get("media_content", "")
                image_url = image_details[0].get("url", "NO IMAGE") if image_details else "NO IMAGE"
                
                # Fetch full text
                print(f"   🔍 Fetching article content...")
                full_text = get_text(entry_link)
                
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
                sleep_random(2, 6)
                
            except Exception as e:
                print(f"   ❌ ERROR: {e}\n")
                continue
        
        print(f"\n{'='*60}")
        print(f"✅ TBS News scraping completed!")
        print(f"📊 Total processed: {len(articles)} articles")
        print(f"{'='*60}\n")
        
        return articles
        
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}\n")
        raise
