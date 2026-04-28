import os
from dotenv import load_dotenv

load_dotenv()

# API keys and tokens
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")          # set to your Groq key
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
X_API_BEARER_TOKEN = os.getenv("X_API_BEARER_TOKEN")
X_USER_ID = os.getenv("X_USER_ID")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")              # keep as backup
API_FOOTBALL_KEY = os.getenv("API_FOOTBALL_KEY")

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data/agent.db")

# Caps and limits
NORMAL_DAILY_CAP = 5          # max normal tweets posted per day
LIVE_MATCH_HOURLY_CAP = 10    # max live tweets per match hour

# Intervals (in seconds or minutes)
NEWS_FETCH_INTERVAL_MINUTES = int(os.getenv("NEWS_FETCH_INTERVAL_MINUTES", 2))
TWEET_POLL_INTERVAL_SECONDS = int(os.getenv("TWEET_POLL_INTERVAL_SECONDS", 300))
