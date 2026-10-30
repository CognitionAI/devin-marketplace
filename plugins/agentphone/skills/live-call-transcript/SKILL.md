---
name: live-call-transcript
description: Show the user what is being said on an AgentPhone call while the call is still in progress. Use whenever you place a call with make_conversation_call or make_call. AgentPhone's get_call returns no transcript until the call ends, so stream the REST transcript endpoint from a background shell and post the new turns to the user every ~15 s.
---

# Live call transcript

## Why

AgentPhone stores a call's transcript only when the call ends. While the call
is live, `get_call` (MCP and `GET /v1/calls/{id}`) returns
`status: in-progress` with no transcript, and the `agent.call_ended` webhook
fires only at hangup. The one live source is the Server-Sent Events endpoint
`GET https://api.agentphone.ai/v1/calls/{id}/transcript/stream`, which pushes
each turn within about 0.2-2 s of it being spoken. It is not exposed by the
MCP server, so read it with `curl` from the shell.

Measured on 2026-10-30: hosted-mode turns arrive as `{agent, user}` pairs
about 2 s after the other party finishes replying; webhook-mode turns arrive
0.01 s after speech-to-text completes.

## Requirements

- `AGENTPHONE_API_KEY` in the shell environment (an org or personal secret
  with that name). If it is missing, use the fallback at the end.
- `curl` and `python3` on the machine.

## Steps

1. Place the call (`make_conversation_call` or `make_call`) and read the
   `Call ID` from the result. (For a call that is already in progress, e.g.
   an inbound one, take the id of the `in-progress` entry in `list_calls`;
   the turns spoken before you connect arrive only at hangup.)
2. **Immediately** start the stream. Turns spoken before you connect are not
   replayed until hangup, and the first turn comes 5-10 s after dialing:

   ```bash
   SSE=$(bash <skill-dir>/scripts/start_stream.sh <call_id>)
   ```

   It prints the path of the `.sse` file it appends to
   (`~/.agentphone/<call_id>.sse`).
3. Tell the user once, in one line, that the call is connecting and that you
   will post what is said as it happens.
4. Loop until the call ends:
   - `wait` about 15 s (shorter makes the user's feed noisy and costs an
     agent turn per iteration; longer feels dead).
   - `python3 <skill-dir>/scripts/new_turns.py "$SSE"` prints only the turns
     that arrived since the previous run, one per line (`Devin: …` for your
     agent, `Them: …` for the other party). Exit code 10 means the `ended`
     event arrived. Exit code 20 means the stream died before the call ended
     (the line printed says why: a 401 body, a dropped connection); run
     `start_stream.sh <call_id>` once more and tell the user the turns in
     between will arrive at hangup. If it dies again, switch to the
     fallback at the end of this file.
   - If it printed any turn, send one non-blocking `message_user` with the
     elapsed time and those lines (format below). If it printed nothing,
     send nothing; after 60 s of silence, send one short "still on the call,
     nothing new (holding/IVR)" note at most once per minute.
   - Stop when the exit code is 10 or `get_call` reports a terminal status
     (`completed`, `failed`, `busy`, `no-answer`).
5. After the call ends, wait 5 s, then call `get_call` for the authoritative
   transcript: AgentPhone writes it 1-3 s after hangup, so if the result has
   no transcript yet, retry every 5 s for up to 30 s, and say so if it is
   still missing. Send the outcome (what was agreed, numbers, next steps)
   first and the full transcript after it, as usual.
6. Delete `~/.agentphone/<call_id>.*` once the transcript is in the chat, so
   the conversation does not linger on the machine.

## Message format

One message per batch, nothing else in it:

```
📞 On the call with <who> (2:30). New:
Them: One moment while I transfer you. Calls may be monitored or recorded…
Devin: I'm still here and holding.
Them: When calling about your Toyota vehicle, please have your VIN handy…
```

Trim a single turn to about 300 characters with `…`. Never post more than
one such message per 15 s, and never relay secrets or card numbers the user
did not ask you to say.

## Fallback when AGENTPHONE_API_KEY is not in the shell

Live text is not available. Every 60 s call `get_call`, and post one line with
the status and elapsed time ("Still on the call, 3:00 elapsed, status
in-progress") so the user is not blind; post the transcript when the call
ends.

## Gotchas

- Re-connecting mid-call after `curl` dies gives you only the `connected`
  event; the turns you missed come at hangup. Say so in the next update.
- A hosted-mode turn is emitted only after the other party's next utterance
  ends, so the last thing your agent says can lag until the call ends.
- The stream has heartbeat comment lines; `new_turns.py` ignores them.
- `end_call <call_id>` hangs up if the user asks you to stop the call.
