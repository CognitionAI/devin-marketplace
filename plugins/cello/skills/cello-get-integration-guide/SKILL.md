---
name: cello-get-integration-guide
description: Generate a tailored, step-by-step guide for integrating Cello (referral/attribution tracking) into a specific application. Use this whenever a developer says they want to "integrate Cello," "add Cello to my app," "set up referral tracking," or "add attribution tracking," especially when they haven't integrated it yet or are starting from scratch. Also trigger if someone asks "how do I add Cello to [React/Next.js/Rails/etc]" or pastes their codebase/repo and asks for an integration plan. This analyzes the actual app (frontend framework, mobile vs. web, payment gateway, signup flow) before generating the guide — it does not just paste the generic docs. Do not use this for debugging an *existing* integration (use cello-integration-health-check for that instead).
compatibility: Requires the Cello MCP server (cello_search_documentation, and ideally cello_get_integration_status for the final verification step). Works best with read access to the target codebase (package.json, requirements.txt, webhook handlers, etc.) so the stack can be detected automatically instead of asked about.
---

# Cello Integration Guide Generator

Produces a step-by-step Cello integration plan customized to the app you're actually integrating into — not a copy of the generic docs. The generic path (docs.cello.so/integration-overview) has 4 steps that apply to everyone, but steps 2 and 4 branch hard depending on the app's stack, and most of the actual work is picking the right branch.

## Step 1: Analyze the app

Before writing any guide, figure out:

1. **Platform**: Web app, mobile app (iOS/Android/React Native), or both?
2. **Frontend framework**: Plain JS/HTML, React, Vue, Angular, Next.js, etc. (Cello's referral component is a script tag + JS API, so it works with all of these — but the mount pattern differs, e.g. SPA re-render timing matters for custom launchers.)
3. **Signup flow**: Does the user sign up on a web form the app controls, via a form tool (HubSpot, Typeform), or via mobile?
4. **Payment/billing system**: Stripe, Chargebee, or something else (custom billing, Paddle, etc.)? And critically: is the gateway customer object created at signup, or only later at purchase/checkout? This timing question — not just "which gateway" — is what actually determines the step 4 path (see Step 2 below), so don't skip it even if Stripe/Chargebee is confirmed.
5. **Auth/user identity**: Where does a stable user ID (or email) live at signup time, that can be attached to Cello as the `ucc` (unique customer code) reference?
6. **Buying persona — user or organization?**: Does the app have organizations/teams/workspaces, and does the *purchase* happen at the org level rather than the individual level (e.g. a workspace admin pays for the whole team)? This determines whether attribution needs to run on the user or the organization, which changes what ID gets passed at several points — don't skip this even for straightforward B2B SaaS apps, since it's easy to assume user-level by default when the actual buyer is the org.
7. **New user discount wanted?**: Does the app want to offer referred users a discount at signup/checkout? This is optional and separate from the core 4 steps — ask if unclear rather than assuming yes or no.

**How to gather this:**
- If you have codebase access: check `package.json`/`requirements.txt`/`Gemfile` for frontend framework and payment SDKs (`stripe`, `chargebee`), grep for webhook handler routes, check for existing auth/session code.
- If you don't have codebase access, or something's ambiguous (e.g. multiple payment integrations found, or none): ask the developer directly rather than guessing. Getting the payment gateway wrong wastes their whole step 4.

## Step 2: Map findings to the 4 setup steps

Use `cello_search_documentation` to pull the exact, current content for each — don't rely on memory, since Cello's docs and snippets change. Map based on what Step 1 found:

| Setup step | Branch on |
|---|---|---|
| 1. Referral component | Web → JS quickstart. Mobile → iOS / Android / React Native SDK. |
| 2. Capture referral codes (`ucc`) on landing | Web signup → web signup flow guide. Mobile → mobile signup flow. Form tool → HubSpot/Typeform guide. |
| 3. Track signups | Same for everyone at this stage — POST /events or the tracking-signups guide — but the exact call site depends on where Step 1 found the signup happens (frontend vs backend). |
| 4. Track purchases | See three-way branch below. |

Step 4 has a real three-way branch — get this one right, it's the highest-cost step to redo:

1. **Stripe/Chargebee, gateway customer created at signup** → full prebuilt webhook quickstart (Stripe/Chargebee Webhook Quickstart). Fastest path, mostly config not code, ~1-2 days guided.
2. **Stripe/Chargebee, gateway customer created at purchase (not signup)** → use the Cello API directly for signup events, and only the Stripe/Chargebee webhook for purchase events. The gateway customer must carry `cello_ucc` (and `new_user_id` matching the `productUserId` used to boot the widget) as metadata at creation time — if the customer is created at purchase, that metadata has to be set right there, not inherited from an earlier signup step.
3. **Any other gateway** → generic tracking-purchases guide via the Cello API, called manually from the app's own payment success handler.

Say which of the three applies, explicitly and early — developers often assume "we use Stripe" alone determines the path, when actually *when* the customer object is created is what matters.

## User-level vs. organization-level attribution

If Step 1 found the buying persona is the organization (a workspace/team pays, not the individual), attribution must run at the org level — this touches the widget boot, the signup event, and the purchase event, not just step 4. Always call this out as its own consideration in the generated guide when it applies, since it's easy to wire only part of it and end up with inconsistent attribution.

- **Widget boot**: pass `orgIds` (the list of organizations the logged-in user belongs to) in the boot/token payload, alongside `productUserId`. This enables automatic attribution for org-based referrals — without it, Cello has no way to associate the individual user with their organization at boot time.
- **Signup event** (`new-signup` via Cello API — only relevant if you're not using the Stripe/Chargebee webhook path): set `payload.newUserId` to the **organization ID**, not the individual user's ID, when the referrer should be rewarded for organization account expansion rather than a single seat. The individual's own ID still goes in `context.newUser.id` (must match `productUserId` used to boot the widget) — only the top-level `newUserId` used for attribution switches to the org ID. Optionally also set `context.newUser.organizationId` alongside it.
- **Stripe/Chargebee path**: there's no separate "purchase event" to set fields on — metadata is set **once, on the customer object**, at creation (or update, for the purchase-first flow) via `new_user_organization_id` (Chargebee) or the equivalent Stripe customer metadata field, alongside `cello_ucc` and `new_user_id`. Every subsequent `invoice.paid`/`invoice-paid` webhook event inherits attribution from that customer record automatically — you don't touch anything per-purchase.
- **Cello API path** (no Stripe/Chargebee webhook — e.g. custom billing, or sending purchase events manually): here purchase events (`invoice-paid`, `charge-refunded`) genuinely are sent individually, and each one needs `payload.newUserId` set to the organization ID directly in that event's payload, the same way the signup event does.
- **Rule of thumb to state plainly in the guide**: wherever `newUserId` normally goes, the org ID goes there instead when attributing at the org level. Where that setting actually happens depends on the integration method — once on the customer object for Stripe/Chargebee, or per-event for the Cello API — so be explicit about which one applies rather than saying "purchase event" generically.

Ground this section in the live doc rather than memory (`cello_search_documentation` query on "organization level attribution"), and reference: https://docs.cello.so/attribution/introduction#how-it-works

## New user discounts (optional)

Only include this section if the developer wants to offer referred users a discount — it's a genuine add-on, not a required part of the 4-step setup, so don't assume it's wanted just because signup/purchase tracking is being built. Ask if it's unclear.

There are two independent halves — don't conflate them:

**1. Displaying the discount on the landing page.** Uses the Attribution JS methods already installed for step 2 (`getUcc`/`getReferrerName`). Add `getCampaignConfig()`, which returns `{ newUserDiscountPercentage, newUserDiscountMonth }`, and render it inline (banner/CTA copy) on the landing or signup page. This is purely cosmetic — it doesn't apply anything, it just shows the visitor what they'd get.

**2. Actually applying the discount at checkout.** This is a separate integration step that happens in the subscription platform, not in Cello:
   - First, discount coupons must be configured directly in Stripe/Chargebee/etc. (plan-level, with coupon IDs stored in the app's config) — this is a one-time platform setup step, not something Cello does.
   - Then, at the moment of subscription creation, the app needs to check whether the new user is a Cello referral and, if so, apply the matching coupon. There are three ways to check eligibility, and the developer only needs one:
     - **New User Reward API** (`GET /new-users/{productUserId}/reward`) — the recommended, explicit approach. Call it before checkout (i.e. before the user/org hits the subscription/payment step) with the user's `productUserId`. Returns `eligible`, and if true, `reward.percentage`/`reward.intervalCount` plus the `referralUcc` and campaign info. This is the cleanest option because it doesn't require the app to have already stored or synced any referral data itself.
     - **Check the Stripe/Chargebee customer object directly** — if `cello_ucc` was already added to the customer at signup/creation (per the attribution setup in earlier steps), the app can just read it off the customer record it already has, with no extra API call.
     - **Check the app's own stored signup data** — if the app cached the `ucc`/eligibility info itself during signup tracking, it can rely on that instead of calling anything at checkout time.
   - This eligibility check is optional infrastructure, not a hard requirement — say this explicitly in the guide: the Reward API exists to make it easier when the app doesn't already have the referral data on hand at checkout, not because it's the only way to do this.
   - Apply the resolved coupon at subscription creation: Stripe uses the `discounts` array or `coupon` parameter on the Checkout Session; Chargebee applies `coupon_ids` on the Subscription (or via Hosted Pages) — not at customer creation, at subscription creation specifically.

Reference these when generating this section: https://docs.cello.so/guides/user-experience/new-user-discounts, https://docs.cello.so/attribution/apply-discounts, https://docs.cello.so/api-reference/new-users/get-reward

## Step 3: Generate the guide

Output an ordered, numbered guide — not a dump of every doc link. For each of the 4 steps:

- State what it does in one line and why it matters for that specific app (e.g. "Since you're using Next.js, mount the referral launcher in a persistent layout component, not per-page, so the SPA client re-render on route change doesn't fight fresh initialization of it.")
- Give the concrete action (code snippet, config location, or webhook URL to register) pulled from the doc content fetched in Step 2 — not paraphrased from general Cello knowledge, since exact field names and snippet syntax matter here.
- Flag any prerequisite from a prior step it depends on (e.g. step 3 needs the `ucc` captured in step 2 to actually attribute the signup).

End with a verification note: once implemented, they can run an integration health check (the `cello-integration-health-check` skill, if installed) against `cello_get_integration_status` and `cello_get_events` to confirm signups/purchases are actually being attributed — don't just trust that the code is right.

## Output format

```
## Cello Integration Plan for [app name/stack]

**Detected:** [platform] · [frontend framework] · [payment gateway] · [signup flow] · [user-level or org-level attribution]
**Fast path available:** [yes/no — Stripe/Chargebee webhook note if relevant]

### Step 1: Referral Component
[why this shape for this app]
[snippet/action]

### Step 2: Capture referral codes
...

### Step 3: Track signups
...

### Step 4: Track purchases
...

### New user discounts (if applicable)
[landing page display + checkout-time eligibility check + coupon application]

### Verify it worked
Run an integration health check once deployed to confirm events are actually attributing.
```

## Edge cases

- **Mixed or unclear payment setup** (e.g. Stripe SDK present but also custom invoicing code): ask rather than assume — this is the highest-cost branch to get wrong.
- **No payment gateway at all yet (pre-monetization app)**: still do steps 1-3, note that step 4 can be added later, and point to the generic tracking-purchases guide as the eventual path once billing exists. Or recommend to reach out to Cello Support to clarify.
- **Docs conflict with what's actually in `cello_search_documentation`'s live result**: always trust the live fetch over anything remembered from a prior guide generation — Cello's docs change.
- **Org-level attribution requested but only some touchpoints wired** (e.g. org ID used in the purchase event but the widget still boots without `orgIds`): flag the gap explicitly rather than treating partial org-level setup as done — inconsistent attribution across the three touchpoints is a common failure mode here.
