# Example Digest Output

Shows the three-tier Slack message architecture. Tier 1 goes in the channel,
Tiers 2-3 go in the thread.

---

## Tier 1: Channel Message

```
:star: *Canva Create 2026 — Product Change Reactions — April 10, 2026*
_~600 feedback items · 15 sources · last 30 days_

:red_circle: *Editor Redesign Backlash* — 700+ reports, 18% negative. Users can't find moved tools and are reverting to old workflows.
:large_orange_circle: *Styles & Layout Panel Confusion* — Zendesk tickets 3x normal. Users report the panel "simply doesn't appear" after cache clears.
:green_circle: *Templates Sentiment* — Mostly positive across App Store and surveys. Surface friction with post-redesign finishability.

:thread: _Details in thread_
```

---

## Tier 2: Thread — Topic Cards

### Reply 1

```
:red_circle: *Editor Redesign Backlash*

*What's happening:*
The Design-to-Templates rename and Styles relocation are the dominant friction points. Most users eventually find the new location but the initial confusion is driving significant support volume — 155 Zendesk tickets in 30 days. Sentiment skews neutral-to-negative, with users describing the change as "ridiculous" but often resolving once guided.

*Signal strength:*
700+ reports · 18% negative · Top channel: Zendesk Support

*Sharpest customer quote:*
> _"this new layout is way too hard to navigate. the old lay out was perfect, maybe we could have the option to switch to this layout of image editing tools if we choose? this has slowed down my working speed already today."_

*Suggested action:*
:point_right: Add a transitional tooltip or shortcut to the old Styles location. The redesign isn't broken — discoverability is. A small bridge could cut Zendesk volume significantly.

───────────────
```

### Reply 2

```
:large_orange_circle: *Styles & Layout Panel Confusion*

*What's happening:*
Users report the Styles panel "simply doesn't appear" after cache clears, browser switches, and support guidance. Zendesk tickets are 3x the normal baseline for this area. The core complaint is that the Styles tab is not in the design tab — it moved, but users can't find where.

*Signal strength:*
170+ reports · 22% negative · Top channel: Zendesk Support (78 tickets)

*Sharpest customer quote:*
> _"I want the styles tab back in the sidebar with the default color palettes and font combinations, like before, for any type of document. I pay for these features, and canva removed them."_

*Suggested action:*
:point_right: Consider a "missing Styles?" callout in the design tab that links users to the new location. 5+ support exchanges per ticket suggests self-service resolution is failing.

───────────────
```

### Reply 3

```
:green_circle: *Templates Sentiment*

*What's happening:*
Template feedback is 1,060 items split largely positive. Surveys and App Store show enthusiasm for surface improvements. The friction point is narrow: post-redesign finishability, where users find templates but struggle to complete edits with the relocated tools.

*Signal strength:*
1,060 reports · 6% negative · Top channels: Surveys, App Store

*Sharpest customer quote:*
> _"I am a paid plan user and I use canva professionally, recently, important tools like the image background have had changes to their workflow. without any prior notice, this directly impacts productivity."_

*Suggested action:*
:point_right: Communicate relevant editor changes via email or within the platform. The template experience itself is healthy — the drag is coming from upstream tool relocation.

───────────────
```

---

## Tier 3: Raw Data (optional)

Only included if user configures `show_raw_data: true`.

```
:bar_chart: *Source Breakdown — Editor Redesign Backlash*

• Zendesk Support — 155 items (14 pos · 107 neutral · 34 neg)
• Submit A Wish — 2,588 items (3 pos · 6,135 neutral · 636 neg)
• Always On Feedback — 621 items (89 pos · 380 neutral · 152 neg)
• Reddit — 58 items (4 pos · 7 neutral · 44 neg)
• App Store — 54 items (19 pos · 1 neutral · 34 neg)
```
