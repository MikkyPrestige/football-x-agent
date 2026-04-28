"""Integration test: full pipeline from NewsItem to Draft. Run with: python -m tests.test_queue_manager"""
import asyncio
from datetime import datetime
from core.ingestion.base import NewsItem
from core.generation.queue_manager import process_item

async def main():
    item = NewsItem(
        title="Transfer rumour: Mbappé to Real Madrid heating up",
        url="",
        source="Test",
        published=datetime.utcnow(),
        raw_text="Multiple sources confirm talks"
    )
    print("Processing item through pipeline...\n")
    draft = await process_item(item)
    if draft:
        print(f"Draft created (id={draft.id}):")
        print(f"  Status: {draft.status}")
        print(f"  Persona: {draft.persona}")
        print("  Variants:")
        for i, v in enumerate(draft.text_variants):
            print(f"    {i+1}: {v}")
    else:
        print("Draft not created (skipped or error).")

if __name__ == "__main__":
    asyncio.run(main())
