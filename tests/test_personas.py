"""Quick test for persona configuration. Run with: python -m tests.test_personas"""
import yaml
from core.classification.event_tagger import classify_item
from core.ingestion.base import NewsItem

# Load personas.yaml
with open("config/personas.yaml", "r") as f:
    personas = yaml.safe_load(f)

print("Base identity loaded:", bool(personas.get("base_identity")))
print("Available modes:", list(personas.get("modes", {}).keys()))

# Test mode selection based on event type
event_to_mode = {}
for mode_name, mode_data in personas["modes"].items():
    for trigger in mode_data["trigger"]:
        event_to_mode[trigger] = mode_name

print("\nEvent → Mode mapping:")
for event, mode in sorted(event_to_mode.items()):
    print(f"  {event} → {mode}")

# Simulate an event
item = NewsItem(title="Transfer rumour: Mbappé to Real Madrid", url="", source="",
                published=None, raw_text="")
tag = classify_item(item)
mode = event_to_mode.get(tag, "pundit")   # default fallback
print(f"\nSimulated: tag={tag}, mode={mode}")
