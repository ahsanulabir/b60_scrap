"""
The Daily Star News Scraper
Scrapes news from The Daily Star website
"""

from datetime import datetime
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

BASE_URL = "https://www.thedailystar.net"
FEED_URL = "https://www.thedailystar.net/todays-news"
SOURCE_NAME = "The Daily Star"
MULTIMEDIA_URL = "multimedia/"


def get_list_articles(url: str) -> list:
    """Get list of article URLs from The Daily Star feed page"""
    try:
        html = fetch_url(url)
        if not html:
            return []
        
        soup = parse_html(html)
        contents = soup.find_all("h3", class_='title')
        links = []
        
        for content in contents:
            link_tag = content.find("a")
            if link_tag and link_tag.get("href"):
                link = BASE_URL + link_tag["href"]
                
                # Skip multimedia links
                if MULTIMEDIA_URL in link:
                    print(f"   ⏭️  Skipping multimedia: {link}")
                    continue
                
                links.append(link)
        
        print(f"   📋 Found {len(links)} article links")
        return links
        
    except Exception as e:
        print(f"   ❌ Failed to get article list: {e}")
        return []


def get_article_details(article_url: str) -> Dict:
    """Extract article details from The Daily Star article page"""
    try:
        html = fetch_url(article_url)
        if not html:
            return None
        
        soup = parse_html(html)
        
        # Extract title
        title_tag = soup.find("h1")
        title = title_tag.text.strip() if title_tag else "No Title"
        
        # Extract image
        image_url = extract_og_image(soup)
        
        # Extract content (paragraphs without classes)
        contents = soup.find_all('p', class_=False)
        article_text = [p.text.strip() for p in contents if p.text.strip()]
        full_text = "\n\n".join(article_text) if article_text else "NO CONTENT"
        
        return {
            "title": title,
            "link": article_url,
            "image": image_url,
            "full_text": full_text,
            "source": SOURCE_NAME,
            "published": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"   ❌ Failed to extract article details: {e}")
        return None


def scrape_dailystar() -> List[Dict]:
    """Main scraper function for The Daily Star"""
    print(f"\n🚀 Starting The Daily Star scraper...")
    print(f"📡 Fetching feed: {FEED_URL}\n")
    
    try:
        # Get article links
        article_links = get_list_articles(FEED_URL)
        articles = []
        processed_count = 0
        
        for article_url in article_links[:config.MAX_ARTICLES]:
            # Check if exists
            if db_handler.check_article_exists(article_url):
                print(f"⏭️  Already exists: {article_url}")
                continue
            
            print(f"\n📰 Processing [{processed_count + 1}]: {article_url}")
            
            try:
                # Get article details
                print(f"   🔍 Fetching article content...")
                article_data = get_article_details(article_url)
                
                if not article_data:
                    continue
                
                # Generate AI summary
                print(f"   🤖 Generating AI analysis...")
                ai_analysis = generate_summary_with_gemini(
                    article_data["title"],
                    article_data["full_text"]
                )
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
        print(f"✅ The Daily Star scraping completed!")
        print(f"📊 Total processed: {len(articles)} articles")
        print(f"{'='*60}\n")
        
        return articles
        
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}\n")
        raise
