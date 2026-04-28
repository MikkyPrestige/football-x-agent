"""Quick test for prompt builder. Run with: python -m tests.test_prompt_builder"""
from datetime import datetime
from core.ingestion.base import NewsItem
from core.generation.prompt_builder import build_prompt, get_mode_for_tag

# Mock event
item = NewsItem(
    title="BREAKING: Mbappe signs 5-year deal with Real Madrid",
    url="",
    source="Test",
    published=datetime.utcnow(),
    raw_text="The transfer window madness continues."
)
event_tag = "TRANSFER"
mode = get_mode_for_tag(event_tag)
print(f"Event tag: {event_tag} → Mode: {mode}\n")

system_prompt, user_prompt = build_prompt(item, event_tag)
print("=== SYSTEM PROMPT ===")
print(system_prompt)
print("\n=== USER PROMPT ===")
print(user_prompt)
