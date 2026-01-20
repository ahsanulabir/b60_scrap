"""
BD24Live Bangla News Scraper
Scrapes news from BD24Live Bangla RSS feed
"""

import feedparser
from typing import List, Dict

from utils import (
    config,
    fetch_url,
    parse_html,
    extract_og_image,
    sleep_random,
    generate_summary_with_gemini,
    db_handler,
    send_to_telegram
)

RSS_URL = "https://www.bd24live.com/bangla/feed/"
SOURCE_NAME = "BD24Live Bangla"


def get_main_image(article_url: str) -> str:
    """Extract main image from BD24Live article page"""
    try:
        html = fetch_url(article_url)
        if not html:
            return "NO IMAGE"
        
        soup = parse_html(html)
        
        # Method 1: Check Open Graph Meta Tags
        image_url = extract_og_image(soup)
        if image_url != "NO IMAGE":
            return image_url
        
        # Method 2: Check for featured image containers
        featured_div = soup.find("div", class_="post-image") or soup.find("div", class_="post-thumbnail")
        if featured_div:
            img_tag = featured_div.find("img")
            if img_tag and img_tag.get("src"):
                return img_tag["src"]
        
        return "NO IMAGE"
        
    except Exception as e:
        print(f"   ❌ Failed to extract image: {e}")
        return f"Error: {e}"


def scrape_bd24live() -> List[Dict]:
    """Main scraper function for BD24Live Bangla"""
    print(f"\n🚀 Starting BD24Live Bangla scraper...")
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
                article_data = {
                    "title": title,
                    "link": entry_link,
                    "image": "",
                    "full_text": entry.get("description", ""),
                    "source": SOURCE_NAME,
                    "published": entry.get("published", "")
                }
                
                # Fetch main image
                print(f"   🔍 Fetching article image...")
                article_data["image"] = get_main_image(entry_link)
                
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
        print(f"✅ BD24Live Bangla scraping completed!")
        print(f"📊 Total processed: {len(articles)} articles")
        print(f"{'='*60}\n")
        
        return articles
        
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}\n")
        raise
