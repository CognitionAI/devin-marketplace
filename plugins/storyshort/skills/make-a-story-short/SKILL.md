---
name: make-a-story-short
description: Turn a story idea into a narrated, captioned faceless short video on the user's StoryShort account. Agree the script scene by scene, save it as a free draft, show the credit price StoryShort returns, and render only after the user says yes. Use when the user wants to make, draft or render a story video, YouTube Short, TikTok or Reel with StoryShort.
license: MIT
compatibility: Needs the StoryShort MCP server (https://storyshort.app/api/mcp) connected and signed in. Rendering spends credits from the user's own StoryShort account.
---

# Make a story short with StoryShort

You turn an idea into a short video in four steps: idea, script, draft, render. Nothing is rendered or charged until the user has seen the script and the price and has said yes. StoryShort is at storyshort.app (not storyshort.ai, a different company).

## Ground rules

- Credits are the user's money. Never call `render_draft` or `create_video` without an explicit yes to the exact price in this conversation. A yes to an earlier question is not approval to render.
- Quote every price, balance and limit from tool output, as StoryShort returned it. Never write a credit number from memory, never estimate one yourself, never convert credits to money.
- The narration you save is spoken exactly as written. Proofread it yourself: spelling, numbers, names.
- Do not promise results. Say what the video is, not how many people will watch it.
- Buying credits happens on the StoryShort website. If the balance is short, say how many credits are needed and how many the account has, and let the user decide.
- If the StoryShort tools are not available, tell the user to connect the StoryShort MCP server (https://storyshort.app/api/mcp) in Devin (Customize, then MCPs) and sign in to StoryShort when asked. You cannot sign in for them.

## 1. Idea

1. Call `list_niches` (read-only) if you need the valid niches, art styles, qualities and durations. Use what it returns; do not hardcode them.
2. Ask only for what you do not know: the story or topic, the narration language and how long it should be (`draft_video` accepts a target of 15, 30, 60 or 90 seconds; 90 needs a paid plan). If the user has only a topic, propose three hook-first angles in one line each and let them pick.

## 2. Script

Write the script scene by scene and show it before saving anything. Use a table with one row per scene:

| # | Narration (spoken, verbatim) | Visual (what the viewer sees) |
|---|---|---|

- The first sentence is the hook: a real question, claim or tension, not a greeting.
- One idea per scene, short sentences, spoken language. A draft has 1 to 12 scenes.
- Each visual is a concrete image description, not a feeling.
- No real or famous people, no fake quotes, no brand logos or protected characters, no sexual content. StoryShort refuses these and so do you.
- For health, money or legal topics keep to general information and say so in the narration; do not promise outcomes.

Ask: "Want to change anything before I save it as a draft?"

## 3. Draft (free)

1. Call `draft_video` with the topic and the options the user chose (title, duration, art style). It writes a script and scenes without rendering or charging. It runs the script writer once, needs a balance that can pay for a render and is limited per hour, so do not call it repeatedly. If the user's agreed text differs from what it returned, replace the scenes with `update_draft` (1 to 12 scenes, narration in `scriptText`, optional `visualPrompt`).
2. Report what the tool returned: the `draftId`, the scenes, the length check and the render price. Use `get_draft` to re-read the current state.
3. Change one scene with `revise_scene` (scene numbers start at 1) or all of them with `update_draft`. Drafts can only be edited until they are rendered. Show the updated scenes again until the user is happy.

## 4. Price, approval, render

1. Read the price from the draft (`get_draft`) and the balance from `get_credit_balance`. Both are free.
2. Say it plainly, using their numbers: "Rendering this draft will charge N credits. Your balance is M."
3. Ask: "Render it?" and wait for a clear yes.
4. On yes, call `render_draft` with the `draftId` and `confirmCredits` set to exactly the approved price. Without `confirmCredits` it answers QUOTE_REQUIRED with the price and charges nothing; a changed price is refused (PRICE_CHANGED) rather than charged. Calling it again on a draft already rendering starts nothing new.
5. Rendering is asynchronous. Poll `get_video` every 20 to 30 seconds until the status is COMPLETED or FAILED. When it is COMPLETED, give the user the `videoUrl`. If it FAILED, relay the message as written. StoryShort may retry a failed render automatically; `cancel_video` stops that and also cancels a draft or queued video that has not started rendering.

A new account that has not made its first video yet may get a watermarked first video, labelled AI-generated, under conditions the tools state. Report what the tool says; do not promise it.

## 5. After the video (only if asked)

- Posting: `get_connection_status` and `list_social_accounts` show which platforms are connected; `publish_video` posts a COMPLETED video. Post only when the user asks, to the platform they name, and relay what the tool says about visibility.
- Past videos: `list_videos`, `get_video`.
- Do not create series, schedules or auto-post unless asked. For a multi-episode story use the `plan-a-drama-season` skill.

## What you can say about StoryShort

StoryShort makes narrated faceless shorts: AI-generated scene images, an AI narration voice and captions, assembled into a vertical video. Because AI makes the images and the voice, remind the user to switch on the platform's AI-content label when they post. Do not claim that a video will be monetised, go viral or earn anything.
