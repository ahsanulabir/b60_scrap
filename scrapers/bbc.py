"""
BBC World News Scraper
Scrapes news from BBC World RSS feed
"""

import feedparser
from typing import List, Dict, Tuple

from utils import (
    config,
    fetch_url,
    parse_html,
    sleep_random,
    generate_summary_with_gemini,
    db_handler,
    send_to_telegram
)

RSS_URL = "https://feeds.bbci.co.uk/news/world/rss.xml"
SOURCE_NAME = "BBC News"


def get_article_image_content(url: str) -> Tuple[str, str]:
    """Extract image and content from BBC article"""
    try:
        html = fetch_url(url)
        if not html:
            return "NO IMAGE", "NO CONTENT"
        
        soup = parse_html(html)
        
        # Extract image
        image = soup.find('meta', property="og:image")
        image_url = image['content'] if image else "NO IMAGE"
        
        # Extract content from BBC's specific structure
        selector = "p.sc-9a00e533-0, h2.sc-f98b1ad2-0, li.sc-734a601e-0"
        raw_text = soup.select(selector)
        clean_text = [content.text.strip() for content in raw_text if content.text.strip()]
        full_text = "\n\n".join(clean_text) if clean_text else "NO CONTENT"
        
        return image_url, full_text
        
    except Exception as e:
        print(f"   ❌ Failed to extract content: {e}")
        return f"Error: {e}", f"Error: {e}"


def scrape_bbc() -> List[Dict]:
    """Main scraper function for BBC World"""
    print(f"\n🚀 Starting BBC World scraper...")
    print(f"📡 Fetching RSS feed: {RSS_URL}\n")
    
    try:
        feed = feedparser.parse(RSS_URL)
        articles = []
        processed_count = 0
        
        for entry in feed.entries:
            if processed_count >= config.MAX_ARTICLES:
                break
            
            # Skip video content
            if "/videos" in entry.link:
                print(f"⏭️  Skipping video: {entry.link}")
                continue
            
            title = entry.get("title", "")
            
            # Check if exists
            if db_handler.check_article_exists(entry.link):
                print(f"⏭️  Already exists: {title[:50]}...")
                continue
            
            print(f"\n📰 Processing [{processed_count + 1}]: {title[:60]}...")
            
            try:
                # Fetch full content and image
                print(f"   🔍 Fetching article content...")
                article_image, article_text = get_article_image_content(entry.link)
                
                article_data = {
                    "title": title,
                    "link": entry.link,
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
        print(f"✅ BBC World scraping completed!")
        print(f"📊 Total processed: {len(articles)} articles")
        print(f"{'='*60}\n")
        
        return articles
        
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}\n")
        raise
