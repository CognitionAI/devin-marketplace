---
name: schedule-google-meeting
description: "Set up, move or cancel a Google Calendar meeting with other people: turn names into addresses, find a time across calendars and time zones, confirm before invitations go out, and handle one occurrence versus a whole series. Use whenever the user asks to schedule, book, find time for, reschedule, move or cancel a meeting, or to add or remove someone from one. Requires google-productivity-mcp."
---

# Scheduling meetings on Google Calendar

Every calendar write emails the attendees straight away and has no draft step, so the work happens
before the write. Signatures are in `google-productivity-mcp`.

## Schedule a new meeting

### 1. Pin down the request

- Who, how long, by when, and whether it needs a Meet link or a location. Ask only for what you
  cannot infer; default to 30 minutes when `durationMinutes` is not stated.
- Turn "next week" or "Thursday afternoon" into concrete dates.
- Use `primary` unless the user names another calendar (`list_calendars`).

### 2. Turn names into addresses

Call `search_contacts` for each person.

- One match: use it.
- Several matches: ask which one. Do not pick by guesswork.
- No match: try `search_emails` (`from:"Jane Doe"`) and read the address from `from`, otherwise ask
  the user. Never construct an address from a name and a company domain.

### 3. Find times

Build `windows` from when these people would really meet: inside everyone's workday, outside lunch
and other shared breaks. For attendees in other zones, work out the overlap first and write the
windows with explicit offsets (`2026-12-08T09:00:00-05:00/2026-12-08T11:00:00-05:00`). Ask when you
do not know where someone is.

Call `suggest_time` and read each slot:

- `free`: these attendees have nothing in that slot.
- `blocked`: these attendees are busy, with the clashing `events`. Their RSVP to the clash tells you
  how firm it is.
- `latestStart`: the slot's start can slide up to this time.

Then read the two top-level fields:

- `unknown`: attendees whose calendar you cannot read, which is normal for people outside the user's
  organization, but also what a mistyped address returns. They are in no slot and no count, so
  `1/1 free` does not mean everyone is free. Do not report them as free or as busy.
- `timeZone`: the user's zone, for presenting the options.

### 4. Propose, then confirm

Offer one to three options in the user's zone, plus the attendee's zone when it differs, and say
whose availability is unknown. Before creating, the user must have seen the title, time with zone
and exact guest list. Skip the options when the user already gave the exact time and guests.

### 5. Create once

Call `create_event` with `addConference: true` if a video link is wanted. Use `recurrence` for a
repeating meeting. Report the time, guests, `link` and `meetLink`, plus `seriesTimeZone` if it comes
back: that is the zone the series was pinned to, and it follows that zone's daylight-saving changes.

A second `create_event` sends a second invitation. If the outcome of a call is unclear, look with
`list_events` before trying again.

## Change an existing meeting

Find it with `list_events` over a date range and match the title yourself. A `recurringEventId` on
the result means it belongs to a series; ask "just this one or all of them?" unless the request
already says.

| Change | Call |
| ------ | ---- |
| Move one meeting, or one occurrence | `suggest_time` with `eventId` to find a slot (all-day events: pass `attendees` and `durationMinutes` instead), then `update_event` for a one-off or `update_occurrence` with the instance id for an occurrence |
| Move the whole series | `update_event` with the bare series id (`recurringEventId`) |
| Add or remove a guest | `update_event` with the full new `attendees` list, built from the guests `list_events` returned |
| Cancel one occurrence | `update_occurrence` with the instance id and `cancel: true`, or `delete_event` with the instance id |
| Cancel the whole meeting or series | `delete_event`, which cannot be undone |

- `suggest_time` does not move anything. Moving takes one of the update calls afterwards.
- A time change passes both `startDateTime` and `endDateTime`.
- Every update above emails the guests, so confirm any cancellation or change to a meeting with
  other people first, and do not send several small updates when one will do. The one exception is
  `delete_event` with `sendUpdates: "none"`, which cancels without emailing anyone; use it only
  when the user asks for a quiet delete, since the default still notifies every guest.
- Replying to an invitation the user received is `rsvp_event`, not an update.
