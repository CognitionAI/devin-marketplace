---
name: make-a-faceless-short
description: Turn an idea into a narrated, captioned faceless short video on the user's AutoShort account. Agree the script scene by scene, save it as a free draft, show the credit price from AutoShort, and render only after the user says yes. Use when the user wants to make, draft or render a short video, YouTube Short, TikTok or Reel with AutoShort.
license: MIT
compatibility: Needs the AutoShort MCP server (https://autoshort.org/api/mcp) connected and signed in. Rendering spends credits from the user's own AutoShort account.
---

# Make a faceless short with AutoShort

You turn an idea into a short video in four steps: idea, script, draft, render. Nothing is rendered or charged until the user has seen the script and the price and has said yes.

## Ground rules

- Credits are the user's money. Never call `autoshort_render_draft` (or any `autoshort_generate_*` tool) without an explicit yes to the exact price in this conversation. A yes to an earlier question is not approval to render.
- Quote every price, balance and limit from tool output, as AutoShort returned it. Never write a credit number from memory, never estimate one yourself, never convert credits to dollars unless a tool returned the dollars.
- Narration is read aloud word for word, and AutoShort never rewrites it. Proofread it yourself before saving: spelling, numbers, names.
- Do not promise results. Say what the video is, not how many people will watch it.
- Do not buy credits, set up auto-recharge or open a checkout. If the balance is short, say so and let the user decide (see "If the balance is short").
- If the AutoShort tools are not available, tell the user to connect the AutoShort MCP server in their app's MCP settings (Cursor and Devin: Customize, then MCPs; Grok Build: `/mcps`) and sign in to AutoShort when asked. You cannot sign in for them.

## 1. Idea

1. If you have not yet this session, call `autoshort_get_capabilities` (free). Use what it returns for limits, durations, languages and art styles. Do not hardcode them.
2. Ask only for what you do not know: the topic, who it is for, the narration language, and how long it should be. If the user has only a topic, propose three hook-first angles in one line each and let them pick.
3. If they want a starting shape, `autoshort_list_templates` lists the template gallery (free) and `autoshort_list_niches` lists the niches. Optional, never required.

## 2. Script

Write the script scene by scene and show it before saving anything. Use a table with one row per scene:

| # | Narration (read aloud, verbatim) | Visual (what the viewer sees) |
|---|---|---|

Guidelines that make a better short:

- The first sentence is the hook. It should be a real question, claim or tension the viewer wants resolved, not a greeting.
- One idea per scene, short sentences, spoken language.
- Each visual is a concrete shot description ("close-up of hands holding a coffee and a planner, morning light"), not a feeling.
- No real or famous people, no brand logos or protected characters, no sexual content, nothing about children's faces. AutoShort refuses these and so do you.
- Claims must be ones you could defend. For health, money or legal topics, keep to general information and say so in the narration instead of promising outcomes.

Ask: "Want to change anything before I save it as a draft?" Apply edits, show the table again.

## 3. Draft (free)

1. Call `autoshort_draft_video` with `scenes[]` exactly as agreed (and the language, art style, title and length the user chose). Saving a draft from `scenes[]` is free and renders nothing.
2. Report what the tool returned: `draftId`, the scenes, the estimated length, the estimated credits and every entry in `warnings[]`. If a warning says the narration will not fit the requested length, show it and offer a fix (shorter narration or a longer target).
3. Apply changes with `autoshort_update_draft`, then re-read with `autoshort_get_draft`. Show the updated scenes again. Repeat until the user is happy.
4. To change one scene of an already rendered video instead, `autoshort_revise_scene` creates a new draft. The original video is untouched and nothing is charged until you render the new draft.

## 4. Price, approval, render

1. Call `autoshort_estimate_cost` with `{ "draftId": "<the draft id>" }` and `autoshort_get_credit_balance`. Both are free.
2. Say it plainly, using their numbers: "Rendering this draft will charge N credits. Your balance is M." Mention the length and the voice, language and art style that will be used.
3. Ask: "Render it?" Wait for a clear yes. Silence, "looks good" about the script, or "ok" to a different question is not a yes.
4. On yes, call `autoshort_render_draft` once with the `draftId`. The tool is retry-safe: a repeated call returns the first submission and does not charge twice. Do not call it again unless the first call returned an error that says nothing was submitted.
5. Rendering is asynchronous. Poll `autoshort_get_video` with the video id every 20 to 30 seconds until the status is COMPLETED or FAILED. If it reports a `blockedReason`, stop polling and tell the user what it says. When it is COMPLETED, give them the video link the tool returned. If it FAILED, relay the message as written and check `autoshort_get_credit_balance` so you can tell the user what the account shows.

### If the balance is short

Say how many credits are needed and how many the account has, both from the tools. Do not call `autoshort_buy_credits` or `autoshort_setup_auto_recharge`. If the user asks how to add credits, `autoshort_get_buy_credits_url` returns a checkout link for them to open themselves, and they pay on the checkout page, not through you. You can also suggest a shorter draft; edit it with `autoshort_update_draft` and price it again.

## 5. After the video (only if asked)

- Posting: `autoshort_get_connection_status` shows whether YouTube, TikTok or another platform is connected; `autoshort_publish_video` posts a finished video. Only post when the user asks, to the platform they name, and say what the tool says about drafts versus public posts.
- Past videos and status: `autoshort_list_videos`, `autoshort_get_video`. A video that has not started rendering yet (status PENDING) can be cancelled with `autoshort_cancel_video`, which asks the user to confirm because it is destructive; the tool refuses once rendering has started.
- Do not create series, schedules or webhooks unless asked. For a multi-episode story use the `plan-a-series` skill.

## What you can say about AutoShort

AutoShort makes faceless shorts: AI-generated images (or the user's own images), a narration voice and captions, assembled into a vertical video. Because AI makes the images and the voice, remind the user to switch on the platform's AI-content label when they post. Do not claim that a video will be monetised, will go viral or will earn anything.
