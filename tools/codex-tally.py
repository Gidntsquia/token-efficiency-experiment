#!/usr/bin/env python3
"""Token usage tally for run06 (Codex CLI) — companion to tally.py.

Codex shares no quota with the Claude weekly /usage cap the other runs are
scored against (see PROTOCOL.md amendment 2026-09-02, run06 note), so this
is a separate script rather than a mode of tally.py. run06's comparability
axis is token totals + estimated $ cost, not criteria-met-per-usage-point.

Source: ~/.codex/sessions/<yyyy>/<mm>/<dd>/rollout-*.jsonl — one file per
Codex session, self-contained. The first line is session_meta (cwd);
turn_context carries the model; event_msg/token_count carries a CUMULATIVE
total_token_usage per session — take the LAST one per file, never sum
across lines within a session. No before/after snapshot is needed (unlike
usage-snap.sh): each session file already scopes to one cwd, so filtering
by run dir is exact.

Usage:
  python3 codex-tally.py runs/06-codex
  python3 codex-tally.py runs/06-codex --json
"""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

CODEX_SESSIONS = Path.home() / ".codex" / "sessions"

# $/MTok (input, output) by model-id prefix. Fill in once real pricing for
# the resolved model (see the report's "model(s)" line) is known — until
# then cost comes back None and the report says so explicitly.
PRICES = {
    # "gpt-5.6-terra": (input_per_mtok, output_per_mtok),
}

USAGE_FIELDS = (
    "input_tokens",
    "cached_input_tokens",
    "cache_write_input_tokens",
    "output_tokens",
    "reasoning_output_tokens",
    "total_tokens",
)


def price_for(model):
    for prefix in sorted(PRICES, key=len, reverse=True):
        if model and model.startswith(prefix):
            return PRICES[prefix]
    return None


def cwd_matches(cwd, run_dir):
    if not cwd:
        return False
    cwd = cwd.replace("file://", "")
    cwd = cwd.replace("\\", "/")
    for prefix in ("//wsl.localhost/", "//wsl$/"):
        if cwd.lower().startswith(prefix):
            cwd = "/" + cwd[len(prefix):].split("/", 1)[1]
    if not Path(cwd).is_absolute():
        return False
    try:
        Path(cwd).resolve().relative_to(run_dir)
        return True
    except ValueError:
        return False


def tally_session(path, run_dir):
    cwd = model = session_id = last_usage = last_usage_at = None
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            t = d.get("type")
            payload = d.get("payload") or {}
            if t == "session_meta":
                cwd = payload.get("cwd")
                session_id = payload.get("id") or payload.get("session_id")
            elif t == "turn_context":
                model = payload.get("model") or model
            elif t == "event_msg" and payload.get("type") == "token_count":
                usage = (payload.get("info") or {}).get("total_token_usage")
                if usage:
                    last_usage = usage
                    last_usage_at = d.get("timestamp")

    if not cwd_matches(cwd, run_dir):
        return None
    return {"session_id": session_id, "path": str(path), "model": model, "usage": last_usage, "last_usage_at": last_usage_at}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("run_dir", type=Path)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--session-root", type=Path, action="append", help="Session store to scan; repeat for multiple stores")
    args = ap.parse_args()

    run_dir = args.run_dir.resolve()
    roots = args.session_root or [CODEX_SESSIONS, Path("/mnt/c/Users/Jaxon/.codex/sessions")]
    files = sorted({f for root in roots for f in root.glob("*/*/*/rollout-*.jsonl")})
    sessions = [s for s in (tally_session(f, run_dir) for f in files) if s]
    unique = {}
    for s in sessions:
        key = s["session_id"] or s["path"]
        if key not in unique or (s["last_usage_at"] or "") > (unique[key]["last_usage_at"] or ""):
            unique[key] = s
    sessions = list(unique.values())

    totals = {k: 0 for k in USAGE_FIELDS}
    models = set()
    no_usage = 0
    for s in sessions:
        if not s["usage"]:
            no_usage += 1
            continue
        for k in USAGE_FIELDS:
            totals[k] += s["usage"].get(k, 0)
        if s["model"]:
            models.add(s["model"])

    cost = None
    if len(models) == 1:
        p = price_for(next(iter(models)))
        if p:
            pin, pout = p
            cost = (totals["input_tokens"] * pin + totals["output_tokens"] * pout) / 1e6

    result = {
        "tallied_at": datetime.now(timezone.utc).isoformat(),
        "run_dir": str(run_dir),
        "sessions_found": len(sessions),
        "sessions_no_usage": no_usage,
        "models": sorted(models),
        "totals": totals,
        "est_cost_usd": cost,
        "sessions": sessions,
    }

    if args.json:
        print(json.dumps(result, indent=2))
        return

    print(f"Codex tally for {run_dir}")
    if not sessions:
        print("  no sessions found")
        return
    print(f"  sessions matched: {len(sessions)} ({no_usage} with no token_count event)")
    print(f"  model(s): {', '.join(sorted(models)) or '(none seen)'}")
    for k in USAGE_FIELDS:
        print(f"  {k}: {totals[k]:,}")
    if cost is not None:
        print(f"  est. cost: ${cost:,.2f}")
    else:
        print("  est. cost: unknown — fill in PRICES in codex-tally.py for this model")


if __name__ == "__main__":
    main()
