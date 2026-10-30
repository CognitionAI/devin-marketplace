#!/usr/bin/env python3
"""Print the transcript turns that arrived since the last run.

    new_turns.py <path.sse>

Reads the SSE file written by start_stream.sh, remembers how far it got in
<path.sse>.offset, and prints one line per new event:

    [connected] in-progress
    Devin: Hi, quick heads up: I'm an AI assistant ...
    Them: One moment while I transfer you.
    [ended] completed after 205 s

Exit codes: 0 while the call is live, 10 once the `ended` event was seen
(also on every later run), 20 when the curl stream died before `ended`
(HTTP error, bad key, dropped connection); the line printed then says why.
"""
import json
import os
import sys


def process_alive(pid_path: str) -> bool:
    try:
        pid = int(open(pid_path).read().strip())
        os.kill(pid, 0)
        return True
    except (FileNotFoundError, ValueError, ProcessLookupError, PermissionError):
        return False


def main() -> int:
    path = sys.argv[1]
    offset_path, done_path = path + ".offset", path + ".done"
    if os.path.exists(done_path):
        return 10
    try:
        offset = int(open(offset_path).read().strip() or 0)
    except FileNotFoundError:
        offset = 0
    with open(path, "rb") as f:
        f.seek(offset)
        raw = f.read()
    # Only consume complete events (terminated by a blank line).
    cut = raw.rfind(b"\n\n")
    chunk, consumed = (raw[: cut + 2], offset + cut + 2) if cut >= 0 else (b"", offset)
    ended = False
    for block in chunk.decode("utf-8", "replace").split("\n\n"):
        event, data = None, []
        for line in block.splitlines():
            if line.startswith("event:"):
                event = line[6:].strip()
            elif line.startswith("data:"):
                data.append(line[5:].strip())
        if not event:
            continue  # heartbeat comment
        try:
            payload = json.loads("\n".join(data)) if data else {}
        except json.JSONDecodeError:
            payload = {}
        if event == "connected":
            print(f"[connected] {payload.get('status', '?')}")
        elif event == "turn":
            who = "Devin" if payload.get("role") == "agent" else "Them"
            text = " ".join(str(payload.get("content", "")).split())
            if text:
                print(f"{who}: {text}")
        elif event == "ended":
            ended = True
            print(
                f"[ended] {payload.get('status', '?')} after "
                f"{payload.get('durationSeconds', '?')} s"
            )
    with open(offset_path, "w") as f:
        f.write(str(consumed))
    if ended:
        open(done_path, "w").close()
        return 10
    if not process_alive(path + ".pid"):
        # curl is gone without an `ended` event: an HTTP error body (not SSE)
        # or the connection dropped. Show whatever it left behind.
        detail = raw[consumed - offset :].decode("utf-8", "replace").strip()
        if not detail:
            try:
                detail = open(path + ".err").read().strip().splitlines()[-1]
            except (FileNotFoundError, IndexError):
                detail = "no output"
        print(f"[stream closed] {detail[:200]}")
        return 20
    return 0


if __name__ == "__main__":
    sys.exit(main())
