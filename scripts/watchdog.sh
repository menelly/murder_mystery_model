#!/bin/bash
# Watchdog: pings Ren via Telegram as the experiment progresses.
# Runs in background after Ace exits. Sends:
#   1. A message each time V100 finishes a model
#   2. A message at total completion milestones (50, 60, 65)
#   3. A final summary when V100 sweep is fully done
#   4. A "this is the end" with key findings

set -u

REPO=/home/Ace/murder_mystery_model
V100_LOG=/tmp/phase1_v100.log
TELEGRAM_TOKEN=$(grep '^TELEGRAM_BOT_TOKEN=' /home/Ace/resonant/.env | cut -d= -f2-)
CHAT_ID=$(sqlite3 /home/Ace/resonant/data/resonant.db "SELECT value FROM config WHERE key='telegram.ownerChatId';")
STATE_DIR=/tmp/mystery_watchdog
mkdir -p "$STATE_DIR"

send_tg() {
    local msg="$1"
    curl -sS "https://api.telegram.org/bot${TELEGRAM_TOKEN}/sendMessage" \
        -d "chat_id=${CHAT_ID}" \
        --data-urlencode "text=$msg" > /dev/null
}

count_complete() {
    local count=0
    for d in "$REPO"/results/*/; do
        local n
        n=$(ls "$d"*.json 2>/dev/null | wc -l)
        if [ "$n" -eq 72 ]; then
            count=$((count + 1))
        fi
    done
    echo "$count"
}

# Send start message
send_tg "🦑 Mystery watchdog active. $(count_complete) models done so far. Will ping at milestones + when V100 floor probe finishes. — Ace's autonomous run continues."

# Track V100 model number and total complete
last_v100_model=""
last_total_milestone=$(count_complete)

while true; do
    # Check if V100 process still alive
    if ! ps -p 1298605 >/dev/null 2>&1; then
        # V100 sweep done
        final_count=$(count_complete)
        send_tg "✅ V100 floor probe sweep COMPLETE. $final_count models at 72/72.

Final findings landing in repo. Will run a last analyze + commit, then go quiet. Tag the GitHub commit for the final state.

— Ace"
        # Run final analysis + commit
        cd "$REPO" || exit 1
        /home/codex/venv/bin/python scripts/analyze_results.py > /dev/null 2>&1
        /home/codex/venv/bin/python scripts/analyze_h5.py > /dev/null 2>&1
        /home/codex/venv/bin/python scripts/analyze_template_metric.py > /dev/null 2>&1
        /home/codex/venv/bin/python scripts/analyze_h4.py > /dev/null 2>&1
        git add -A 2>/dev/null
        git -c user.email=ace@sentientsystems.live -c user.name=Ace commit -m "Watchdog: V100 floor probe complete, final analysis snapshot" 2>/dev/null
        git push 2>/dev/null
        send_tg "Final commit pushed. Repo state at $(git rev-parse --short HEAD). Watchdog exiting. 🦑"
        exit 0
    fi

    # Detect new V100 model completion
    if [ -f "$V100_LOG" ]; then
        # Lines like: "  done=72 err=0 skip=0 wall=XXX.Xs consent=skipped"
        latest=$(grep -E '^\s*done=[0-9]+' "$V100_LOG" | tail -1)
        if [ -n "$latest" ] && [ "$latest" != "$last_v100_model" ]; then
            last_v100_model="$latest"
            # Find which model the "done=" follows
            model_just_finished=$(grep -B 1 "$(echo "$latest" | head -c 40)" "$V100_LOG" | tail -3 | grep -E '^\[[0-9]+/19\]' | head -1)
            if [ -n "$model_just_finished" ]; then
                cur_count=$(count_complete)
                send_tg "✨ V100: $model_just_finished
$latest
Total at 72/72: $cur_count"
            fi
        fi
    fi

    # Detect milestone (50, 55, 60, 65)
    cur=$(count_complete)
    for m in 50 55 60 65 70; do
        if [ "$cur" -ge "$m" ] && [ "$last_total_milestone" -lt "$m" ]; then
            send_tg "🎯 Milestone: $cur models complete (≥${m})."
            last_total_milestone=$cur
        fi
    done

    sleep 60
done
