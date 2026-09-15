#!/usr/bin/env python3
"""Exact token usage + report for the token-efficiency experiment.

Two sources, merged with global message-id dedupe:
1. Local transcripts: ~/.claude/projects/<slug-of-run-dir>/ — sessions,
   subagents, in-session cron ticks.
2. Cloud routine fires: .usage-log/*.jsonl anywhere inside the run dir —
   written by the fire's own Stop hook (cloud-usage-hook/) and pulled in via
   git. `git pull` the project repo before tallying.

Usage:
  python3 tally.py runs/01-control      # one run
  python3 tally.py --all                # every dir under runs/
  python3 tally.py --all --json         # machine-readable
  python3 tally.py --all --report       # also write REPORT.md

Completeness check for cloud fires: the number of .usage-log files must match
RemoteTrigger list_runs' session count for the routine — a fire whose sandbox
died before the Stop hook ran leaves no usage file.
"""
import argparse
import json
import re
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

EXP = Path(__file__).resolve().parent.parent
DATA = EXP / "data"
DOCS = EXP / "docs"
PROJECTS = Path.home() / ".claude" / "projects"
USAGE_KEYS = (
    "input_tokens",
    "output_tokens",
    "cache_read_input_tokens",
    "cache_creation_input_tokens",
)
ALL_KEYS = USAGE_KEYS + ("cache_5m", "cache_1h")

# Sessions opened in a run dir for something other than the run (protocol
# rule 2 violation) — excluded so they don't pollute that run's count.
EXCLUDE_SESSIONS = {
    "b3948a9d-d959-49ba-9659-3ab905892e02",  # 2026-09-01 final-analysis session, opened in runs/03 by mistake
}

# $/MTok (input, output) — API list prices, cached 2026-06 (claude-api skill).
# Cache weighting: read = 0.1x input; write = 1.25x (5m TTL) / 2x (1h TTL).
# A proxy for comparing mixed-model approaches, not a bill.
PRICES = {
    "claude-fable-5": (10.0, 50.0),
    "claude-mythos-5": (10.0, 50.0),
    "claude-opus-5": (5.0, 25.0),
    "claude-opus-4": (5.0, 25.0),
    "claude-sonnet-5": (2.0, 10.0),
    "claude-sonnet-4-6": (3.0, 15.0),
    "claude-haiku-4-5": (1.0, 5.0),
}


def price_for(model: str):
    for prefix in sorted(PRICES, key=len, reverse=True):
        if model.startswith(prefix):
            return PRICES[prefix]
    return None


def est_cost(bucket: dict, model: str):
    p = price_for(model)
    if p is None:
        return None
    pin, pout = p
    unsplit = max(
        bucket["cache_creation_input_tokens"] - bucket["cache_5m"] - bucket["cache_1h"], 0
    )
    return (
        bucket["input_tokens"] * pin
        + bucket["output_tokens"] * pout
        + bucket["cache_read_input_tokens"] * 0.1 * pin
        + (bucket["cache_5m"] + unsplit) * 1.25 * pin
        + bucket["cache_1h"] * 2.0 * pin
    ) / 1e6


def slug_for(path: Path) -> str:
    return re.sub(r"[^A-Za-z0-9]", "-", str(path.resolve()))


def _note_ts(result: dict, ts) -> None:
    if not ts:
        return
    if result["first_activity"] is None or ts < result["first_activity"]:
        result["first_activity"] = ts
    if result["last_activity"] is None or ts > result["last_activity"]:
        result["last_activity"] = ts


def _accumulate(result, per_model, seen_ids, mid, model, usage) -> bool:
    if not usage or not mid:
        return False
    if mid in seen_ids:
        # Streamed messages are written once per content block with the same
        # id; output_tokens can grow across those lines — keep the max.
        prev, bucket = seen_ids[mid]
        cur = usage.get("output_tokens") or 0
        if cur > prev:
            bucket["output_tokens"] += cur - prev
            result["totals"]["output_tokens"] += cur - prev
            seen_ids[mid] = (cur, bucket)
        return False
    bucket = per_model[model or "unknown"]
    seen_ids[mid] = (usage.get("output_tokens") or 0, bucket)
    result["api_calls"] += 1
    for k in USAGE_KEYS:
        v = usage.get(k) or 0
        bucket[k] += v
        result["totals"][k] += v
    split = usage.get("cache_creation") or {}
    for src, dst in (
        ("ephemeral_5m_input_tokens", "cache_5m"),
        ("ephemeral_1h_input_tokens", "cache_1h"),
    ):
        v = split.get(src) or 0
        bucket[dst] += v
        result["totals"][dst] += v
    return True


def tally(run_dir: Path) -> dict:
    proj = PROJECTS / slug_for(run_dir)
    result = {
        "run": run_dir.name,
        "transcript_dir": str(proj),
        "sessions": 0,
        "subagent_files": 0,
        "cloud_usage_files": 0,
        "api_calls": 0,
        "cloud_calls": 0,
        "first_activity": None,
        "last_activity": None,
        "per_model": {},
        "totals": dict.fromkeys(ALL_KEYS, 0),
    }
    seen_ids = {}
    per_model = defaultdict(lambda: dict.fromkeys(ALL_KEYS, 0))

    # Source 1: local transcripts for this run dir's slug.
    if proj.is_dir():
        for f in sorted(proj.rglob("*.jsonl")):
            if f.relative_to(proj).parts[0].replace(".jsonl", "") in EXCLUDE_SESSIONS:
                continue
            if f.parent == proj:
                result["sessions"] += 1
            else:
                result["subagent_files"] += 1
            with f.open() as fh:
                for line in fh:
                    try:
                        rec = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    _note_ts(result, rec.get("timestamp"))
                    if rec.get("type") != "assistant":
                        continue
                    msg = rec.get("message") or {}
                    _accumulate(
                        result, per_model, seen_ids,
                        msg.get("id") or rec.get("requestId"),
                        msg.get("model"), msg.get("usage"),
                    )

    # Source 2: cloud-fire usage logs pushed into the project repo.
    if run_dir.is_dir():
        for f in sorted(run_dir.rglob(".usage-log/*.jsonl")):
            result["cloud_usage_files"] += 1
            with f.open() as fh:
                for line in fh:
                    try:
                        rec = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if _accumulate(
                        result, per_model, seen_ids,
                        rec.get("id"), rec.get("model"), rec.get("usage"),
                    ):
                        result["cloud_calls"] += 1
                        _note_ts(result, rec.get("timestamp"))

    if not proj.is_dir() and result["cloud_usage_files"] == 0:
        result["error"] = "no transcripts or .usage-log files for this directory"
        return result

    result["per_model"] = dict(per_model)
    result["grand_total"] = sum(result["totals"][k] for k in USAGE_KEYS)
    costs = {m: est_cost(b, m) for m, b in per_model.items()}
    result["est_cost_usd"] = (
        round(sum(costs.values()), 2) if costs and None not in costs.values() else None
    )
    return result


def fmt(n) -> str:
    return f"{n:,}" if isinstance(n, int) else ("?" if n is None else f"{n}")


def print_table(results: list) -> None:
    snaps = load_snaps()
    for r in results:
        li = limit_impact(r["run"], snaps)
        if li:
            delta = f"{li['weekly_delta']:+.1f}" if li["weekly_delta"] is not None else "?"
            notes = f"  [{'; '.join(li['notes'])}]" if li["notes"] else ""
            print(
                f"{r['run']}: weekly {li['before7']}% -> {li['after7']}% "
                f"(Δ {delta} pts), 5h max seen {li['fh_max']}%{notes}"
            )
    print()
    hdr = (
        f"{'run':<20} {'calls':>6} {'cloud':>6} {'input':>10} {'output':>10} "
        f"{'cache_read':>12} {'cache_write':>12} {'total':>13} {'est_$':>8}"
    )
    print(hdr)
    print("-" * len(hdr))
    for r in results:
        if r.get("error"):
            print(f"{r['run']:<20} {r['error']}")
            continue
        t = r["totals"]
        cost = f"{r['est_cost_usd']:.2f}" if r["est_cost_usd"] is not None else "?"
        print(
            f"{r['run']:<20} {r['api_calls']:>6} {r['cloud_calls']:>6} "
            f"{fmt(t['input_tokens']):>10} {fmt(t['output_tokens']):>10} "
            f"{fmt(t['cache_read_input_tokens']):>12} "
            f"{fmt(t['cache_creation_input_tokens']):>12} {fmt(r['grand_total']):>13} {cost:>8}"
        )
    print()
    for r in results:
        if not r.get("error") and r["cloud_usage_files"]:
            print(
                f"  {r['run']}: {r['cloud_usage_files']} cloud fire(s) ingested — "
                f"cross-check against RemoteTrigger list_runs count"
            )
        for m, b in sorted(r.get("per_model", {}).items()):
            c = est_cost(b, m)
            print(
                f"  {r['run']} / {m}: out {fmt(b['output_tokens'])}, "
                f"read {fmt(b['cache_read_input_tokens'])}, "
                f"write {fmt(b['cache_creation_input_tokens'])}"
                + (f", est ${c:.2f}" if c is not None else ", est $?")
            )


def _iso(ts: str) -> str:
    return (ts or "").replace("Z", "+00:00")


def load_snaps() -> list:
    snaps = []
    f = DATA / "usage-snapshots.jsonl"
    if f.exists():
        for line in f.read_text().splitlines():
            try:
                snaps.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return snaps


def limit_impact(run_id: str, snaps: list):
    """Weekly/5h /usage impact from before/during/after:<run_id> snapshots."""
    mine = [s for s in snaps if s.get("label", "").endswith(f":{run_id}")]
    if not mine:
        return None
    before = next((s for s in reversed(mine) if s["label"].startswith("before:")), None)
    after = next((s for s in reversed(mine) if s["label"].startswith("after:")), None)
    out = {
        "snaps": len(mine),
        "fh_max": max(s["five_hour"]["utilization"] for s in mine),
        "before7": before and before["seven_day"]["utilization"],
        "after7": after and after["seven_day"]["utilization"],
        "weekly_delta": None,
        "notes": [],
    }
    if not (before and after):
        out["notes"].append("missing before/after snapshot")
        return out
    if _iso(after["ts"]) > _iso(before["seven_day"]["resets_at"]) or out["after7"] < out["before7"]:
        # A drop in utilization can only mean the weekly window reset (early
        # resets happen) — the delta is a lower bound at best, so mark invalid.
        out["notes"].append("weekly reset crossed mid-run — delta invalid")
    else:
        out["weekly_delta"] = round(out["after7"] - out["before7"], 1)
    if _iso(after["ts"]) > _iso(before["five_hour"]["resets_at"]):
        out["notes"].append("5h reset crossed (expected on long runs)")
    return out


def load_state() -> dict:
    try:
        return json.loads((DATA / "state.json").read_text())
    except (OSError, json.JSONDecodeError):
        return {}


def write_report(results: list) -> None:
    state = load_state()
    by_id = {r.get("id"): r for r in state.get("runs", [])}
    L = [f"# Token Report — {state.get('experiment', 'experiment')}", ""]
    L.append(f"Generated {date.today().isoformat()} by tally.py. Exact counts from local")
    L.append("transcripts (sessions + subagents + in-session cron ticks) plus cloud-fire")
    L.append("usage logs (.usage-log/, written by each fire's Stop hook), deduped by")
    L.append("message id.")
    L.append("")
    snaps = load_snaps()
    impacts = {r["run"]: limit_impact(r["run"], snaps) for r in results}
    if any(impacts.values()):
        L.append("## Limit impact — the headline (/usage, account-scoped: cloud fires included)")
        L.append("")
        L.append("| Run | Weekly before | Weekly after | Δ weekly pts | 5h max seen | Notes |")
        L.append("|---|--:|--:|--:|--:|---|")
        for r in results:
            li = impacts[r["run"]]
            if not li:
                L.append(f"| {r['run']} | — | — | no snapshots | — | run usage-snap.sh before/after |")
                continue
            delta = f"{li['weekly_delta']:+.1f}" if li["weekly_delta"] is not None else "?"
            L.append(
                f"| {r['run']} | {li['before7']}% | {li['after7']}% | {delta} "
                f"| {li['fh_max']}% | {'; '.join(li['notes'])} |"
            )
        L.append("")
        L.append("Utilization is reported in whole percent — a run under ~1% of the weekly")
        L.append("cap can read as 0; use the token tables below to break ties.")
        L.append("")
    L.append("## Totals per approach")
    L.append("")
    L.append("| Run | Status | API calls | Cloud calls | Cloud fires | Sessions | Input | Output | Cache read | Cache write | Total tokens | Est. cost* |")
    L.append("|---|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|")
    for r in results:
        s = by_id.get(r["run"], {})
        if r.get("error"):
            L.append(f"| {r['run']} | {s.get('status', '?')} | — | — | — | — | — | — | — | — | no data | — |")
            continue
        t = r["totals"]
        cost = f"${r['est_cost_usd']:.2f}" if r["est_cost_usd"] is not None else "?"
        L.append(
            f"| {r['run']} | {s.get('status', '?')} | {r['api_calls']} | {r['cloud_calls']} "
            f"| {r['cloud_usage_files']} | {r['sessions']} "
            f"| {fmt(t['input_tokens'])} | {fmt(t['output_tokens'])} "
            f"| {fmt(t['cache_read_input_tokens'])} | {fmt(t['cache_creation_input_tokens'])} "
            f"| {fmt(r['grand_total'])} | {cost} |"
        )
    L.append("")
    L.append("## Per-model breakdown (orchestration split)")
    L.append("")
    L.append("| Run | Model | Input | Output | Cache read | Cache write | Est. cost* |")
    L.append("|---|---|--:|--:|--:|--:|--:|")
    for r in results:
        for m, b in sorted(r.get("per_model", {}).items()):
            c = est_cost(b, m)
            L.append(
                f"| {r['run']} | {m} | {fmt(b['input_tokens'])} | {fmt(b['output_tokens'])} "
                f"| {fmt(b['cache_read_input_tokens'])} | {fmt(b['cache_creation_input_tokens'])} "
                + (f"| ${c:.2f} |" if c is not None else "| ? |")
            )
    L.append("")
    scored = [
        (r, by_id[r["run"]])
        for r in results
        if not r.get("error") and by_id.get(r["run"], {}).get("criteria_met") is not None
    ]
    if scored:
        L.append("## Efficiency")
        L.append("")
        L.append("| Run | Criteria met | Δ weekly pts | Criteria / weekly pt | Total tokens | Criteria / MTok |")
        L.append("|---|--:|--:|--:|--:|--:|")
        for r, s in sorted(
            scored,
            key=lambda p: p[1]["criteria_met"] / max(p[0]["grand_total"], 1),
            reverse=True,
        ):
            li = impacts.get(r["run"])
            wd = li and li["weekly_delta"]
            per_pt = f"{s['criteria_met'] / wd:.2f}" if wd else "?"
            wd_s = f"{wd:+.1f}" if wd is not None else "?"
            eff = s["criteria_met"] / (r["grand_total"] / 1e6)
            L.append(
                f"| {r['run']} | {s['criteria_met']} | {wd_s} | {per_pt} "
                f"| {fmt(r['grand_total'])} | {eff:.2f} |"
            )
        L.append("")
    L.append("## Timing")
    L.append("")
    for r in results:
        if not r.get("error"):
            L.append(f"- {r['run']}: {r['first_activity']} → {r['last_activity']}")
    L.append("")
    L.append("\\* Est. cost weights tokens by API list price ($/MTok: fable 10/50,")
    L.append("opus 5/25, sonnet 2/10; cache read 0.1x input, cache write 1.25x/2x for")
    L.append("5m/1h TTL). A comparison proxy across mixed-model approaches, not a bill.")
    (DOCS / "REPORT.md").write_text("\n".join(L) + "\n")
    print(f"wrote {DOCS / 'REPORT.md'}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("run_dirs", nargs="*", type=Path)
    ap.add_argument("--all", action="store_true", help="tally every dir under runs/")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--report", action="store_true", help="write REPORT.md")
    args = ap.parse_args()

    dirs = list(args.run_dirs)
    if args.all:
        dirs = sorted(p for p in (EXP / "runs").iterdir() if p.is_dir())
    if not dirs:
        ap.error("pass run directories or --all")

    results = [tally(d) for d in dirs]
    if args.json:
        json.dump(results, sys.stdout, indent=2)
        print()
    else:
        print_table(results)
    if args.report:
        write_report(results)


if __name__ == "__main__":
    main()
