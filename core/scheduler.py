"""Main scheduler loop: ingestion → classification → dedup → draft generation."""
import asyncio
import time
import schedule
from datetime import datetime
from core.ingestion.rss_fetcher import RSSFetcher
from core.ingestion.reddit_fetcher import RedditFetcher
from core.ingestion.google_news_fetcher import GoogleNewsFetcher
from core.ingestion.api_football_fetcher import APIFootballFetcher
from datetime import datetime, timedelta
from core.generation.queue_manager import process_item
from core.analytics.engine import run_weekly_analytics

MAX_ITEMS_PER_SOURCE = 5
MAX_LLM_CALLS_PER_CYCLE = 10

RELEVANCE_KEYWORDS = {
    "goal", "transfer", "sign", "deal", "rumour", "injury", "manager",
    "sack", "appoint", "champion", "relegation", "promotion",
    "var", "red card", "yellow card", "hattrick", "brace", "derby",
    "el clasico", "classique", "rival", "record", "stats",
    "premier league", "la liga", "serie a", "bundesliga", "ligue 1",
    "champions league", "europa league", "fa cup", "copa del rey",
    "world cup", "euro", "copa america", "afcon"
}

MAX_AGE_HOURS = 12  # hours

def is_relevant(title: str) -> bool:
    title_lower = title.lower()
    return any(kw in title_lower for kw in RELEVANCE_KEYWORDS)

async def fetch_all_and_process():
    fetchers = [
        ("RSS", RSSFetcher()),
        ("Reddit", RedditFetcher()),
        ("Google News", GoogleNewsFetcher()),
        ("API-Football", APIFootballFetcher()),
    ]
    llm_calls = 0
    for name, fetcher in fetchers:
        if llm_calls >= MAX_LLM_CALLS_PER_CYCLE:
            print("  ⚠️ Reached cycle LLM call limit. Skipping remaining fetchers.")
            break
        print(f"Fetching {name}...")
        items = await fetcher.fetch()
        print(f"  {name}: got {len(items)} items")
        relevant = [item for item in items if is_relevant(item.title) and item.published > datetime.utcnow() - timedelta(hours=MAX_AGE_HOURS)]
        print(f"  {name}: {len(relevant)} relevant items, processing first {min(MAX_ITEMS_PER_SOURCE, len(relevant))}")
        for item in relevant[:MAX_ITEMS_PER_SOURCE]:
            if llm_calls >= MAX_LLM_CALLS_PER_CYCLE:
                print("  ⚠️ Reached cycle LLM call limit. Stopping.")
                break
            await process_item(item)
            llm_calls += 3

def job():
    print("\n⏰ Running scheduled job...")
    try:
        asyncio.run(fetch_all_and_process())
        print("✅ Job completed.")
    except Exception as e:
        print(f"❌ Job failed: {e}")

def analytics_job():
    print("📊 Running weekly analytics...")
    run_weekly_analytics()
    print("✅ Analytics complete.")

def main():
    schedule.every(10).minutes.do(job)
    schedule.every().monday.at("02:00").do(analytics_job)
    print("Scheduler started — news every 10 min, analytics on Monday 02:00.")
    job()
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()
