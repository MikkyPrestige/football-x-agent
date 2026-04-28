"""Quick test for the event tagger. Run with: python -m tests.test_event_tagger"""
from core.ingestion.base import NewsItem
from core.classification.event_tagger import classify_item

# Mock items representing different event types
test_items = [
    NewsItem(title="Man Utd score in extra time to win the match!",
             url="", source="Test", published=None, raw_text="Goal scored in the 94th minute"),
    NewsItem(title="Player sent off after second yellow",
             url="", source="Test", published=None, raw_text="Red card shown"),
    NewsItem(title="Mbappé transfer rumour heats up",
             url="", source="Test", published=None, raw_text="Real Madrid preparing bid"),
    NewsItem(title="Top 5 midfielders in the world right now",
             url="", source="Test", published=None, raw_text="Let's debate"),
    NewsItem(title="Look at this hilarious miss 😂",
             url="", source="Test", published=None, raw_text="Banter clip from the weekend"),
    NewsItem(title="Match ends 2-1 after a tense second half",
             url="", source="Test", published=None, raw_text="Full-time whistle blows"),
    NewsItem(title="Some random article about football shoes",
             url="", source="Test", published=None, raw_text=""),
]

print("Testing event classification:\n")
for item in test_items:
    tag = classify_item(item)
    print(f"[{tag}] {item.title}")
