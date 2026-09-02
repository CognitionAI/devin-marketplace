#!/usr/bin/env bash
#
# preflight.sh — sanity checks before a GitLab→Unleash feature flags migration.
#
# Usage: preflight.sh <target-dir> [--mode api|import|mcp] [--frontend]
#
#   <target-dir>  app/service being migrated
#   --mode        provisioning mechanism (default: api)
#                   api    — direct Admin API: requires an automation token
#                   import — AI generates import files only: no credentials
#                   mcp    — Unleash MCP server does the writes
#   --frontend    browser-facing app: also check the frontend token/API
#
# Always uses UNLEASH_URL. Automation token for --mode api: UNLEASH_API_TOKEN
# (PAT or service account; falls back to legacy UNLEASH_ADMIN_TOKEN with a
# deprecation warning). Exit 0 = all checks passed; exit 1 = failure.

set -euo pipefail

fail=0
ok()   { printf 'OK   %s\n' "$1"; }
bad()  { printf 'FAIL %s\n' "$1" >&2; fail=1; }
warn() { printf 'WARN %s\n' "$1" >&2; }

target="${1:-}"
mode="api"
frontend=0
shift || true
while [[ $# -gt 0 ]]; do
  case "$1" in
    --mode) mode="${2:?--mode needs api|import|mcp}"; shift 2 ;;
    --frontend) frontend=1; shift ;;
    *) echo "unknown argument: $1" >&2; exit 1 ;;
  esac
done

if [[ -z "$target" ]]; then
  echo "usage: preflight.sh <target-dir> [--mode api|import|mcp] [--frontend]" >&2
  exit 1
fi
case "$mode" in api|import|mcp) ;; *) echo "mode must be api|import|mcp" >&2; exit 1 ;; esac

# --- tooling ----------------------------------------------------------------
for tool in curl jq; do
  if command -v "$tool" >/dev/null 2>&1; then ok "$tool on PATH"; else bad "$tool not on PATH"; fi
done

# --- environment ------------------------------------------------------------
if [[ -n "${UNLEASH_URL:-}" ]]; then ok "UNLEASH_URL is set"; else bad "UNLEASH_URL is not set"; fi

api_token=""
if [[ "$mode" == "api" ]]; then
  if [[ -n "${UNLEASH_API_TOKEN:-}" ]]; then
    api_token="$UNLEASH_API_TOKEN"; ok "UNLEASH_API_TOKEN is set (PAT/service account)"
  elif [[ -n "${UNLEASH_ADMIN_TOKEN:-}" ]]; then
    api_token="$UNLEASH_ADMIN_TOKEN"
    warn "using UNLEASH_ADMIN_TOKEN — admin tokens are deprecated; prefer a PAT (OSS) or service account (Enterprise) in UNLEASH_API_TOKEN. Proceed only if the user explicitly supplied/authorized this token; otherwise stop and ask."
  else
    bad "mode=api needs UNLEASH_API_TOKEN (or legacy UNLEASH_ADMIN_TOKEN)"
  fi
elif [[ "$mode" == "mcp" ]]; then
  # A locally-configured server needs these; a session-connected or remote MCP
  # server may not surface them here — hence warnings, not failures.
  [[ -n "${UNLEASH_BASE_URL:-}" ]] || warn "UNLEASH_BASE_URL not set — fine if the MCP server is already connected to the session (check the MCP tool list / claude mcp list)"
  [[ -n "${UNLEASH_PAT:-}" ]] || warn "UNLEASH_PAT not set — fine if the MCP server is already connected or uses remote OAuth"
else
  ok "mode=import — no Unleash credentials required (files are applied by a human/CI)"
fi

# The app's own runtime token; may legitimately be created during Phase 4.
if [[ -z "${UNLEASH_CLIENT_TOKEN:-}" ]]; then
  warn "UNLEASH_CLIENT_TOKEN not set — the app needs a project+environment-scoped backend token; it can be created during provisioning (Phase 4 token step)"
else
  ok "UNLEASH_CLIENT_TOKEN is set"
fi
if (( frontend )) && [[ -z "${UNLEASH_FRONTEND_TOKEN:-}" ]]; then
  warn "UNLEASH_FRONTEND_TOKEN not set — browser apps need a frontend token; it can be created during provisioning (Phase 4 token step)"
fi

# Not required — Phase 2 falls back to code/manifests — but say so up front.
if [[ -z "${GITLAB_API_TOKEN:-}" ]]; then
  warn "GITLAB_API_TOKEN not set — flag inventory will fall back to code/manifests"
fi
(( fail )) && { echo "preflight: aborting before network checks" >&2; exit 1; }

# --- target server ----------------------------------------------------------
# UNLEASH_URL may or may not include the /api suffix; normalize both bases.
root="${UNLEASH_URL%/}"; root="${root%/api}"
api="$root/api"

if curl -fsS --max-time 10 "$root/health" | jq -e '.health == "GOOD"' >/dev/null 2>&1; then
  ok "Unleash health at $root/health"
else
  if [[ "$mode" == "import" ]]; then
    warn "Unleash not reachable at $root/health — acceptable in import mode (governed target); verification will be deferred to whoever applies the files"
  else
    bad "Unleash health check failed at $root/health"
  fi
fi

if [[ "$mode" == "api" && -n "$api_token" ]]; then
  if curl -fsS --max-time 10 -H "Authorization: $api_token" "$api/admin/projects" \
      | jq -e '.projects | length >= 1' >/dev/null 2>&1; then
    ok "automation token accepted by $api/admin/projects"
  else
    bad "automation token rejected by $api/admin/projects (auth or permission)"
  fi
fi

if (( frontend )) && [[ -n "${UNLEASH_FRONTEND_TOKEN:-}" ]]; then
  if curl -fsS --max-time 10 -H "Authorization: $UNLEASH_FRONTEND_TOKEN" "$api/frontend" >/dev/null 2>&1; then
    ok "frontend token accepted by $api/frontend"
  else
    bad "frontend token rejected by $api/frontend"
  fi
fi

# --- target directory -------------------------------------------------------
if [[ -d "$target" ]]; then
  ok "target dir $target exists"
  manifests=(package.json go.mod pom.xml build.gradle Gemfile composer.json
             requirements.txt pyproject.toml)
  found=""
  for m in "${manifests[@]}"; do
    [[ -f "$target/$m" ]] && found+="$m "
  done
  if compgen -G "$target"/*.csproj >/dev/null; then found+="*.csproj "; fi
  if [[ -n "$found" ]]; then
    ok "stack manifest(s): $found"
  else
    # Not fatal: plain shell/ops targets have no manifest.
    warn "no stack manifest found in $target — stack detection falls back to file extensions"
  fi
else
  bad "target dir $target does not exist"
fi

if (( fail )); then
  echo "preflight: FAILED" >&2
  exit 1
fi
echo "preflight: all checks passed (mode=$mode)"
