"""Weekly analytics engine: analyzes tweet performance and generates rule suggestions."""
import re
from datetime import datetime, timedelta
from sqlalchemy import func
from core.database import SessionLocal
from core.models import Tweet, Draft, Rule

def _count_emojis(text: str) -> int:
    """Count emoji characters in text using a simple pattern."""
    emoji_pattern = re.compile("[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF"
                               "\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF"
                               "\u2600-\u26FF\u2700-\u27BF]", flags=re.UNICODE)
    return len(emoji_pattern.findall(text))

def _length_category(length: int) -> str:
    if length < 100:
        return "short"
    elif length < 200:
        return "medium"
    else:
        return "long"

def _emoji_category(count: int) -> str:
    if count == 0:
        return "none"
    elif count <= 2:
        return "some"
    else:
        return "many"

def run_weekly_analytics():
    """Analyze last 7 days' tweets, generate rule suggestions."""
    with SessionLocal() as session:
        cutoff = datetime.utcnow() - timedelta(days=7)
        tweets = session.query(Tweet).join(Draft, Tweet.draft_id == Draft.id)\
            .filter(Tweet.posted_at >= cutoff).all()

        if len(tweets) < 10:
            print("Not enough tweets for analytics (<10). Skipping rule generation.")
            return

        # Compute overall average likes
        total_likes = sum(t.likes for t in tweets)
        avg_likes = total_likes / len(tweets)
        print(f"Analyzing {len(tweets)} tweets, overall avg likes: {avg_likes:.1f}")

        # Group by various dimensions
        groups = {}
        for t in tweets:
            draft = t.draft
            if not draft:
                continue
            hour = t.posted_at.hour
            day = t.posted_at.strftime("%A")
            content_type = draft.content_type
            persona = draft.persona
            length_cat = _length_category(len(t.text))
            emoji_cat = _emoji_category(_count_emojis(t.text))

            keys = [
                ("content_type", content_type),
                ("persona", persona),
                ("hour", str(hour)),
                ("day", day),
                ("length", length_cat),
                ("emojis", emoji_cat),
            ]
            for dim, val in keys:
                groups.setdefault(dim, {}).setdefault(val, []).append(t.likes)

        # Generate rules
        suggestions = []
        for dim, values in groups.items():
            for val, likes_list in values.items():
                mean = sum(likes_list) / len(likes_list)
                if mean > avg_likes * 1.2:  # 20% above average
                    pct = int((mean - avg_likes) / avg_likes * 100)
                    dim_label = dim.replace("_", " ").title()
                    rules_text = f"{dim_label} = {val} gets {pct}% higher engagement (avg {mean:.1f} likes vs {avg_likes:.1f} overall)."
                    suggestions.append(rules_text)

        # Store suggestions in DB (avoid duplicates)
        for rule_text in suggestions:
            existing = session.query(Rule).filter_by(rule_text=rule_text).first()
            if not existing:
                session.add(Rule(rule_text=rule_text, source="auto", active=False))
        session.commit()
        print(f"Generated {len(suggestions)} rule suggestions.")
