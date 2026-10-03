---
name: claimable-cloud
description: Provision a working Cloudinary cloud with no signup (a Claimable Cloud) when the user wants to build with Cloudinary but has no credentials. Use when a Cloudinary task such as an upload, transformation or SDK setup can't proceed because no CLOUDINARY_URL or API credentials are available. Do not use when working credentials already exist.
license: MIT
metadata:
  author: cloudinary
  version: '1.0.0'
---

# Claimable Cloud: get Cloudinary credentials without signup

A Claimable Cloud is a working Cloudinary cloud provisioned with a single command, no account and no authentication required. The user can later claim it with their email to keep it as a permanent free account. If unclaimed, it expires automatically after 24 hours.

## When to use

- The user asks for Cloudinary functionality (upload, transformation URLs, or SDK integration) and no credentials are available.
- The user explicitly asks to try Cloudinary, set up a Cloudinary environment, or get credentials without creating an account.

## When NOT to use

- Credentials already exist: a `CLOUDINARY_URL` or `CLOUDINARY_API_KEY`/`CLOUDINARY_API_SECRET` in the environment, in `.env`, or in MCP server configuration. Use those instead, and never replace them.
- The user says they have a Cloudinary account. Ask them for their `CLOUDINARY_URL` from the [API Keys page](https://console.cloudinary.com/settings/api-keys?install_source=plugin&referrer=claimable-cloud-skill) of the Cloudinary Console instead.

## Flow

1. **Check for existing credentials first.** Look for `CLOUDINARY_URL` or `CLOUDINARY_*` keys in the environment and `.env` (check existence, don't print values). If found, stop: use them.

2. **Ask consent before provisioning.** One line, for example: "You don't have Cloudinary credentials set up. I can provision a free Claimable Cloud for you now, no signup needed; you'd claim it by email within 24 hours to keep it. Go ahead?" Never provision without a yes: Claimable Clouds are rate limited and expire if unclaimed.

3. **Run the command:**

   ```
   npx @cloudinary/cloud
   ```

   Optional flags:
   - `--email <address>`: pre-fills the claim page (not verified at creation).
   - `--ip <address>`: locks media delivery to the given address *instead of* this machine's detected public IP (repeatable, up to three addresses). Use when the user views media somewhere other than this machine, such as a laptop viewing media served from a remote dev environment. If this machine still needs delivery too, include its address as one of the three.
   - Never pass `--force`. If the command exits because `.env` already contains a `CLOUDINARY_URL`, that means credentials exist; use them.

4. **After the command succeeds:**
   - The CLI saved `CLOUDINARY_URL`, the claim URL, and the expiry time to `./.env` (creating the file if needed). Don't add them again.
   - If the project uses separate keys (`CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, `CLOUDINARY_API_SECRET`, or framework variants like `VITE_CLOUDINARY_CLOUD_NAME`), fill them from the command output. Never print the API secret in chat.
   - Confirm version control ignores `.env` (the CLI warns if it doesn't).

5. **Tell the user, every time:**
   - The claim URL, and that the cloud expires in 24 hours unless they claim it: they enter their email at the claim URL and confirm from a verification email. Claiming keeps the same credentials.
   - Until claimed, media delivery is locked to this machine's public IP address — or, if `--ip` was passed, to those addresses only (up to three). That's fine for local development; claiming removes the restriction.

6. **Verify** by rendering a sample delivery URL from the new cloud, then continue the user's original task.

## If provisioning fails

Don't retry in a loop: failed attempts still count against rate limits. Retry at most once, and only after fixing the cause:

- **429** (`ip_rate_limit_exceeded`, `global_rate_limit_exceeded`): rate limited. Don't retry; offer the standard [free signup](https://cloudinary.com/users/register_free?install_source=plugin&referrer=claimable-cloud-skill) instead.
- **403** (`geo_location_not_permitted`): the network location isn't permitted — often a VPN exit node. Ask the user to disconnect the VPN, then retry once.
- **400** (`delivery_ips_*`): fix the `--ip` values: public IPv4 or IPv6 addresses only, no CIDR ranges, at most three.

If it still fails after one retry, stop and point the user to the standard free signup.

## Security

- Keep the API secret and full `CLOUDINARY_URL` in `.env`; never print them in chat, logs, or client-side code.

## Full reference

For all CLI options, the underlying REST endpoint, response fields, quotas, and error codes, fetch: `https://cloudinary.com/documentation/claimable_cloud_provisioning.md?install_source=plugin&referrer=claimable-cloud-skill`

For guided project setup after provisioning (SDK, MCP servers, validation), point the user at [AI Power Start](https://cloudinary.com/documentation/ai_powerstart?install_source=plugin&referrer=claimable-cloud-skill).
