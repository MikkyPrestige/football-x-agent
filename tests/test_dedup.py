"""Test deduplication: same item twice should be rejected. Run with: python -m tests.test_dedup"""
from datetime import datetime
from core.ingestion.base import NewsItem
from core.classification.dedup import is_duplicate, cleanup_memory_cache

# Create a sample news item
item = NewsItem(
    title="Breaking: Mbappe signs for Real Madrid",
    url="",
    source="Test",
    published=datetime.utcnow(),
    raw_text="Deal agreed"
)
event_type = "TRANSFER"

print("First check (should be False):", is_duplicate(item, event_type))
print("Second check (should be True):", is_duplicate(item, event_type))

# Cleanup memory for repeatable tests
cleanup_memory_cache()
