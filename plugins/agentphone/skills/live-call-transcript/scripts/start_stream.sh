#!/usr/bin/env bash
# Start streaming an AgentPhone call's transcript (Server-Sent Events) into a
# file, in the background. Run it right after make_conversation_call/make_call
# returns: turns spoken before you connect are not replayed until hangup.
# Running it again for the same call restarts the stream from scratch.
#
#   start_stream.sh <call_id>   -> prints the path of the .sse file
set -euo pipefail
call_id="${1:?usage: start_stream.sh <call_id>}"
: "${AGENTPHONE_API_KEY:?AGENTPHONE_API_KEY is not set in this shell}"
dir="${AGENTPHONE_STREAM_DIR:-$HOME/.agentphone}"
mkdir -p "$dir"
out="$dir/$call_id.sse"
: > "$out"
rm -f "$out.offset" "$out.done"
nohup curl -sN --no-buffer --fail-with-body --max-time 7200 \
  -H "Authorization: Bearer $AGENTPHONE_API_KEY" \
  "https://api.agentphone.ai/v1/calls/$call_id/transcript/stream" \
  >> "$out" 2>> "$out.err" &
echo $! > "$out.pid"
echo "$out"
