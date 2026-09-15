#!/usr/bin/env bash
# Snapshot /usage (5-hour + weekly utilization %) to usage-snapshots.jsonl.
# Same endpoint the /usage panel uses; account-scoped, so cloud routine fires
# and subagents are all included.
#
# Usage: ./usage-snap.sh <before|during|after>:<run-id>
#   ./usage-snap.sh before:01-control     # immediately before launching
#   ./usage-snap.sh after:01-control      # immediately after the run ends
#   ./usage-snap.sh during:02-orchestrate # optional, for long cloud runs
set -euo pipefail
EXP="$(cd "$(dirname "$0")" && pwd)"
LABEL="${1:?usage: usage-snap.sh <before|during|after>:<run-id>}"

TOK=$(jq -r '.claudeAiOauth.accessToken // empty' "$HOME/.claude/.credentials.json" 2>/dev/null)
[ -n "$TOK" ] || { echo "no OAuth token in ~/.claude/.credentials.json" >&2; exit 1; }

RESP=$(curl -sS -m 30 'https://api.anthropic.com/api/oauth/usage' \
  -H "Authorization: Bearer $TOK" -H 'anthropic-beta: oauth-2025-04-20')
echo "$RESP" | jq -e '.five_hour.utilization' >/dev/null 2>&1 || {
  echo "unexpected response (expired token? open any claude session to refresh, then retry):" >&2
  echo "$RESP" | head -c 400 >&2
  exit 1
}

SNAP=$(echo "$RESP" | jq -c --arg label "$LABEL" --arg ts "$(date -u +%FT%TZ)" \
  '{ts: $ts, label: $label,
    five_hour: {utilization: .five_hour.utilization, resets_at: .five_hour.resets_at},
    seven_day: {utilization: .seven_day.utilization, resets_at: .seven_day.resets_at},
    model_scoped: [(.limits // [])[] | select(.kind == "weekly_scoped" and .scope.model.display_name != null) |
      {model: .scope.model.display_name, utilization: .percent, resets_at: .resets_at}]}')
echo "$SNAP" >> "$EXP/usage-snapshots.jsonl"
echo "$SNAP"
