"""Integration test: prompt builder + LLM client. Run with: python -m tests.test_llm_client"""
import asyncio
from datetime import datetime
from core.ingestion.base import NewsItem
from core.generation.prompt_builder import build_prompt
from core.generation.llm_client import generate_tweet

async def main():
    item = NewsItem(
        title="Transfer rumour: Mbappé to Real Madrid heating up",
        url="",
        source="Test",
        published=datetime.utcnow(),
        raw_text="Multiple sources confirm talks"
    )
    event_tag = "TRANSFER"
    system, user = build_prompt(item, event_tag)

    print("Generating tweet with Groq…\n")
    try:
        tweets = generate_tweet(system, user, n=1)
        for i, t in enumerate(tweets, 1):
            print(f"Variant {i}:\n{t}\n")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(main())
