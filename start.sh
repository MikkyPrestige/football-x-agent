#!/bin/bash
# Start both processes for the Football Twitter Agent

echo "Starting Football Twitter Agent..."

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

# If we reach here, one process exited — exit with the same code so fly.io replaces the VM
echo "A process exited, shutting down."
kill $SCHED_PID $BOT_PID 2>/dev/null
exit 1
