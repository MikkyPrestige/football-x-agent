"""Event deduplication: prevents duplicate drafts for the same event."""
import hashlib
from datetime import datetime, timedelta
from core.database import SessionLocal
from core.models import EventCache
from core.ingestion.base import NewsItem

# In-memory set of active hashes to avoid DB hits for very recent events
_recent_hashes: set[str] = set()

# Live event types use a tighter time window (5 min) vs normal (1 hour)
LIVE_TAGS = {"LIVE_GOAL", "LIVE_CARD", "LIVE_OTHER"}

def generate_event_hash(item: NewsItem, event_type: str) -> str:
    """Create a unique hash from source, normalized title, event type, and rounded timestamp."""
    # Normalize title: lowercase, strip extra whitespace
    normalized_title = " ".join(item.title.lower().split())
    # Round timestamp to the hour for normal events, to 5 minutes for live events
    if event_type in LIVE_TAGS:
        # Round to nearest 5 minutes
        minute_bucket = (item.published.minute // 5) * 5
        rounded = item.published.replace(minute=minute_bucket, second=0, microsecond=0)
    else:
        rounded = item.published.replace(minute=0, second=0, microsecond=0)
    # Build a stable string for hashing
    raw = f"{item.source}|{normalized_title}|{event_type}|{rounded.isoformat()}"
    return hashlib.sha256(raw.encode()).hexdigest()

def is_duplicate(item: NewsItem, event_type: str) -> bool:
    """Return True if this event was already processed (in memory or DB), else store and return False."""
    event_hash = generate_event_hash(item, event_type)

    # 1. Check in-memory cache
    if event_hash in _recent_hashes:
        return True

    # 2. Check database
    with SessionLocal() as session:
        existing = session.get(EventCache, event_hash)
        if existing:
            # Found in DB, still valid? (should be very recent; we clean up old entries later)
            if existing.expiry > datetime.utcnow():
                # Also add to memory for future quick checks
                _recent_hashes.add(event_hash)
                return True
            else:
                # Expired – remove from DB and memory, it's no longer a duplicate
                session.delete(existing)
                session.commit()
                _recent_hashes.discard(event_hash)
                # Fall through to store new entry

    # 3. Store new hash
    hours = 2 if event_type in LIVE_TAGS else 24
expiry = datetime.utcnow() + timedelta(hours=hours)
    new_entry = EventCache(event_hash=event_hash, created_at=datetime.utcnow(), expiry=expiry)
    with SessionLocal() as session:
        session.merge(new_entry)
        session.commit()

    _recent_hashes.add(event_hash)
    return False

def cleanup_memory_cache():
    """Remove memory hashes that are older than 2 hours (call periodically)."""
    # Since we don't store timestamps in memory, we just clear the whole set.
    # A more refined approach could store (hash, expiry) but for our volume this is fine.
    _recent_hashes.clear()
