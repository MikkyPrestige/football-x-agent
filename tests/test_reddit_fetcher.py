"""Quick manual test for RedditFetcher. Run with: python -m tests.test_reddit_fetcher"""
import asyncio
from core.ingestion.reddit_fetcher import RedditFetcher

async def main():
    fetcher = RedditFetcher()
    print("Fetching Reddit r/soccer new posts...")
    items = await fetcher.fetch()
    print(f"Got {len(items)} items.\n")
    for item in items[:5]:
        print(f"[{item.source}] {item.title}")
        print(f"  URL: {item.url}")
        print()

if __name__ == "__main__":
    asyncio.run(main())
