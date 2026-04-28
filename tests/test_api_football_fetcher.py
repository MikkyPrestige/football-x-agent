"""Quick manual test for APIFootballFetcher. Run with: python -m tests.test_api_football_fetcher"""
import asyncio
from core.ingestion.api_football_fetcher import APIFootballFetcher

async def main():
    fetcher = APIFootballFetcher()
    print("Fetching live match data from API-Football...")
    items = await fetcher.fetch()
    print(f"Got {len(items)} events.\n")
    for item in items[:5]:
        print(f"[{item.source}] {item.title}")
        print(f"  URL: {item.url}")
        print()

if __name__ == "__main__":
    asyncio.run(main())
