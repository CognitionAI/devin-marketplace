---
name: fuse
description: Use when the user wants to find prospects or companies, build or enrich contact lists, watch for buying signals (job changes, hiring, funding), research an account before a call, or create and run email or LinkedIn outreach with Fuse. Covers credit-aware search and enrichment, draft-first campaigns, and signal monitors.
---

# Fuse

Fuse is a B2B prospecting and outreach platform. The Fuse MCP server (`https://mcp.fuseai.com`) gives you tools to search people and companies, build and enrich lists, monitor buying signals, research accounts, and create email, LinkedIn and calling campaigns. Every action runs in the signed-in user's own Fuse workspace and uses their credits.

## Ground rules

1. **Check credits before large jobs.** Searches, enrichment and research spend the user's Fuse credits. Before anything that touches more than a handful of records, check the balance and prices (e.g. `get_credits_balance`, `get_credit_prices`) and tell the user the expected cost.
2. **Preview, then save.** Run a search and show a sample before saving hundreds of results to a list or enriching them. Ask before scaling up.
3. **Campaigns are drafts until the user says launch.** Create, edit and preview campaigns freely, but only launch or approve sending when the user explicitly asks. Never send email or LinkedIn messages on your own initiative.
4. **Confirm before destructive or outward actions.** Deleting lists, disconnecting accounts, pushing to a CRM, or sending a message all need a clear yes.
5. **Use IDs from tool results.** Never guess list, campaign or contact IDs. Look them up first.

## Common workflows

**Build a targeted list**
1. Turn the user's description into filters (e.g. `build_prospect_search_filters`).
2. Search (`search_people` or `search_companies`) and show a short sample with the total count.
3. On approval, save to a new list (e.g. `search_and_save_people_to_list`), then enrich emails or phones if asked.

**Act on a buying signal**
- Funding, hiring and job changes are tracked with signal monitors (e.g. `create_funding_announcement_monitor`, `create_job_posting_monitor`, `create_job_changes_watcher_monitor`). Confirm the criteria and the destination list before creating one.
- To act on a signal now, search for matching companies, find the right person at each, enrich them and draft outreach.

**Run outreach**
1. Pick or build the target list.
2. Generate a sequence (email, LinkedIn or both) personalised to each contact's role and company.
3. Show the user the steps and a sample message. Adjust tone and length as requested.
4. Leave the campaign as a draft. Launch only on an explicit request.

**Prepare for a meeting**
- Combine contact enrichment, web research and the user's own email and call history with that contact or company. Summarise background, recent company news and open threads.

## Tips

- Ask one clarifying question when the target is vague (role, company size, region, industry). Good filters save credits.
- Long-running jobs (enrichment, deep research, exports, campaign generation) can be asynchronous. Start them, tell the user, and check status rather than waiting silently.
- Docs: https://docs.fuseai.com/mcp/connect and https://docs.fuseai.com/mcp/tools
