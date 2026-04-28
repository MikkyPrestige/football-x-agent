"""Quick manual test for RSSFetcher. Run with: python tests/test_rss_fetcher.py"""
import asyncio
from core.ingestion.rss_fetcher import RSSFetcher

async def main():
    fetcher = RSSFetcher()
    print("Fetching feeds...")
    items = await fetcher.fetch()
    print(f"Got {len(items)} items total.\n")
    for item in items[:5]:
        print(f"[{item.source}] {item.title}")
        print(f"  URL: {item.url}")
        print()

if __name__ == "__main__":
    asyncio.run(main())
