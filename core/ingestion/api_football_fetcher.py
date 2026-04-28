import asyncio
from datetime import datetime
from typing import List
import requests
from config.settings import API_FOOTBALL_KEY
from core.ingestion.base import BaseFetcher, NewsItem
from core.ingestion.monitor import record_success, record_failure

BASE_URL = "https://v3.football.api-sports.io"
HEADERS = {"x-apisports-key": API_FOOTBALL_KEY}

# Top 5 leagues, domestic cups, European competitions, plus Saudi & Turkey
LEAGUE_IDS = [
    39,    # Premier League
    528,   # Community Shield
    45,    # FA Cup
    48,    # League Cup
    143,   # Copa del Rey
    140,   # La Liga
    78,    # Bundesliga
    81,    # DFB Pokal
    135,   # Serie A
    137,   # Coppa Italia
    66,    # Coupe de France
    61,    # Ligue 1
    2,     # UEFA Champions League
    3,     # UEFA Europa League
    848,   # UEFA Conference League
    826,   # Saudi Super Cup
    307,   # Saudi Pro League
    203,   # Turkish Süper Lig
    551,   # Turkish Super Cup
]

class APIFootballFetcher(BaseFetcher):
    async def fetch(self) -> List[NewsItem]:
        items = []
        try:
            # Build league filter string: 39-140-135-...
            league_filter = "-".join(str(lid) for lid in LEAGUE_IDS)
            # 1. Get live fixtures filtered by leagues
            fixtures_data = await asyncio.to_thread(
                self._get_json,
                f"{BASE_URL}/fixtures?live=all&league={league_filter}"
            )
            live_fixtures = fixtures_data.get("response", [])

            for fixture in live_fixtures:
                fixture_id = fixture["fixture"]["id"]
                home = fixture["teams"]["home"]["name"]
                away = fixture["teams"]["away"]["name"]
                status = fixture["fixture"]["status"]["short"]

                # 2. Get events for this fixture
                events_data = await asyncio.to_thread(
                    self._get_json,
                    f"{BASE_URL}/events?fixture={fixture_id}"
                )
                for evt in events_data.get("response", []):
                    event_type = evt["type"]
                    detail = evt.get("detail", "")
                    player = evt.get("player", {}).get("name", "Unknown")
                    team = evt["team"]["name"]
                    minute = evt["time"]["elapsed"]

                    # Build a tweet‑friendly title
                    if event_type == "Goal":
                        title = f"⚽ GOAL! {team} {detail} – {home} vs {away} ({minute}')"
                    elif event_type in ("Card", "Yellow Card", "Red Card"):
                        title = f"🟨 CARD: {player} ({team}) – {home} vs {away}"
                    elif event_type == "subst":
                        title = f"↔️ SUB: {player} – {home} vs {away}"
                    else:
                        continue  # skip other events

                    items.append(NewsItem(
                        title=title,
                        url=f"https://www.flashscore.com/match/{fixture_id}",
                        source="API-Football",
                        published=datetime.utcnow(),
                        raw_text=f"{event_type} by {player} at {minute}'"
                    ))

                # Also mark match start / halftime / fulltime if we want
                if status in ("1H", "HT", "2H", "FT"):
                    items.append(NewsItem(
                        title=f"📢 {home} vs {away} – Status: {status}",
                        url=f"https://www.flashscore.com/match/{fixture_id}",
                        source="API-Football",
                        published=datetime.utcnow(),
                        raw_text=f"Match status: {status}"
                    ))

            record_success("API-Football")
        except Exception as e:
            record_failure("API-Football")
            print(f"API-Football fetch failed: {e}")
        return items

    def _get_json(self, url: str):
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        return resp.json()
