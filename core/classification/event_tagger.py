"""Keyword-based event classifier for NewsItems."""
from core.ingestion.base import NewsItem

# Tag priority: earlier patterns in the list are checked first.
# Add/remove patterns as needed; matches are case-insensitive.
PATTERNS = {
    "LIVE_GOAL": [
        "goal", "scores", "scored", "hat-trick", "hattrick", "penalty scored",
        "free-kick goal", "header goal", "volley goal", "curler", "tap-in",
        "equaliser", "winner", "opener", "brace"
    ],
    "LIVE_CARD": [
        "red card", "yellow card", "sent off", "second yellow", "straight red",
        "dismissed", "booked", "cautioned", "ejection"
    ],
    "TRANSFER": [
        "transfer", "signs", "signed", "bid", "rumour", "deal", "contract",
        "loan", "offered", "target", "free agent", "release clause",
        "transfer window", "deadline day", "medical", "agreed terms",
        "set to join", "close to signing", "moves for", "in talks"
    ],
    "STAT_INSIGHT": [
        "stats", "statistics", "xG", "expected goals", "pass completion",
        "tackles won", "interceptions", "clearances", "duels won",
        "assists", "key passes", "heatmap", "rating", "average",
        "most chances created", "touches", "saves", "clean sheet",
        "possession", "passes", "distance covered"
    ],
    "DEBATE": [
        "debate", "controversial", "should have", "should've", "agree",
        "disagree", "hot take", "unpopular opinion", "argue", "arguably",
        "better than", "vs", "versus", "rival", "who is", "best player",
        "top 5", "top 10", "ranking", "compare", "comparison", "thread"
    ],
    "MEME": [
        "meme", "😂", "💀", "👀", "shithousery", "banter", "troll",
        "crying", "laugh", "funny", "joke", "wild", "unreal",
        "cant believe", "can't believe", "imagine", "only in",
        "peak football", "scripted", "madness"
    ],
}

# Catch-all patterns that always indicate a live event but not specific to goals/cards
LIVE_INDICATORS = [
    "minute", "half-time", "halftime", "full-time", "kick-off",
    "substitution", "subbed", "injury", "stoppage", "added time",
    "penalty shootout", "extra time", "var", "overturned",
    "1h", "2h", "ht", "ft", "status:", "elapsed"
]

def classify_item(item: NewsItem) -> str:
    """Return the best event type tag for a news item based on its title and raw text."""
    text = f"{item.title} {item.raw_text}".lower()

    # Check live indicators first (generic match events) - important!
    if any(ind in text for ind in LIVE_INDICATORS):
        return "LIVE_OTHER"

    # Check high-priority live tags next
    for tag, keywords in PATTERNS.items():
        if any(kw in text for kw in keywords):
            return tag

    return "OTHER"
