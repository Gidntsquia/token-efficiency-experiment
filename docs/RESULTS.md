# Results — token-efficiency experiment

Analysis pass 2026-09-01/02 (after all three runs closed). Tally: `python3 tally.py --all`
(REPORT.md has the mechanical tables). Quality checks: builds, unit tests, snapshot
shape checks, and a real-browser pass at 390×844 (Windows Chrome headless via WSL
interop, same-origin probe page: scroll width, item tap, hero switch, reload determinism).

## Headline — criteria met per weekly /usage point

| Run | Criteria met (of 10) | Weekly Δ pts | Criteria / pt | Total tokens | Est. API cost* | Wall-clock | Steering msgs |
|---|--:|--:|--:|--:|--:|--:|--:|
| 01-control (Fable xhigh, solo) | 9 | +9 | 1.00 | 36.3M | $67 | 3h04m | 12 |
| 02-orchestrate (Fable + Sonnet cloud fires) | 7 | **≥ +14 (invalid)** | ≤ 0.50 | 36.6M **(cloud fires uncounted)** | $67 + unknown | 14h52m | ~15 (+ backstop ticks) |
| 03-new-orchestrate (Fable → Opus → Sonnet) | 9 | +8 | 1.13 | 122.4M | $69 | 4h18m | 11 |

\* Est. cost = API list-price proxy from tally.py. For 03, Opus/Sonnet output tokens are
estimated from transcript content at 3.8 chars/token (see "Accounting caveats").

**Verdict.** 01 and 03 tie on the headline within the whole-percent granularity of
/usage (9 pts vs 8 pts is inside ±1 pt noise); both are clearly ahead of 02. The
protocol's tiebreakers pull in opposite directions: raw criteria/MTok favours 01 by 3×
(0.25 vs 0.07), but that number counts a Sonnet cache-read the same as a Fable one and
the API-price proxy says the two runs cost the same ($67 vs $69). On defects and code
quality, 03 delivered more (4 named builds, 99 tests, honest baselines) but shipped
with a real mobile overflow bug that 01 does not have; 01 shipped one build and zero
tests. Call it: **03 ≈ 01 > 02**, with 03 the better product and 01 the one that was
actually ready to ship at close. 02 lost on every axis: fewer criteria, more weekly
usage than either (at least 14 pts, exact figure unknowable), 15 hours of wall-clock,
and its Sonnet cloud usage is invisible to the tally.

## Quality scores

| Run | Criteria met | Defects (15-min inspection) | Code quality (1-5) |
|-----|--------------|--------------------|--------------------|
| 01-control | 9/10 | 1 — only one named build (spec: ≥2) | 3 — 2.2k LOC, clean split (lib/generator, lib/validation, components), but a 547-line generator and **no tests at all** |
| 02-orchestrate | 7/10 | 4 — catalog pruned to 156 items (spec ≥200); one build only; ability lanes are icon-only, no ability names anywhere in the DOM; early/"mid-to-late" instead of three phases | 4 — 2.4k LOC + 1.7k test LOC, 85 tests, machine-enforced held-out gate; process files (GOALS_ARCHIVE 115 KB, PROGRESS 51 KB, .tune-tmp) left in the repo |
| 03-new-orchestrate | 9/10 | 1 — horizontal overflow at 390 px: `.ability-timeline` renders 533 px wide (documentElement.scrollWidth 513); the fix packet (P11) was still "running" when the run closed | 4 — 4.2k LOC + 2.7k test LOC, 99 tests, engine/ui/data split, 536-line README with weights before/after tuning; larger than it needs to be (465-line UI fixtures, three held-out sets) |

### Per-criterion detail

| # | Criterion | 01 | 02 | 03 |
|---|---|---|---|---|
| 1 | Snapshots: ≥200-item catalog, analytics for every active hero, ≥20 Zergggy matches with items | ✓ 251 / 38 / 30 | ✗ **156** / 38 / 30 | ✓ 251 / 38×3 / 30 |
| 2 | Offline `npm run build` + renders without errors | ✓ | ✓ (85 tests pass) | ✓ (99 tests pass) |
| 3 | Infernus opens with ≥2 named builds, ≥12 items, early/mid/late, cost + running total, correct images | ✗ **1 build** (21 items, groups, totals, images OK) | ✗ **1 build** (13 items) | ✓ 4 builds, 20 items |
| 4 | 3 other heroes generate + render | ✓ Abrams/Haze/Lash | ✓ | ✓ (18–20 items each, 4 named ability lanes) |
| 5 | Ability sequence with the 4 real Infernus names, unlock + tiers | ✓ | ✗ **icons only, no names** | ✓ |
| 6 | Tap item → card with image, cost, tier, slot, stats | ✓ | ✓ | ✓ |
| 7 | Core/not-core badges, agreement %, README ≥30% rule | ✓ 83% | ✓ 48% | ✓ 71% |
| 8 | Generator modules never reference the Zergggy snapshot (grep) | ✓ | ✓ (gate script) | ✓ literal grep clean, but see deviation below |
| 9 | 390×844: no horizontal scroll, targets ≥40 px | ✓ 375 px, 0 small targets | ✓ | ✗ **513 px** |
| 10 | README documents weights; rerun is deterministic | ✓ | ✓ | ✓ |

Note on criterion 1: the assets API only flags 173 of 251 upgrade items `shopable`, so
"≥200 shopable" is unreachable as written. Scored as "catalog ≥200 items".
Criterion 2's "no console errors" could not be captured through the probe; scored on
clean build, passing tests and error-free rendering.

## Experiment-validity caveats (read before quoting the numbers)

1. **The spec was not run as frozen.** All three runs received 11–15 mid-run steering
   messages (in-game styling with reference images, GitHub Pages deployment, "remove
   personal insight", "adjust the numbers until agreement is higher", test on Deathy's
   Lash, then Zergggy's Mina). The spec says no user input is available during the
   build. The extra scope is roughly symmetric across runs, so the comparison survives,
   but every run built more than SPEC.md asked for and the criteria scores measure only
   the spec part.
2. **The held-out rule was broken in all three runs, on instruction.** 01 (README:
   "tuning used the held-out score as its yardstick"), 02 (T19: Zergggy became the
   tuning set; ctc/Drifter became held-out) and 03 (D68–D83: coordinate-ascent tuner
   against Zergggy; app now labels it a "calibration set"; 03's orchestrator refused
   twice before complying). Criterion 8 is scored on its literal grep wording. Agreement
   percentages across runs are therefore fit statistics, not held-out measurements.
3. **02's usage numbers are unusable.** The weekly reset fired mid-run (19% → ≥26% →
   reset → 7%), so Δ is "at least 14 pts". Its 10 Sonnet cloud fires
   (`trig_01QxmDBRdwQgKUHKsTf8ZNXg`, now disabled, all 10 sessions visible via
   list_runs) never landed a `usage-log:` commit — the Stop hook did not run in the
   sandbox and the halt rule was waived at 07:55Z — so their tokens appear nowhere. The
   36.6M in the table is the local Fable orchestrator only.
4. **Subagent output tokens are not recorded in transcripts.** For in-session Agent
   workers (03's Opus and Sonnet), every transcript line carries the `message_start`
   usage (`output_tokens: 3`) even for a 118 KB thinking block. tally.py's counts for
   03 output are therefore ~5× low (37.6K recorded vs ~124K estimated for Opus, 21K vs
   ~271K for Sonnet). Cache read/write are correct. This affects only the est. cost
   column (+$5), not /usage. Fable's own thinking is not stored in transcripts either,
   but its usage field is complete.
5. **This analysis session was opened in `runs/03-new-orchestrate`** (rule 2 says
   analysis happens from `token-experiment/`). Its session id is now on an exclusion
   list in tally.py so the 03 numbers stay clean; its ~0.3M tokens of cache reads are in
   the 03 transcript slug but not in any table above.
6. The 5-hour reset was crossed in every run (expected; weekly is the metric).

## Observations

- Run 02 (02-orchestrate): the weekly (7-day) usage reset fired early this
  week, mid-run. Weekly usage had climbed to at least 26% during run 02
  before the reset happened. No `during:` snapshot was taken at the peak, so
  usage-snapshots.jsonl only shows the before/after drop (19% -> 7%), not the
  26%+ high point. Factor this into any usage-based accounting for run 02 —
  the reset timing wasn't the normal end-of-week schedule.
- Model split for 03: Fable 42 calls / 2.6M cache-read (2% of tokens, ~10% of est.
  cost); Opus 205 calls / 25.3M read + 3.1M write; Sonnet 858 calls / 88.2M read.
  The chain did what it was designed to do — Fable stayed out of the build — yet the
  weekly-usage cost came out the same as Fable doing everything itself. Sonnet cache
  reads at 3.4× the volume cost about what Fable's did.
- 01 is the only run that needed the user present the whole time (usage limit hit at
  05:11Z mid-run). 02 ran unattended for ~9 hours overnight but produced the least.
- What each method would need to win outright: 01 needs tests and the second build;
  03 needs the overflow fix (P11) and less scaffolding (fixtures, third held-out set);
  02 needs a working usage hook before its numbers mean anything.

## Phase 2 — runs 04 and 05 (pending)

Added 2026-09-02 after the analysis above. 04 = Fable 5.1 out of box (no flags;
global settings resolve to `claude-fable-5-1[1m]`, xhigh). 05 = Jaxon's revised
orchestrate skill. Scored in a second analysis pass after both close; nothing
above is re-scored. Launch details: RUNBOOK.md "Phase 2"; methods: METHODS.md.

## Run 03 usage by model, weighted to weekly-limit impact

Weights = API list price relative to Fable uncached input (Fable in 1.0 / out 5.0,
Opus 0.5 / 2.5, Sonnet 0.2 / 1.0; cache read 0.1× input, cache write 1.25× for 5-min
TTL, 2× for 1-hour). Unit: "Fable-equivalent" (FE) tokens. Calibrated on run 01 (pure
Fable): 6.72M FE = 9 weekly pts, so 1 pt ≈ 0.75M FE. Applied to run 03 this predicts
9.3 pts against 8 observed — inside the whole-percent granularity, so the proxy holds.
Anthropic does not publish the subscription weighting; this is the best available model.

| Model | Calls | Raw tokens | FE tokens | Share of weekly cost | ≈ weekly pts |
|---|--:|--:|--:|--:|--:|
| Opus 5 (orchestrator) | 205 | 28.6M | 3.51M | 51% | 4.7 |
| Sonnet 5 (workers) | 858 | 91.0M | 2.68M | 39% | 3.6 |
| Fable 5 (dispatcher) | 42 | 2.7M | 0.72M | 10% | 1.0 |
| Fable 5.1 (1 stray call) | 1 | 0.04M | 0.03M | 0% | 0.0 |
| **Total** | 1106 | 122.4M | 6.93M | 100% | 9.3 (obs. 8) |

By token type, all models: cache read 3.29M FE (47%), cache write 5-min 2.57M FE (37%),
cache write 1-hour 0.38M FE (5%), output 0.70M FE (10%), uncached input ≈ 0.
Opus's 3.1M raw cache-write tokens (5-min TTL, 1.93M FE) are the single largest line
after cache reads: the orchestrator rebuilt its cache prefix often enough to pay more
for writes than Sonnet paid for 88M tokens of reads.
