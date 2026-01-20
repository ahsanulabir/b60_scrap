"""
BD Pratidin News Scraper
Scrapes news from BD Pratidin RSS feed
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

RSS_URL = "https://www.bd-pratidin.com/rss.xml"
SOURCE_NAME = "BD Pratidin"


def get_article_content(article_url: str) -> str:
    """Extract full article content from BD Pratidin"""
    try:
        html = fetch_url(article_url)
        if not html:
            return "NO CONTENT"
        
        soup = parse_html(html)
        
        content = soup.find("article")
        if content is not None:
            content_array = content.find_all("p")
            text_array = [p.text.strip() for p in content_array if p.text.strip()]
            full_text = "\n\n".join(text_array)
            return full_text if full_text else "NO CONTENT"
        
        return "NO CONTENT"
        
    except Exception as e:
        print(f"   ❌ Failed to extract content: {e}")
        return f"Error: {e}"


def scrape_bdpratidin() -> List[Dict]:
    """Main scraper function for BD Pratidin"""
    print(f"\n🚀 Starting BD Pratidin scraper...")
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
            image_link = entry.guid
            
            # Check if exists
            if db_handler.check_article_exists(entry_link):
                print(f"⏭️  Already exists: {title[:50]}...")
                continue
            
            print(f"\n📰 Processing [{processed_count + 1}]: {title[:60]}...")
            
            try:
                # Build initial article data
                article_data = {
                    "title": title,
                    "link": entry_link,
                    "image": image_link,
                    "full_text": entry.get("summary", entry.get("description", "")),
                    "source": SOURCE_NAME,
                    "published": entry.get("published", "")
                }
                
                # Fetch full content
                print(f"   🔍 Fetching article content...")
                full_text = get_article_content(entry_link)
                article_data["full_text"] = full_text
                
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
        print(f"✅ BD Pratidin scraping completed!")
        print(f"📊 Total processed: {len(articles)} articles")
        print(f"{'='*60}\n")
        
        return articles
        
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}\n")
        raise
