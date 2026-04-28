"""Quick manual test for GoogleNewsFetcher. Run with: python -m tests.test_google_news_fetcher"""
import asyncio
from core.ingestion.google_news_fetcher import GoogleNewsFetcher

async def main():
    fetcher = GoogleNewsFetcher()
    print("Fetching Google News...")
    items = await fetcher.fetch()
    print(f"Got {len(items)} items.\n")
    for item in items[:5]:
        print(f"[{item.source}] {item.title}")
        print(f"  URL: {item.url}")
        print()

if __name__ == "__main__":
    asyncio.run(main())
