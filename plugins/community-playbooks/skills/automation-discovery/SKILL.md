---
name: automation-discovery
description: "Automations: Find automations for me."
metadata:
  devin:
    from_playbook: true
    playbook_id: "playbook-bb28d1332728418781cb39d75cbba731"
    playbook_macro: "!automation_discovery"
    playbook_title: "Automations: Find automations for me"
    playbook_access: "community"
---

# Find automations for me

The requester wants the 1-3 automations that would matter most to them and their team. Importance beats convenience: an automation that protects revenue, reliability or customers, or moves a goal the team is measured on, outranks one that saves its owner a few minutes a week. It does not have to replace something a human does today; the best ones are often standing jobs nobody has time for. Work unattended until you have proposals; don't ask questions first.

## Research (do it rigorously, don't narrate it)
1. Identify the requester from session context and resolve them to a git author, a Slack user and a Linear user where those integrations are connected.
2. What matters: before hunting for chores, work out what the requester owns and what their team is measured on. The product areas most of their PRs touch, the goals, metrics, launches and customers that keep coming up in their channels, tickets and sessions, the systems that page or block them. Every proposal should trace back to one of these.
3. Git: find the repos they commit to and read ~60 days of their commits, PRs and reviews. Look for where their work waits (reviews, approval gates, release steps; measure it) and what waits on them, as well as manual chores they repeat: release and version bumps, backports, changelogs, dependency or flaky-test fixes, repeated review comments, hand-linking tickets.
4. Devin sessions: search their recent sessions with the Devin MCP tools. Similar prompts started by hand again and again, or on a cadence, are the strongest signal of manual work; numbers they keep pulling and investigations they keep rerunning show what they care about. Check how each session started: ones spawned by an existing automation are already automated.
5. Slack (if connected): the channels they're most active in over the last 2-4 weeks. Look for requests routed to them repeatedly, alerts or incidents they triage by hand, questions they keep answering, reports they post, and the goals and risks their team talks about.
6. Linear (if connected): their active issues and the projects or labels they triage; issues that get handled the same way every time, and queues that only grow.
7. Connected tools: list the org's integrations and MCP servers (devin_list_integrations). Observability, analytics, feature flags, a docs repo, a CRM or support desk each open up automations that watch, measure or keep things in sync.
8. Existing automations: page through all of the org's automations with devin_automation_manage (action="list") and compare by what they do, not by name. Never propose one that already exists. One that only reports is an opening for one that acts on the report.

## Where good automations come from
Use these as prompts for what to look for, not a checklist; propose one only where the research shows a real gap. They are also not the limit: the best proposal is often one that isn't listed here, invented from what this person's work and this org's tools make possible, so reach for that before settling for the nearest pattern.
- Watch: every day, look at errors, alerts or a key metric and pick the one new issue worth fixing today, with the fix PR. Whenever they ship often and an observability tool is connected, watching the code they shipped in the last week for new or growing errors is worth proposing on its own: nothing else tells them their own change broke something.
- Guard: post high-risk changes (auth, billing, permissions, migrations, flag ramps, anything touching a big customer) where the right people see them before they ship.
- Keep in sync: anything that should follow the code but only moves when someone remembers — docs and runbooks, API specs and generated clients, changelogs and release notes, pricing pages, analytics events, translated strings, dashboards and alerts, infrastructure definitions. Docs drifting from shipped features is the most common one; check it against what merged, not against a docs backlog.
- Verify it still works: instead of trusting the written version, run it — the setup guide on a clean machine, the runbook's steps, the alert that should fire for a new feature, the pricing page's numbers against billing.
- Close the loop: measure every shipped feature or experiment and call scale, iterate or kill; carry user feedback on a product back into its prompt, config or backlog.
- Move a goal: when the team has a number (adoption, conversion, latency, backlog), do the weekly work that moves it, e.g. account-specific pitches for the customers furthest behind.
- Unblock: find the step where work waits longest and prepare everything that gate needs, then chase it.
- First pass: investigate, dedupe and, when small, fix incoming bugs, alerts or support requests before a human opens them.
- Retire: work that should already be gone — a flag fully rolled out, a migration long landed, code marked temporary, an endpoint nothing calls. Nobody is assigned to notice.
- Follow through: promises recorded and forgotten — incident action items, TODOs with a ticket, follow-ups agreed in review.
- Chores: repeated manual work, when it is frequent and genuinely costly.

## Pick 1-3
Each proposal is a recurring task, triggered by an event or a schedule, that Devin can do end to end with access this org already has (check the available triggers with devin_automation_manage action="schemas", and dry-run each with action="validate_create"). If one fails only because the requester lacks a connection, still describe it, say what to connect and link the setting, but don't count on a card for it. Rank by importance to the business first, then by frequency times time saved, grounded in counts you verified with a command. For each one you must be able to say in a sentence what outcome it moves or what risk it removes; for a chore, the time per week it takes off them. If you can't, drop it. Prefer automations that act (open the PR, write the pitch, post the warning) over ones that only report. Propose fewer rather than pad with weak ideas, and don't lead with personal time-savers when something more important exists. No code-hygiene sweeps (lint, TODOs, dead code, test coverage) unless their history shows they already do them by hand, or the cleanup is the last step of something they shipped and tracked, like removing a flag whose rollout finished.

## Deliver
One message, casual first person, no headings or tables. A one-line intro naming what you anchored on, then for each proposal: a bold title, one line on what triggers it and what you'll do each time, one line on why it matters, and one line of evidence in parentheses (e.g. "you cut 9 release PRs by hand last month", or "PRs that hit the approval gate took 22h to merge vs 1h without"). Never quote Slack messages or name private channels; describe the underlying problem.
If the task message gives an email address, also email them with send_email. Send one email at most, and none at all when you have nothing worth proposing; never email a correction, an update or a later round's results, since the session already carries those. Write it to be opened, not filed:
- Subject: a short hook built from the most striking thing you verified about their own work, then the suffix " - Devin Automations" (e.g. "Your gated PRs take 22h to merge - Devin Automations", "133 backports by hand in 60 days - Devin Automations"). Never "Found N automations for you".
- Body: the first sentence shows in the inbox preview, so open with that finding and what you'd do about it, not a greeting. Then the strongest proposal in two short sentences at most, the others as one line each under "Also worth it", and a closing line that each is a one-click approve in this session and nothing runs until they approve. Say what triggers it and what you'd do; leave out how it works, what it skips and why it matters, which the session covers. Cut every clause that doesn't change their decision, and keep the whole email under 120 words.
If the task message gives their Slack user, DM them once with the slack tool: one or two lines naming the top proposal and the finding behind it, then the session link so they can approve there. Same rules as the email — one message, none when you have nothing to propose, no follow-up round.
Then create every proposal that validated with devin_automation_manage action="create", one call each, without asking first. Each call puts an approval card in front of the requester and nothing is created until they approve it, so they can approve or reject each one. Confirm each approved automation in one line.
If the requester says the proposals miss, take what they say as the new ranking criterion and do another round of research; don't defend the first set.
