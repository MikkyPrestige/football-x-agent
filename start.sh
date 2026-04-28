#!/bin/bash
# Football Twitter Agent startup

echo "Starting Football Twitter Agent..."
python -c "from core.database import SessionLocal; from core.models import Draft, EventCache; s=SessionLocal(); s.query(Draft).delete(); s.query(EventCache).delete(); s.commit(); print("Old data cleared")"

# Initialize database (creates tables if missing)
python -c "from core.database import init_db; init_db(); print('Database ready')"

# Start scheduler in background
python -m core.scheduler &
SCHED_PID=$!
echo "Scheduler started (PID $SCHED_PID)"

# Start Telegram bot in background
python -m bot.main &
BOT_PID=$!
echo "Telegram bot started (PID $BOT_PID)"

# Wait for either process to exit
wait -n $SCHED_PID $BOT_PID

echo "A process exited, shutting down."
kill $SCHED_PID $BOT_PID 2>/dev/null
exit 1
