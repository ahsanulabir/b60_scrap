"""
Bangladesh News Scraper - Main Controller
Orchestrates all news scrapers and manages execution
"""

import json
import argparse
from datetime import datetime
from typing import List, Dict

from scrapers import SCRAPERS
from utils import config


def run_scraper(scraper_name: str) -> Dict:
    """Run a single scraper by name"""
    if scraper_name not in SCRAPERS:
        print(f"❌ Unknown scraper: {scraper_name}")
        print(f"Available scrapers: {', '.join(SCRAPERS.keys())}")
        return {"scraper": scraper_name, "status": "error", "articles": []}
    
    try:
        scraper_func = SCRAPERS[scraper_name]
        articles = scraper_func()
        
        return {
            "scraper": scraper_name,
            "status": "success",
            "articles": articles,
            "count": len(articles)
        }
    except Exception as e:
        print(f"❌ Scraper {scraper_name} failed: {e}")
        return {
            "scraper": scraper_name,
            "status": "error",
            "articles": [],
            "error": str(e)
        }


def run_all_available_scrapers() -> Dict:
    """Run all available scrapers"""
    print("="*70)
    print("🚀 STARTING ALL NEWS SCRAPERS")
    print("="*70)
    
    results = {}
    
    for idx, (name, scraper_func) in enumerate(SCRAPERS.items(), 1):
        try:
            print(f"\n\n[{idx}/{len(SCRAPERS)}] Running {name.upper()} Scraper...")
            articles = scraper_func()
            results[name] = {
                "status": "success",
                "articles": articles,
                "count": len(articles)
            }
            
            # Save individual results
            output_file = f"{name}_articles.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(articles, f, ensure_ascii=False, indent=2)
            
        except Exception as e:
            print(f"❌ {name} failed: {e}")
            results[name] = {
                "status": "error",
                "articles": [],
                "count": 0,
                "error": str(e)
            }
    
    # Print summary
    print("\n\n" + "="*70)
    print("✅ ALL SCRAPERS COMPLETED!")
    print("="*70)
    print("\n📊 SUMMARY:")
    
    total_articles = 0
    for name, result in results.items():
        count = result.get("count", 0)
        status = "✓" if result["status"] == "success" else "✗"
        print(f"   {status} {name:20} {count} articles")
        total_articles += count
    
    print(f"\n   🎯 TOTAL: {total_articles} articles processed")
    print("="*70)
    
    # Save combined results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    combined_file = f"all_scrapers_results_{timestamp}.json"
    
    with open(combined_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n📁 Combined results saved to: {combined_file}")
    
    return results


def run_enabled_scrapers() -> Dict:
    """Run only enabled scrapers (prothomalo and jagonews24)"""
    # Only these scrapers will run by default
    ENABLED_SCRAPERS = ['prothomalo', 'jagonews24']
    
    print("="*70)
    print("🚀 STARTING ENABLED NEWS SCRAPERS")
    print(f"📋 Running: {', '.join(ENABLED_SCRAPERS)}")
    print("="*70)
    
    results = {}
    
    for idx, name in enumerate(ENABLED_SCRAPERS, 1):
        scraper_func = SCRAPERS.get(name)
        if not scraper_func:
            print(f"⚠️  Scraper '{name}' not found, skipping...")
            continue
        try:
            print(f"\n\n[{idx}/{len(ENABLED_SCRAPERS)}] Running {name.upper()} Scraper...")
            articles = scraper_func()
            results[name] = {
                "status": "success",
                "articles": articles,
                "count": len(articles)
            }
            
            # Save individual results
            output_file = f"{name}_articles.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(articles, f, ensure_ascii=False, indent=2)
            
        except Exception as e:
            print(f"❌ {name} failed: {e}")
            results[name] = {
                "status": "error",
                "articles": [],
                "count": 0,
                "error": str(e)
            }
    
    # Print summary
    print("\n\n" + "="*70)
    print("✅ ENABLED SCRAPERS COMPLETED!")
    print("="*70)
    print("\n📊 SUMMARY:")
    
    total_articles = 0
    for name, result in results.items():
        count = result.get("count", 0)
        status = "✓" if result["status"] == "success" else "✗"
        print(f"   {status} {name:20} {count} articles")
        total_articles += count
    
    print(f"\n   🎯 TOTAL: {total_articles} articles processed")
    print("="*70)
    
    # Save combined results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    combined_file = f"enabled_scrapers_results_{timestamp}.json"
    
    with open(combined_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n📁 Combined results saved to: {combined_file}")
    
    return results


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Bangladesh News Scraper - Multi-source news aggregator with AI analysis"
    )
    
    parser.add_argument(
        '--scraper',
        '-s',
        type=str,
        help=f"Run specific scraper. Options: {', '.join(SCRAPERS.keys())}, all"
    )
    
    parser.add_argument(
        '--list',
        '-l',
        action='store_true',
        help="List all available scrapers"
    )
    
    args = parser.parse_args()
    
    # Validate configuration
    if not config.validate():
        print("\n❌ Configuration validation failed. Please check your environment variables.")
        return
    
    # List scrapers
    if args.list:
        print("\n📋 Available Scrapers:")
        for idx, name in enumerate(SCRAPERS.keys(), 1):
            print(f"   {idx}. {name}")
        print("\nUsage:")
        print("  python main.py --scraper <name>  # Run specific scraper")
        print("  python main.py --scraper all     # Run all scrapers")
        return
    
    # Run specific scraper
    if args.scraper:
        if args.scraper.lower() == 'all':
            # Run ALL scrapers (kept for manual use)
            run_all_available_scrapers()
        else:
            result = run_scraper(args.scraper.lower())
            
            # Save results
            if result["status"] == "success":
                output_file = f"{args.scraper}_articles.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(result["articles"], f, ensure_ascii=False, indent=2)
                print(f"\n📁 Results saved to: {output_file}")
    else:
        # Default: run only enabled scrapers
        run_enabled_scrapers()


if __name__ == "__main__":
    main()
