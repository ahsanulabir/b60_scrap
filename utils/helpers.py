"""
Utility Helper Functions
Common functions used across all scrapers
"""

import time
import random
import requests
from datetime import datetime, timedelta
from typing import Optional
from bs4 import BeautifulSoup

from .config import config


def sleep_random(min_seconds: float = 2, max_seconds: float = 6):
    """Random sleep to avoid rate limiting"""
    delay = random.uniform(min_seconds, max_seconds)
    time.sleep(delay)


def fetch_url(url: str, max_retries: int = 3) -> Optional[str]:
    """Fetch URL with retry logic"""
    headers = {'User-Agent': config.USER_AGENT}
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, timeout=config.REQUEST_TIMEOUT)
            response.raise_for_status()
            return response.text
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"⚠️  Retry {attempt + 1}/{max_retries} for {url}: {e}")
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                print(f"❌ Failed to fetch {url}: {e}")
                return None


def parse_html(html_content: str) -> BeautifulSoup:
    """Parse HTML content"""
    return BeautifulSoup(html_content, 'html.parser')


def extract_og_image(soup: BeautifulSoup) -> str:
    """Extract Open Graph image from HTML"""
    og_image = soup.find("meta", property="og:image")
    if og_image and og_image.get("content"):
        return og_image["content"]
    return "NO IMAGE"


def extract_paragraphs(soup: BeautifulSoup) -> str:
    """Extract all paragraphs from HTML"""
    paragraphs = soup.find_all("p")
    text_array = [p.text.strip() for p in paragraphs if p.text.strip()]
    return "\n\n".join(text_array) if text_array else "NO CONTENT"


def convert_to_utc_plus_6(published_date: str) -> str:
    """Convert date to UTC+6 timezone"""
    try:
        if 'T' in published_date and 'Z' in published_date:
            date = datetime.fromisoformat(published_date.replace('Z', '+00:00'))
        else:
            date = datetime.strptime(published_date, "%a, %d %b %Y %H:%M:%S %z")
        
        if date.utcoffset().total_seconds() != 6 * 3600:
            utc_plus_6 = date + timedelta(hours=6)
        else:
            utc_plus_6 = date
        
        return utc_plus_6.isoformat()
    except Exception as e:
        print(f"⚠️  Date conversion error: {e}")
        return datetime.now().isoformat()
