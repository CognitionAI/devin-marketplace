#!/usr/bin/env bash
# Copyright 2026 Anthropic PBC
# SPDX-License-Identifier: Apache-2.0
# search hubspot crm records with curl + jq: build the filterGroups/sorts/query body, post to
# /crm/v3/objects/{type}/search, follow paging.next.after through every page up to a row cap,
# surface the {"status":"error",...} envelope verbatim, and emit tsv or jsonl. generic to any
# hubspot account — everything instance-specific comes from env vars or flags.

set -euo pipefail

usage() {
  cat <<'EOF'
usage:
  hs_search.sh --object TYPE [options]

options:
  --object TYPE          object type to search: contacts, companies, deals, tickets, or any
                         object type name / objectTypeId (required)
  --query TEXT           free-text phrase matched across the type's default searchable properties
  --filter PROP:OP:VAL   property filter, repeatable; all filters are ANDed in one filterGroup.
                         OP is uppercased. IN / NOT_IN take a comma list (PROP:IN:v1,v2,...)
                         and map to a values array — for string properties the values must be
                         lowercase; BETWEEN takes PROP:BETWEEN:low,high and
                         maps to value + highValue; HAS_PROPERTY / NOT_HAS_PROPERTY take no
                         value; every other operator takes a single value.
  --properties LIST      comma-separated property names to request and emit as tsv columns.
                         defaults: contacts -> email,firstname,lastname,createdate; companies ->
                         name,domain; deals -> dealname,amount,dealstage,closedate; tickets ->
                         subject,hs_pipeline_stage,hs_ticket_priority. required for any other
                         object type.
  --sort PROP[:desc]     sort by one property; append :desc for descending (default ascending)
  --limit N              stop after N total rows (default 100; 0 = fetch everything — note the
                         api hard-caps any search at 10000 results)
  --page-size N          rows per request page, max 200 (default 100)
  --json                 emit one json object per record (jsonl) instead of tsv
  -h, --help             show this help

environment:
  HUBSPOT_ACCESS_TOKEN   bearer token; injected by the runtime, so the placeholder default is fine
  HUBSPOT_BASE_URL       api root override (default https://api.hubapi.com)

output:
  records on stdout — tsv with a header row (id then each requested property) by default, or
  jsonl with --json (one raw result object per line). nulls become empty strings in tsv; nested
  values are emitted as json. total match count, fetched count, and any truncation warning go to
  stderr.

exit codes:
  0 success    1 request failed, api error, or bad arguments
EOF
}

err() { printf '%s\n' "$*" >&2; }

command -v curl >/dev/null || { err "curl is required"; exit 1; }
command -v jq >/dev/null || { err "jq is required"; exit 1; }

BASE_URL="${HUBSPOT_BASE_URL:-https://api.hubapi.com}"
TOKEN="${HUBSPOT_ACCESS_TOKEN:-placeholder}"
OBJECT=""
QUERY=""
FILTERS='[]'
PROPS=""
SORT_PROP=""
SORT_DIR="ASCENDING"
LIMIT=100
PAGE_SIZE=100
FORMAT=tsv

# require_int FLAG VALUE — flags that take a count must get a non-negative integer
require_int() {
  case "$2" in
    ''|*[!0-9]*) err "$1 needs a non-negative integer, got '${2:-nothing}'"; exit 1 ;;
  esac
}

while [ $# -gt 0 ]; do
  case "$1" in
    --object)
      if [ -z "${2:-}" ]; then err "--object needs an object type"; exit 1; fi
      OBJECT="$2"; shift 2 ;;
    --query)
      if [ -z "${2:-}" ]; then err "--query needs a text value"; exit 1; fi
      QUERY="$2"; shift 2 ;;
    --filter)
      SPEC="${2:-}"
      PROP="${SPEC%%:*}"
      REST="${SPEC#*:}"
      if [ -z "$PROP" ] || [ "$PROP" = "$SPEC" ]; then
        err "bad --filter '$SPEC' (expected PROP:OP[:VALUE], e.g. lifecyclestage:EQ:lead)"
        exit 1
      fi
      RAW_OP="${REST%%:*}"
      OP="$(printf '%s' "$RAW_OP" | tr '[:lower:]' '[:upper:]')"
      if [ "$RAW_OP" = "$REST" ]; then VAL=""; else VAL="${REST#*:}"; fi
      case "$OP" in
        IN|NOT_IN)
          if [ -z "$VAL" ]; then
            err "--filter ${PROP}:${OP} needs a comma-separated value list"; exit 1
          fi
          FILTERS="$(jq -c --arg p "$PROP" --arg o "$OP" --arg v "$VAL" \
            '. + [{propertyName: $p, operator: $o, values: ($v | split(","))}]' <<<"$FILTERS")"
          ;;
        BETWEEN)
          LO="${VAL%%,*}"; HI="${VAL#*,}"
          if [ -z "$VAL" ] || [ "$LO" = "$VAL" ] || [ -z "$LO" ] || [ -z "$HI" ]; then
            err "--filter ${PROP}:BETWEEN needs low,high (e.g. amount:BETWEEN:100,500)"; exit 1
          fi
          FILTERS="$(jq -c --arg p "$PROP" --arg o "$OP" --arg lo "$LO" --arg hi "$HI" \
            '. + [{propertyName: $p, operator: $o, value: $lo, highValue: $hi}]' <<<"$FILTERS")"
          ;;
        HAS_PROPERTY|NOT_HAS_PROPERTY)
          FILTERS="$(jq -c --arg p "$PROP" --arg o "$OP" \
            '. + [{propertyName: $p, operator: $o}]' <<<"$FILTERS")"
          ;;
        *)
          if [ -z "$VAL" ]; then
            err "--filter ${PROP}:${OP} needs a value"; exit 1
          fi
          FILTERS="$(jq -c --arg p "$PROP" --arg o "$OP" --arg v "$VAL" \
            '. + [{propertyName: $p, operator: $o, value: $v}]' <<<"$FILTERS")"
          ;;
      esac
      shift 2 ;;
    --properties)
      if [ -z "${2:-}" ]; then err "--properties needs a comma-separated list"; exit 1; fi
      PROPS="$2"; shift 2 ;;
    --sort)
      if [ -z "${2:-}" ]; then err "--sort needs PROP or PROP:desc"; exit 1; fi
      SORT_PROP="${2%%:*}"
      if [ "$SORT_PROP" != "$2" ]; then
        SDIR="$(printf '%s' "${2#*:}" | tr '[:upper:]' '[:lower:]')"
        case "$SDIR" in
          desc|descending) SORT_DIR="DESCENDING" ;;
          asc|ascending) SORT_DIR="ASCENDING" ;;
          *) err "--sort direction must be asc or desc, got '${2#*:}'"; exit 1 ;;
        esac
      fi
      shift 2 ;;
    --limit) require_int --limit "${2:-}"; LIMIT="$2"; shift 2 ;;
    --page-size)
      require_int --page-size "${2:-}"
      if [ "$2" -lt 1 ] || [ "$2" -gt 200 ]; then err "--page-size must be 1..200"; exit 1; fi
      PAGE_SIZE="$2"; shift 2 ;;
    --json) FORMAT=json; shift ;;
    -h|--help) usage; exit 0 ;;
    -*) err "unknown option: $1 (see --help)"; exit 1 ;;
    *) err "unexpected extra argument: $1 (see --help)"; exit 1 ;;
  esac
done

if [ -z "$OBJECT" ]; then err "--object is required (see --help)"; exit 1; fi

# per-type property defaults; any other object type must pass --properties explicitly
if [ -z "$PROPS" ]; then
  case "$OBJECT" in
    contacts) PROPS="email,firstname,lastname,createdate" ;;
    companies) PROPS="name,domain" ;;
    deals) PROPS="dealname,amount,dealstage,closedate" ;;
    tickets) PROPS="subject,hs_pipeline_stage,hs_ticket_priority" ;;
    *) err "--properties is required for object type '${OBJECT}'"; exit 1 ;;
  esac
fi
PROPS_JSON="$(jq -cn --arg p "$PROPS" '$p | split(",") | map(select(length > 0))')"
if [ "$(jq -r 'length' <<<"$PROPS_JSON")" = "0" ]; then
  err "--properties resolved to an empty list"; exit 1
fi

SORTS='[]'
if [ -n "$SORT_PROP" ]; then
  SORTS="$(jq -cn --arg p "$SORT_PROP" --arg d "$SORT_DIR" '[{propertyName: $p, direction: $d}]')"
fi

hs_api() {
  curl -sS --max-time 60 \
    -H "Authorization: Bearer ${TOKEN}" \
    -H "Content-Type: application/json" \
    "$@"
}

hs_urlenc() { jq -rn --arg s "$1" '$s | @uri'; }

# exit with the api's own message if the response is an error envelope (or not json at all)
hs_check_error() {
  if ! jq -e . >/dev/null 2>&1 <<<"$1"; then
    err "non-json response from the api:"
    printf '%s\n' "$1" | head -c 2000 >&2
    exit 1
  fi
  if [ "$(jq -r 'type == "object" and .status == "error"' <<<"$1")" = "true" ]; then
    jq -r '"hubspot error \(.category // "?"): \(.message // "unknown error")"' <<<"$1" >&2
    exit 1
  fi
}

SEARCH_URL="${BASE_URL%/}/crm/v3/objects/$(hs_urlenc "$OBJECT")/search"

build_body() {
  jq -cn \
    --arg q "$QUERY" \
    --argjson filters "$FILTERS" \
    --argjson props "$PROPS_JSON" \
    --argjson sorts "$SORTS" \
    --argjson page "$PAGE_SIZE" \
    --arg after "$1" \
    '{limit: $page, properties: $props}
     + (if $q != "" then {query: $q} else {} end)
     + (if ($filters | length) > 0 then {filterGroups: [{filters: $filters}]} else {} end)
     + (if ($sorts | length) > 0 then {sorts: $sorts} else {} end)
     + (if $after != "" then {after: ($after | tonumber? // $after)} else {} end)'
}

print_page() {
  if [ "$FORMAT" = "tsv" ]; then
    jq -r --argjson take "$2" --argjson cols "$PROPS_JSON" \
      '[.results[]?][:$take][]
       | .properties as $p
       | [.id] + [$cols[] | $p[.]
          | if . == null then "" elif type == "string" then . else tojson end]
       | @tsv' <<<"$1"
  else
    jq -c --argjson take "$2" '[.results[]?][:$take][]' <<<"$1"
  fi
}

AFTER=""
FETCHED=0
TOTAL=""

while :; do
  # search api is capped at 5 req/s; throttle between pages
  if [ -n "$AFTER" ]; then sleep 0.3; fi
  BODY="$(build_body "$AFTER")"
  PAGE="$(hs_api -X POST "$SEARCH_URL" -d "$BODY")"
  hs_check_error "$PAGE"

  if [ -z "$TOTAL" ]; then
    TOTAL="$(jq -r '.total // 0' <<<"$PAGE")"
    err "total: ${TOTAL}"
    if [ "$FORMAT" = "tsv" ]; then
      jq -rn --argjson p "$PROPS_JSON" '["id"] + $p | @tsv'
    fi
  fi

  COUNT="$(jq -r '[.results[]?] | length' <<<"$PAGE")"
  TAKE="$COUNT"
  if [ "$LIMIT" -gt 0 ]; then
    REMAINING=$(( LIMIT - FETCHED ))
    if [ "$COUNT" -gt "$REMAINING" ]; then TAKE="$REMAINING"; fi
  fi
  if [ "$TAKE" -gt 0 ]; then print_page "$PAGE" "$TAKE"; fi
  FETCHED=$(( FETCHED + TAKE ))

  AFTER="$(jq -r '.paging.next.after // empty' <<<"$PAGE")"
  if [ "$LIMIT" -gt 0 ] && [ "$FETCHED" -ge "$LIMIT" ]; then
    if [ -n "$AFTER" ] || [ "$COUNT" -gt "$TAKE" ]; then
      err "output truncated at ${FETCHED} of ${TOTAL} rows (raise --limit, or 0 for everything)"
    fi
    break
  fi
  if [ -z "$AFTER" ]; then break; fi
done

err "fetched ${FETCHED} of ${TOTAL} rows"
