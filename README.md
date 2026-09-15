# Token efficiency experiment

**Question:** for the same small app spec, how much does approach (model,
effort level, orchestration structure) change the tokens spent and the
quality delivered?

**Method:** built the same app — "Deadlock Build Optimizer" — 9 times to
completion plus 2 abandoned local-model attempts, one approach per run,
same spec each time. Measured exact token usage from transcripts (API
calls, cache reads/writes, output), converted to Fable-equivalent (FE)
tokens so mixed-model and cross-provider runs compare on one scale, and
scored each build's effectiveness out of 5. Full method: [docs/METHODS.md](docs/METHODS.md),
[docs/PROTOCOL.md](docs/PROTOCOL.md), [docs/SPEC.md](docs/SPEC.md).

## Results

| Run | Approach | FE tokens | Est. $ | Weekly pts | Effectiveness | Build |
|---|---|--:|--:|--:|--:|---|
| 07-sonnet-low | Sonnet, low effort | 0.91M | $9.14 | ~1.2 pred. | 5/5 | [pages](https://gidntsquia.github.io/deadlock-build-optimize-07/) |
| 01-control | Fable 5, high effort | 6.72M | $67.24 | +9 obs. | 4.5/5 | [pages](https://gidntsquia.github.io/deadlock-build-optimizer/) |
| 04-fable51-oob | Fable 5.1, high effort | 5.84M | $58.35 | +10 obs.† | 4.5/5 | [pages](https://gidntsquia.github.io/deadlock-build-optimizer-04/) |
| 08-fable51-low | Fable 5.1, low effort | 2.88M | $28.81 | +3.0 obs. | 5/5 | [pages](https://gidntsquia.github.io/deadlock-build-optimizer-fable/) |
| 02-orchestrate | Orchestration, Cloud Routines | 6.67M | $66.74+ | ≥14 obs.‡ | 2/5 | [pages](https://gidntsquia.github.io/deadlock-build-optimizer-r02/) |
| 05-orchestrate-v2 | Orchestration, Workflows | 4.98M | $49.82 | +13 obs.† | 2/5 | [pages](https://gidntsquia.github.io/deadlock-build-optimizer-v2/) |
| 03-new-orchestrate | Meta-orchestration (3 layers)¹ | 6.47M | $64.65 | +8 obs. | 3.5/5 | [pages](https://gidntsquia.github.io/deadlock-build-optimizer-03/) |
| 06-codex | Codex Sol, low effort | 1.80M² | n/a (Codex quota) | +2.4 obs.³ | 3/5 | [pages](https://gidntsquia.github.io/deadlock-build-optimizer-codex/) |
| 09-astra | Codex Astra, high effort | 5.53M² | n/a (Codex quota) | +7.4 ($100 norm.) | 4.5/5 | [pages](https://gidntsquia.github.io/deadlock-build-optimizer-astra/) |
| 10-qwen-claude | Local qwen3.5-9b via Claude Code | n/a, local | $0 | — | 0/5 | none: never usable |
| 11-qwen-opencode | Local qwen3.5-9b via OpenCode | n/a, local | $0 | — | 0/5 | none: never ran |

¹ Fable → Opus → Sonnet. ² Sol/Astra ran on Codex CLI (separate quota, no
Anthropic price); FE is each run's $100-normalized weekly-quota
contribution, not a raw-token conversion. ³ Sol's quota delta came from
per-turn rate-limit readings in the Codex session files, not a snapshot.
† Snapshot polluted by other sessions on the account during the run
window — treat as an upper bound; ranked on FE instead. ‡ Weekly reset
crossed mid-run — delta not measurable.

Raw per-model token split (input, cache write 5m/1h, cache read, output,
$) is in [docs/TOKEN-COMPARISON.md](docs/TOKEN-COMPARISON.md). Full
numbers and generation script: `tools/tally.py --all --report` (needs the
original `~/.claude/projects` transcripts, not included here — see
"Reproducing" below).

## Verdict

**Low effort won, by a wide margin.** 07 (Sonnet, low effort) is the best
result in the experiment: 5/5 effectiveness at 0.91M FE — about an eighth
the cost of any high-effort solo run. 08 (Fable 5.1, low effort) is
second: also 5/5, at 2.88M FE, still a fraction of the high-effort runs.
09 (Codex Astra, high effort) is third: 4.5/5 at an estimated 5.53M
FE-equivalent — competitive with the best Claude high-effort runs, but
nowhere near 07 or 08 on cost. Turning effort down beat every other
variable tested in this experiment, including model choice and
orchestration structure.

Everything else is a distant second to that finding. 01 (Fable 5, high)
and 03 (three-layer meta-orchestration) land at almost the same FE cost
(~6.5–6.7M) — orchestration here added no efficiency and cost real
quality (03 scored 3.5/5 vs 01's 4.5/5). 02 (Cloud Routines orchestration)
and 05 (Workflows orchestration) both scored 2/5: orchestration overhead
bought nothing on this spec, and both scored worse than solo runs at
similar or lower cost. The local 9B model (10, 11) could not produce a
workable app by either tool — a real result, not missing data.

## Caveats

- **FE tokens are a list-price comparison proxy, not a bill.** Every
  token type is weighted to Fable list price (Fable in 1.0/out 5.0, Opus
  0.5/2.5, Sonnet 0.2/1.0; cache read 0.1×, cache write 1.25× at 5m TTL /
  2× at 1h TTL). 1 weekly point ≈ 0.75M FE, calibrated on run 01's clean
  snapshot delta.
- **Weekly-point deltas are the least reliable column.** 02: the weekly
  reset crossed mid-run, so its delta (≥14 pts) is a floor, not a real
  number; its 10 Sonnet cloud fires are also uncounted (the usage-logging
  hook never landed in time, and the gap was waived rather than re-run).
  04 and 05: other sessions on the account ran during the measurement
  window, so their observed deltas are upper bounds — rank on FE instead.
  07: its weekly delta is a prediction (~1.2 pts), not an observed one —
  the 5h window only moved 7% and never crossed the weekly boundary.
  `/usage` reports whole percent, so ±1 point is noise regardless.
- **06 and 09 ran on OpenAI's Codex CLI, a separate quota with no
  Anthropic dollar figure.** Comparability there is raw tokens and a
  quota-normalized FE estimate (each run's $100-normalized weekly points
  × the 0.75M FE/point calibration from run 01), not a token-price
  conversion. 06's own quota delta wasn't snapshotted — it's read from
  per-turn rate-limit fields in the Codex session rollout files instead
  (4%→16% on a $20 plan = +2.4 pts normalized to $100). Despite using
  more than double 09's raw tokens (32.68M vs 15.27M), 06 consumed about
  6.6× less quota per token. 09 hit its usage cap twice mid-run.
- **03's per-model counts are exact**, taken straight from transcripts,
  not estimated — an earlier draft carried a stale "estimated from
  content" caveat for its subagent output tokens; that's fixed as of this
  report (see `tools/tally.py` for the exact accounting method).
- **Wall-clock time is only recorded for runs 01, 02, and 03** — it's in
  the run notes, not the results table, because it wasn't tracked
  consistently after that.
- Every number in the results table traces to
  [docs/TOKEN-COMPARISON.md](docs/TOKEN-COMPARISON.md) and from there to
  `data/state.json`; every table is regenerable by `tools/tally.py`.

## What I'd do differently

- **Snapshot discipline.** Take a `/usage` snapshot immediately before and
  after every run, with no other account activity in between. Run 06 has
  no snapshot at all; runs 02, 04, and 05 were polluted by other sessions
  during the window.
- **Run each arm at least twice.** One run per approach means there's no
  variance estimate — a single effectiveness score and token count could
  easily be run-specific noise rather than a property of the approach.
- **Land the cloud-usage hook before run 1**, not mid-experiment. Run 02's
  10 Sonnet cloud fires went uncounted because the logging hook wasn't
  ready yet, and that gap was waived instead of re-run.
- **Blind the run ID when scoring effectiveness.** A single rater (me)
  scoring builds while aware of which approach produced them is a bias
  risk that a blind pass would remove.
- **Prefer token counts over `/usage` percentages as the primary metric.**
  Whole-percent reporting is too coarse to resolve small runs or short
  windows; FE tokens turned out to be the metric everything actually got
  ranked on.
- **Test more than one spec.** All 11 runs built the same app from the
  same spec, so the spec's particular shape (and my familiarity with it
  by run 11) may dominate the result more than the approach does. A
  second, different task would test whether these rankings generalize.

## Reproducing

```
python3 tools/tally.py --all --report
```

This needs the original run transcripts under `~/.claude/projects/`
(one directory per run, matching this repo's run paths) and, for run 02,
the `.usage-log/` cloud-fire logs pulled from each run's own repo. Those
transcripts aren't included here — they're local-only and were the
input, not the output, of this experiment. `data/state.json` is the
machine-readable source for the results table above; `docs/REPORT.md` is
tally.py's last output against the full transcript set.

## Layout

- `docs/METHODS.md`, `PROTOCOL.md`, `SPEC.md` — how the experiment was run
- `docs/RESULTS.md`, `REPORT.md`, `TOKEN-COMPARISON.md` — full results detail
- `docs/writeup.md` — the write-up
- `docs/img/` — charts (regenerate with `tools/charts.py`)
- `tools/tally.py`, `codex-tally.py`, `usage-snap.sh`, `cloud-usage-hook/` — measurement scripts
- `data/state.json`, `usage-snapshots.jsonl` — run records and `/usage` snapshots
