---
name: auth
description: Configure Browserless API authentication. Set up your API token and region for all Browserless skills. Use when the user wants to authenticate, set their token, configure their API region, or check auth status.
disable-model-invocation: true
---

# Browserless Auth

Configure authentication for all Browserless API skills. The user's request is: "$ARGUMENTS"

## Subcommands

Based on `$ARGUMENTS`, do one of the following:

### If no arguments or "setup" — Interactive Setup

1. Ask the user for their Browserless API token. They can get one at https://www.browserless.io
2. Ask which API region they want to use:
   - **SFO** (US West, default): `https://production-sfo.browserless.io`
   - **LON** (London): `https://production-lon.browserless.io`
   - **AMS** (Amsterdam): `https://production-ams.browserless.io`
   - **Custom URL**: (prompt for the full API URL)
3. Create the config directory and write the config file:

```bash
mkdir -p ~/.browserless
cat > ~/.browserless/.env << 'ENVEOF'
BROWSERLESS_TOKEN=<their-token>
BROWSERLESS_API_URL=<their-chosen-url>
ENVEOF
chmod 600 ~/.browserless/.env
```

4. Validate the token by making a test API call:

```bash
source ~/.browserless/.env
curl -s -X POST "${BROWSERLESS_API_URL}/map?token=${BROWSERLESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "limit": 1}'
```

If the response contains `"success": true`, tell the user auth is configured and working. If it fails (401, 403, or connection error), tell them the token may be invalid and offer to retry.

### If "status" — Check Current Config

Check if authentication is configured:

```bash
if [ -n "$BROWSERLESS_TOKEN" ]; then
  echo "Token set via environment variable"
  echo "Token: ${BROWSERLESS_TOKEN:0:8}..."
elif [ -f ~/.browserless/.env ]; then
  source ~/.browserless/.env
  echo "Token loaded from ~/.browserless/.env"
  echo "Token: ${BROWSERLESS_TOKEN:0:8}..."
  echo "API URL: ${BROWSERLESS_API_URL:-https://production-sfo.browserless.io}"
else
  echo "Not configured"
fi
```

Report the status to the user. If configured, show the first 8 characters of the token (masked) and the API URL. If not configured, suggest running `/browserless:auth` to set up.

### If "clear" — Remove Saved Credentials

Remove the saved config:

```bash
rm -f ~/.browserless/.env
echo "Browserless credentials removed."
```

Confirm to the user that credentials have been cleared.

### If "region" — Change Region Only

Update just the API URL in the existing config:

1. Ask which region (SFO, LON, or custom URL)
2. Update the `BROWSERLESS_API_URL` line in `~/.browserless/.env`
