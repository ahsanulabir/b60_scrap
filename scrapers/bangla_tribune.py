"""
Bangla Tribune News Scraper
Scrapes news from Bangla Tribune RSS feed
"""

import feedparser
import curl_cffi
from typing import List, Dict, Tuple

from utils import (
    config,
    parse_html,
    sleep_random,
    generate_summary_with_gemini,
    db_handler,
    send_to_telegram
)

RSS_URL = "https://www.banglatribune.com/feed/"
SOURCE_NAME = "Bangla Tribune"


def get_article_image_fulltext(url: str) -> Tuple[str, str]:
    """Extract image and full text from Bangla Tribune article"""
    try:
        response = curl_cffi.requests.get(url, impersonate='safari260')
        html = response.content
        if not html:
            return "NO IMAGE", "NO CONTENT"
        
        soup = parse_html(html)
        
        # Extract image
        image = soup.find("meta", property="og:image")
        image_url = image["content"] if image else "NO IMAGE"
        
        # Extract content
        raw_text = soup.find_all('p', class_='alignfull')
        clean_text = [p.text.strip() for p in raw_text if p.text.strip()]
        full_text = '\n\n'.join(clean_text) if clean_text else "NO CONTENT"
        
        return image_url, full_text
        
    except Exception as e:
        print(f"   ❌ Failed to extract content: {e}")
        return "Error", f"Error: {e}"


def scrape_bangla_tribune() -> List[Dict]:
    """Main scraper function for Bangla Tribune"""
    print(f"\n🚀 Starting Bangla Tribune scraper...")
    print(f"📡 Fetching RSS feed: {RSS_URL}\n")
    
    try:
        feed = feedparser.parse(RSS_URL)
        articles = []
        processed_count = 0
        
        for entry in feed.entries:
            if processed_count >= config.MAX_ARTICLES:
                break
            
            title = entry.get("title", "")
            entry_link = entry.get("link", "")
            
            # Check if exists
            if db_handler.check_article_exists(entry_link):
                print(f"⏭️  Already exists: {title[:50]}...")
                continue
            
            print(f"\n📰 Processing [{processed_count + 1}]: {title[:60]}...")
            
            try:
                # Fetch content and image
                print(f"   🔍 Fetching article content...")
                article_image, article_text = get_article_image_fulltext(entry_link)
                
                article_data = {
                    "title": title,
                    "link": entry_link,
                    "image": article_image,
                    "full_text": article_text,
                    "source": SOURCE_NAME,
                    "published": entry.get("published", "")
                }
                
                # Generate AI summary
                print(f"   🤖 Generating AI analysis...")
                ai_analysis = generate_summary_with_gemini(title, article_text)
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
        print(f"✅ Bangla Tribune scraping completed!")
        print(f"📊 Total processed: {len(articles)} articles")
        print(f"{'='*60}\n")
        
        return articles
        
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}\n")
        raise
