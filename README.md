# 🌐 Bangladesh News Scraper

**Automated multi-source news aggregator with AI-powered analysis**

[![GitHub Actions](https://img.shields.io/badge/GitHub-Actions-2088FF?logo=github-actions&logoColor=white)](https://github.com/features/actions)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![MongoDB](https://img.shields.io/badge/MongoDB-47A248?logo=mongodb&logoColor=white)](https://www.mongodb.com/)

## 📰 Supported News Sources

| #   | Source         | Language   | Type         |
| --- | -------------- | ---------- | ------------ |
| 1   | Prothom Alo    | 🇧🇩 Bangla  | RSS          |
| 2   | The Daily Star | 🇬🇧 English | Web Scraping |
| 3   | TBS News       | 🇬🇧 English | RSS          |
| 4   | BD Pratidin    | 🇧🇩 Bangla  | RSS          |
| 5   | BBC World      | 🇬🇧 English | RSS          |
| 6   | Jago News 24   | 🇧🇩 Bangla  | RSS          |
| 7   | Bangla Tribune | 🇧🇩 Bangla  | RSS          |
| 8   | BD24Live       | 🇧🇩 Bangla  | RSS          |

## ✨ Features

- ✅ **Multi-source scraping** from 8 major news outlets
- ✅ **AI-powered analysis** using Google Gemini
- ✅ **Automatic duplicate detection**
- ✅ **Direct MongoDB integration**
- ✅ **Telegram notifications** (optional)
- ✅ **Bangla & English support**
- ✅ **Clickbait detection & correction**
- ✅ **MCQ generation** from news articles
- ✅ **Category classification**
- ✅ **Importance scoring** (1-10)
- ✅ **60-word summaries** in both languages
- ✅ **GitHub Actions** for automated scheduling

## 🚀 Quick Start

### Local Development

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/bangladesh-news-scraper.git
   cd bangladesh-news-scraper
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**

   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

4. **Run scrapers**

   ```bash
   # Run all scrapers
   python main.py

   # Run specific scraper
   python main.py --scraper prothomalo

   # List available scrapers
   python main.py --list
   ```

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# MongoDB (Required)
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/database
MONGODB_DATABASE=briefly60

# Gemini API (Required - comma-separated for multiple keys)
GEMINI_API_KEYS=key1,key2,key3

# Telegram (Optional)
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# Scraper Settings
MAX_ARTICLES=10
REQUEST_TIMEOUT=30
```

### GitHub Actions Setup

1. **Add GitHub Secrets**
   - Go to Settings → Secrets and variables → Actions
   - Add these secrets:
     - `MONGODB_URI`
     - `MONGODB_DATABASE`
     - `GEMINI_API_KEYS`
     - `TELEGRAM_BOT_TOKEN` (optional)
     - `TELEGRAM_CHAT_ID` (optional)

2. **Configure Schedule**
   - Edit `.github/workflows/scraper.yml`
   - Default: Runs every 6 hours
   - Cron format: `'0 */6 * * *'`

3. **Manual Trigger**
   - Go to Actions → News Scraper Cron Job
   - Click "Run workflow"
   - Select specific scraper or run all

## 📁 Project Structure

```
bangladesh-news-scraper/
├── scrapers/              # Individual scraper modules
│   ├── __init__.py
│   ├── prothomalo.py
│   ├── dailystar.py
│   ├── tbs.py
│   ├── bdpratidin.py
│   ├── bbc.py
│   ├── jagonews24.py
│   ├── bangla_tribune.py
│   └── bd24live.py
├── utils/                 # Utility modules
│   ├── __init__.py
│   ├── config.py          # Configuration management
│   ├── helpers.py         # Helper functions
│   ├── gemini_ai.py       # AI integration
│   ├── database.py        # MongoDB operations
│   └── telegram.py        # Telegram notifications
├── .github/
│   └── workflows/
│       └── scraper.yml    # GitHub Actions workflow
├── main.py               # Main controller
├── requirements.txt      # Python dependencies
├── .env.example         # Environment template
└── README.md            # This file
```

## 🎯 Usage Examples

### Run All Scrapers

```bash
python main.py
# or
python main.py --scraper all
```

### Run Specific Scraper

```bash
python main.py --scraper prothomalo
python main.py --scraper dailystar
python main.py --scraper bbc
```

### List Available Scrapers

```bash
python main.py --list
```

## 📊 Output Format

Each article is saved with the following structure:

```json
{
  "title": "Article title",
  "corrected_title": "Corrected title if clickbait",
  "source": "News source name",
  "source_url": "Article URL",
  "content": "Full article text",
  "banner": "Image URL",
  "published_at": "2024-01-20T10:00:00+06:00",
  "category": "Politics",
  "summary_60_bn": "60-word Bangla summary",
  "summary_60_en": "60-word English summary",
  "importance": 8,
  "clickbait_score": 2,
  "clickbait_reason": "Reason if clickbait detected",
  "keywords": ["keyword1", "keyword2"],
  "quiz_questions": [
    {
      "question": "Quiz question",
      "options": ["A", "B", "C", "D"],
      "correct_answer": "A"
    }
  ]
}
```

## 🔄 Automation

### GitHub Actions Workflow

The scraper runs automatically via GitHub Actions:

- **Schedule**: Every 6 hours (customizable)
- **Manual trigger**: Available via Actions tab
- **Artifact storage**: Results saved for 7 days
- **Environment**: Ubuntu latest with Python 3.11

### Cron Schedule Examples

```yaml
# Every 6 hours
- cron: "0 */6 * * *"

# Every day at 9 AM UTC
- cron: "0 9 * * *"

# Every hour
- cron: "0 * * * *"

# Every 30 minutes
- cron: "*/30 * * * *"
```

## 🛠️ Development

### Adding a New Scraper

1. Create a new file in `scrapers/` (e.g., `newsource.py`)
2. Implement the scraping function following this template:

```python
from typing import List, Dict
from utils import (
    config,
    fetch_url,
    parse_html,
    generate_summary_with_gemini,
    db_handler,
    send_to_telegram
)

def scrape_newsource() -> List[Dict]:
    """Scraper for New Source"""
    # Implementation here
    pass
```

3. Register in `scrapers/__init__.py`:

```python
from .newsource import scrape_newsource

SCRAPERS = {
    # ... existing scrapers
    'newsource': scrape_newsource,
}
```

## 📝 Requirements

- Python 3.11+
- MongoDB database
- Google Gemini API keys
- Telegram Bot (optional)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- News sources for providing RSS feeds
- Google Gemini for AI analysis
- MongoDB for database services
- GitHub Actions for automation

## 📧 Contact

For issues and questions, please open an issue on GitHub.

---

**Made with ❤️ for Bangladesh News Aggregation**
