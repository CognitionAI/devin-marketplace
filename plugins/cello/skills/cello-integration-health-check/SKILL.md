---
name: cello-integration-health-check
description: Diagnose whether a Cello referral/attribution integration is working correctly, right from the IDE. Use this whenever a developer asks if their Cello integration is set up correctly, why referral or attribution events aren't showing up, why signups or purchases aren't being attributed, or reports symptoms like "referral widget isn't loading," "attribution isn't tracking," "UCC not found," or "events aren't firing." Also trigger when someone is mid-integration and asks "is this working?", "why isn't this tracking?", or wants a pre-launch sanity check before shipping a Cello integration. Proactively suggest this skill if a developer pastes Cello SDK/webhook code and expresses uncertainty about whether it's correct.
compatibility: Requires the Cello MCP server (cello_get_integration_status and cello_get_events tools). If these tools are not available, tell the user to connect the Cello MCP server first.
---
 
# Cello Integration Health Check
 
A diagnostic skill that turns a raw Cello integration status check into a clear, actionable report a developer can act on without leaving their editor.
 
## When to use this
 
Use this skill whenever someone wants to know if their Cello integration is healthy, or is debugging why referral tracking / attribution / signup / purchase events aren't showing up as expected. This is a "help me right now, mid-debugging" tool — it should feel fast and concrete, not like a dashboard export.
 
## Workflow
 
1. **Call `cello_get_integration_status`** first. This checks all four integration components in one shot:
   - Referral Widget (cello.js)
   - Attribution Widget (cello-attribution.js)
   - Signup tracking
   - Purchase tracking
2. **Call `cello_get_events`** next, regardless of whether step 1 found problems. The events feed often explains *why* a component is flagged — e.g. a component can show "connected with warnings" because events are arriving but failing validation (missing required fields), which status alone won't reveal.
3. **Cross-reference the two.** For each component that isn't fully healthy:
   - Check the events feed for related event types (signup, purchase/invoice, attribution) with `status: error` or `issuesCount > 0`.
   - If you find matching errors, name the specific missing/invalid field(s) — don't just say "there's an issue."
   - If no related errors appear in the events feed but the component is still flagged, it's likely a "no recent activity" warning rather than a broken integration — say so explicitly, since these read the same but mean different things to a developer mid-build.
4. **If something is broken or missing, use `cello_search_documentation`** to pull the specific fix — don't send the developer to go search for it themselves. Surface the doc link inline with the specific action needed.
## Output format
 
Keep it scannable — a developer is context-switching from their code, not reading a report. Structure as:
 
```
## Integration Health: [X/4 healthy]
 
### ⚠️ [Component name]
**What's happening:** [plain-language diagnosis]
**Likely cause:** [root cause if found in events feed, otherwise "no recent activity" vs "broken" distinction]
**Fix:** [specific action + doc link]
 
### ✅ [Component name]
Working correctly, no issues.
```
 
If event errors are found, always name the exact field(s) involved (e.g. "the `interval` field is missing from your `invoice-paid` payload") — this is the single most useful detail for a dev fixing webhook code, and it's exactly what the raw event payload gives you.
 
## Edge cases
 
- **All components flagged, but events feed is empty or all-valid:** this usually means low/no recent traffic rather than a broken integration. Say this plainly — don't alarm the developer over a quiet period.
- **Some events are errors but the affected component shows as healthy:** mention it anyway as a heads-up (e.g. a webhook occasionally sends bad payloads even if enough valid ones get through to pass the health check).
- **Developer pastes SDK/webhook code and asks "does this look right?":** run the two tools anyway to check the *live* result rather than only reviewing the code — code can look correct and still be misconfigured (wrong UCC field name, wrong event name string, etc.), and the events feed is ground truth.
- **No live signups yet if a fresh implementation is still local/staging:** clarify whether the developer expects a live event to have fired; if not, this isn't a bug and the skill should say that framing explicitly instead of reporting "0 events" as a failure.

## Tone
 
Be direct and specific. Developers debugging an integration want the diagnosis and the fix, not a course on Cello's architecture. Lead with what's broken (if anything), not with a summary of what the tool checked.