"""Main scheduler loop: ingestion → classification → dedup → draft generation."""
import asyncio
import time
import schedule
import random
from datetime import datetime, timedelta
from core.ingestion.rss_fetcher import RSSFetcher
from core.ingestion.reddit_fetcher import RedditFetcher
from core.ingestion.google_news_fetcher import GoogleNewsFetcher
from core.ingestion.api_football_fetcher import APIFootballFetcher
from core.ingestion.espn_fetcher import ESPNFetcher
from core.generation.queue_manager import process_item
from core.analytics.engine import run_weekly_analytics

MAX_ITEMS_PER_SOURCE = 5
MAX_LLM_CALLS_PER_CYCLE = 6
MAX_AGE_HOURS = 12  # hours

RELEVANCE_KEYWORDS = {
    "goal", "transfer", "sign", "deal", "rumour", "injury", "manager",
    "sack", "appoint", "champion", "relegation", "promotion",
    "var", "red card", "yellow card", "hattrick", "brace", "derby",
    "el clasico", "classique", "rival", "record", "stats",
    "premier league", "la liga", "serie a", "bundesliga", "ligue 1",
    "champions league", "europa league", "fa cup", "copa del rey",
    "world cup", "euro", "copa america", "afcon"
}

def is_relevant(title: str) -> bool:
    title_lower = title.lower()
    return any(kw in title_lower for kw in RELEVANCE_KEYWORDS)

async def fetch_all_and_process():
    fetchers = [
        ("RSS", RSSFetcher()),
        ("Reddit", RedditFetcher()),
        ("Google News", GoogleNewsFetcher()),
        ("API-Football", APIFootballFetcher()),
        ("ESPN", ESPNFetcher()),
    ]
    llm_calls = 0
    now = datetime.utcnow()
    age_cutoff = now - timedelta(hours=MAX_AGE_HOURS)
    for name, fetcher in fetchers:
        if llm_calls >= MAX_LLM_CALLS_PER_CYCLE:
            print("  ⚠️ Reached cycle LLM call limit. Skipping remaining fetchers.")
            break
        print(f"Fetching {name}...")
        items = await fetcher.fetch()
        print(f"  {name}: got {len(items)} items")
        # 1. Remove items older than MAX_AGE_HOURS
        fresh_items = [item for item in items if item.published and item.published > age_cutoff]
        print(f"  {name}: {len(fresh_items)} fresh items (within {MAX_AGE_HOURS}h)")
        # 2. Apply relevance filter
        relevant = [item for item in fresh_items if is_relevant(item.title)]
        print(f"  {name}: {len(relevant)} relevant items")
        if not relevant:
            continue
        # 3. Shuffle and take up to MAX_ITEMS_PER_SOURCE
        sample_size = min(MAX_ITEMS_PER_SOURCE, len(relevant))
        to_process = random.sample(relevant, sample_size)
        print(f"  {name}: processing {len(to_process)} randomly selected items")
        for item in to_process:
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
    schedule.every(30).minutes.do(job)
    schedule.every().monday.at("02:00").do(analytics_job)
    print("Scheduler started — news every 30 min, analytics on Monday 02:00.")
    job()
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()
