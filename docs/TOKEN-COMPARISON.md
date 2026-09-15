# Token Usage Comparison — runs 01–09

Written 2026-09-03 after runs 04, 05 and 06 closed; updated 2026-09-04 after 07 and 08
closed. Mechanical tables regenerated in REPORT.md (`python3 tally.py --all --report`).
Quality scoring for 04–06 (criteria met, defects, code quality) has **not** been done
yet — this report covers usage only. 07 and 08 are scored (5/5 each, Jaxon).

## Run 09 — Astra (added 2026-09-06)

### Primary comparison: weekly quota normalized to a $100 plan

Per Jaxon's revised method, `normalized points = observed weekly delta × plan
price / 100`. This experiment convention assumes linear scaling with price;
it does not claim actual provider plan entitlements scale that way. It supersedes
the separate-quota exclusion for run 09. Historical API-price FE figures remain
proxies, distinct from this quota-based measurement.

Recorded Codex weekly usage rose **33% → 70%**, or **37 points** on the user's
**$20 plan**. At $100: **37 × 20 / 100 = 7.4 points**. Effectiveness per normalized
weekly point: **4.5 / 7.4 = 0.61**. Against run 01's 9 points on the $100 Claude
baseline, this is about **18% less normalized quota** for the same 4.5/5 rating.

Run 01 used 36,290,481 raw Fable tokens per 9 weekly points. Run 09 therefore
corresponds to **29.84M Fable raw-token equivalents** (`7.4 × 36,290,481 / 9`).
In the report's older weighted FE unit (6.72M per 9 points), that is **5.53M FE**.
Both conversions depend on run 01's workload mix; actual Astra tokens remain 15.27M.

Evidence: [quota-usage.json](runs/09-astra/verification/quota-usage.json), from
2026-09-05 04:37:22 UTC through 2026-09-06 21:20:05 UTC. No observed weekly reset
or decrease; the weekly reset timestamp stayed unchanged. The two cap hits are
not two full weekly allowances; recorded five-hour usage reached 100%.
The baseline is the earliest in-session reading, not a prelaunch snapshot.
Readings are rounded and account-wide, include report/accounting work, and may
include unrelated account usage. Treat 7.4 points as the observed-window estimate.

| Run | Model | Effectiveness | Usage-cap interruptions | Total tokens |
|---|---|--:|--:|--:|
| 09-astra | GPT-6 Astra (Codex) | **4.5/5** | **2** | **15,274,096** |

Effectiveness is Jaxon's rating. We hit the usage cap twice during this run.
The app was deployed to GitHub Pages; additional 30-match benchmarks measured
75% build agreement for both Deathy's Lash and Zergggy's Mina. These agreement
scores are separate from the user-rated effectiveness score.

Tally snapshot through 2026-09-06 21:19:03 UTC: one GPT-6 Astra session,
15,185,824 input tokens (14,553,600 cached), plus 88,272 output tokens
(15,198 reasoning), totaling **15,274,096**. Cached input and reasoning are
subsets, not additional tokens. This includes report/accounting work up to the
snapshot; subsequent messages are not included. Effectiveness per 10 MTok:
**2.95**. Cost is unknown; quota comparison uses the price normalization above.

Reproduce with `python3 codex-tally.py runs/09-astra --json`. The script scans
both WSL and Windows session stores, normalizes WSL UNC paths, deduplicates
session IDs, and uses the last cumulative usage record per session. Saved
evidence: [token-usage.json](runs/09-astra/verification/token-usage.json).

## Runs 07–08: single-model low-effort head-to-head

Same task run twice, single session each, no orchestration: build a Deadlock item/build
optimizer against the same spec. 07 = Sonnet 5, effort low. 08 = Fable 5.1, effort low.
Both snapshots are clean (no reset crossed mid-run, no other session on the account
during the bracket) — the observed weekly delta is trustworthy here, unlike 04/05.

| Run | Model | Calls | Total tokens | Output tokens | Est. $ | FE tokens | Predicted weekly pts | Observed Δ weekly pts | Effectiveness |
|---|---|--:|--:|--:|--:|--:|--:|--:|--:|
| **07-sonnet-low** | claude-sonnet-5 | 352 | **32.67M** | 112K | $9.14 | 0.91M | 1.2 | +0.0 (sub-percent) | 5/5 |
| **08-fable51-low** | claude-fable-5-1 | 157 | **14.34M** | 152K | $28.81 | 2.88M | 3.8 | +3.0 (clean) | 5/5 |

FE computed with the same weights as 03–05 (RESULTS.md "Run 03 usage by model"):
Fable in 1.0 / out 5.0, cache read 0.1×, cache write 1.25×(5-min)/2×(1-hour); Sonnet
in 0.2 / out 1.0, cache read 0.02×, cache write 0.25×(5-min)/0.4×(1-hour).

07's observed delta of +0.0 pts is below the whole-percent resolution of `/usage`
(weekly stayed at 43% before and after) — the FE prediction of ~1.2 pts is the better
estimate for it. 08's observed +3.0 lines up with its 3.8-pt FE prediction.

**Effectiveness per usage:**

| Run | Effectiveness | Total tokens | Eff. / 10 MTok | Weekly pts (best estimate) | Eff. / weekly pt |
|---|--:|--:|--:|--:|--:|
| 07-sonnet-low | 5/5 | 32.67M | **1.53** | ~1.2 (FE, delta unmeasurable) | ~4.1 |
| 08-fable51-low | 5/5 | 14.34M | **3.49** | 3.0 (observed) | **1.67** |

**Verdict.** Both hit the same 5/5 effectiveness, but Sonnet used 2.3× the raw tokens
and roughly 3× the weekly-limit impact of Fable 5.1 at the same effort level for
identical output quality on this task. Fable 5.1 low is the clear winner on this pair:
same result, a third of the weekly cost. This also reverses the phase-2 pattern
above — at low effort, single-model Fable still beats single-model Sonnet on
tokens-per-output, so the earlier "strong model wins" conclusion is about
orchestration overhead specifically, not about Fable vs. Sonnet in general.

## Headline: total tokens and cost proxy

| Run | Approach | Models seen | API calls | Total tokens | Output tokens | Est. API cost* | Fable-equiv. tokens (FE)† | Predicted weekly pts‡ | Observed Δ weekly pts | Active wall-clock |
|---|---|---|--:|--:|--:|--:|--:|--:|--:|--:|
| 01-control | Fable 5 xhigh, solo | fable-5 | 299 | 36.3M | 358K | $67 | 6.72M | 9.0 (calibration) | +9 (clean) | 3h04m |
| 02-orchestrate | Fable + Sonnet cloud fires | fable-5 (+10 uncounted cloud fires) | 325 | 36.6M local only | 275K | $67 + unknown | ≥ 6.8M | — | ≥ +14 (reset mid-run) | 14h52m |
| 03-new-orchestrate | Fable → Opus → Sonnet | fable-5, opus-5, sonnet-5 | 1106 | 122.0M | 82K (recorded; ~400K est.) | $65 (+$5 est.) | 6.93M | 9.3 | +8 (clean) | 4h18m |
| **04-fable51-oob** | Fable 5.1 [1m] xhigh, solo | fable-5-1, sonnet-5 (3 Explore subagents) | 219 | **22.4M** | 412K | **$58** | **5.83M** | **7.8** | +10 (polluted, upper bound) | ~11.5h main session + 2.5h follow-ups (span 14h, idle gaps included) |
| **05-orchestrate-v2** | Fable 5.1 + workflow-orchestrate → Sonnet waves | fable-5-1, sonnet-5 (31 subagent files) | 524 | **24.1M** | 423K | **$50** | **4.98M** | **6.6** | +13 (polluted, upper bound) | 3h44m + 1h13m next morning |
| **06-codex** | Codex CLI out of box | gpt-5.6-sol + codex-auto-review | — | **32.7M** | 133K | unknown (no price for gpt-5.6-sol) | n/a (different quota) | n/a | n/a | ~3h20m on 09-02 + short session 09-03 |

\* tally.py list-price proxy: fable 10/50, opus 5/25, sonnet 2/10 $/MTok; cache read 0.1×,
cache write 1.25× (5-min) / 2× (1-hour). tally prints "?" for 01 and 05 because of a
`<synthetic>` model row; the per-model rows sum to $67.24 and $49.82.

† FE = tokens weighted by list price relative to Fable uncached input (method in
RESULTS.md, "Run 03 usage by model"). Sonnet weights: in 0.2, out 1.0, cache read 0.02,
cache write 0.25 (5-min) / 0.4 (1-hour).

‡ Calibrated on run 01: 0.75M FE per weekly point. Run 03 validated it (9.3 predicted,
8 observed). This is the number to use for 04 and 05 because their snapshots are polluted.

## Why the 04/05 snapshot deltas are unusable

Other sessions were on the account during both runs, so the before/after `/usage`
deltas are upper bounds, not measurements. Evidence in usage-snapshots.jsonl:

- Weekly rose 15% → 18% between `after:03` (02:19Z) and `before:04` (04:06Z), 1h47m
  with no run in progress: ~3 pts of unrelated usage in under two hours.
- Weekly rose 28% → 29% between `after:04` (18:09Z) and `before:05` (18:38Z), 29 minutes
  with no run in progress.
- 05's bracket spans 15h22m (18:38Z 09-02 → 10:00Z 09-03) for ~5h of actual run
  activity; the rest of that window is exposed to whatever else was running.

Token-weighted prediction vs observed delta:

| Run | Predicted (FE) | Observed | Implied pollution |
|---|--:|--:|--:|
| 04 | 7.8 | +10 | ~2 pts |
| 05 | 6.6 | +13 | ~6 pts |

Both runs are ranked on FE tokens below, not on the snapshot delta.

## Ranking on usage alone (quality not yet scored)

Cheapest first, by Fable-equivalent tokens (the best available proxy for weekly-limit impact):

1. **05-orchestrate-v2 — 4.98M FE (~6.6 pts).** 26% below 01. Fable did 351 of 524 calls
   but only 7.5M cache reads (vs 35M for 01): the orchestrator kept its context small.
   Sonnet did 14M cache reads and 134K output for 0.9M FE (18% of the run).
2. **04-fable51-oob — 5.83M FE (~7.8 pts).** 13% below 01 with the same "solo Fable"
   shape. Fable 5.1 [1m] used 45% fewer cache-read tokens than Fable 5 (19.5M vs 35.2M)
   but 14% more output (408K vs 358K) and 22% more cache writes. The 1m context means
   fewer compactions; the cost shifts from re-reading to writing.
3. **01-control — 6.72M FE (9 pts).** Baseline.
4. **03-new-orchestrate — 6.93M FE (~9.3 pts).** Same weekly cost as 01 despite Fable
   doing only 2% of tokens; Opus cache writes (3.1M, 5-min TTL) were the largest line.
5. **02-orchestrate — ≥ 6.8M FE plus 10 uncounted Sonnet cloud fires.** Unrankable.

06-codex is on a separate quota and is compared on raw tokens only: 32.7M total, of
which 29.8M was cached input. Raw-token comparison: more than 04 or 05, less than 03,
about the same as 01. No price is on file for gpt-5.6-sol, so no $ figure.

## Per-model breakdown for the new runs

| Run | Model | Calls | Input | Output | Cache read | Cache write (TTL) | Est. $ | FE |
|---|---|--:|--:|--:|--:|--:|--:|--:|
| 04 | claude-fable-5-1 | 216 | 35,542 | 408,496 | 19,540,243 | 855,914 (1h) | $57.44 | 5.74M |
| 04 | claude-sonnet-5 | 3 subagents | 76 | 3,942 | 1,385,802 | 192,586 (118K 5m / 74K 1h) | $0.91 | 0.09M |
| 05 | claude-fable-5-1 | 351 | 115,171 | 288,242 | 7,524,296 | 886,687 (1h) | $40.82 | 4.08M |
| 05 | claude-sonnet-5 | 173 | 790 | 134,494 | 13,897,496 | 1,218,681 (1h) | $9.00 | 0.90M |
| 06 | gpt-5.6-sol (main, Windows Codex) | 255 turns | 14,509,788 (14,052,608 cached) | 92,568 (16,768 reasoning) | — | 0 | ? | n/a |
| 06 | gpt-5.6-sol (2 WSL sessions) | 79 turns | 2,894,923 (2,755,584 cached) | 24,195 (2,771 reasoning) | — | 0 | ? | n/a |
| 06 | codex-auto-review (7 sessions) | 213 turns | 15,144,151 (13,005,824 cached) | 16,535 (7,090 reasoning) | — | 0 | ? | n/a |

04's 115K uncached input in 05 is unusual (01–04 have < 36K): the workflow re-sent
packet briefs as fresh input rather than cached prefix. Small in FE terms (0.1M).

## Accounting caveats specific to phase 2

1. **06 was mostly run from the Windows Codex client, not WSL.** `codex-tally.py` reads
   `~/.codex/sessions` in WSL and found only 2 sessions (2.9M). The other 10 sessions
   (29.8M, including the 14.6M main build) are in `/mnt/c/Users/Jaxon/.codex/sessions`
   with cwd `\\wsl.localhost\Ubuntu\...\runs\06-codex`. The 32.7M figure above sums
   both stores by hand. The run dir's own `TOKEN_USAGE.md` (written by Codex at
   08:49Z) reports 14.4M for the main task only and omits the auto-review sessions
   and the WSL sessions. Fix: point `codex-tally.py` at both session roots and
   accept the UNC cwd form.
2. **codex-auto-review sessions are half of 06's tokens** (15.2M of 32.7M). Codex
   spawns these automatically after turns; they are part of the out-of-box cost and
   are counted, but they are a different model label and their billing weight is
   unknown.
3. **Subagent output tokens are under-recorded** (same as RESULTS.md caveat 4). 05's
   134K Sonnet output across 31 subagent files and 04's 3.9K are likely low. Cache
   read/write are correct, and those dominate FE, so the ranking does not move.
4. **04's model resolved to `claude-fable-5-1`** (tally per-model table). The [1m]
   context window is not visible in the transcript model id; assume it applied since
   settings.json set it.
5. **04 ran 9 sessions** (1 main 11.5h session plus 8 follow-ups on 09-02 afternoon,
   including 2 stand-alone Sonnet sessions). All in the run slug, all counted.
6. **05 was resumed the next morning** (08:43Z–09:56Z 09-03, 6 sessions, ~1h13m) after
   the main orchestrator session closed at 22:23Z. Counted, but this is where the
   weekly-delta window absorbed most of its pollution.
7. 01 and 03 keep their clean snapshot deltas from phase 1; nothing re-scored.

## Bottom line on usage

Both phase-2 Claude approaches beat the phase-1 runs on tokens. The revised
orchestrate skill (05) is the cheapest at ~4.98M FE (about 6.6 weekly points), and
Fable 5.1 out of box (04) is second at ~5.83M FE (about 7.8 points). Against the 01
baseline that is a 26% and 13% reduction. Whether that holds as *output per token*
depends on the quality pass for 04–06, which is still to do. Codex used 32.7M raw
tokens on its own quota, comparable to 01's raw count but not comparable on cost until
gpt-5.6-sol is priced.

## Effectiveness per usage (added 2026-09-03)

Jaxon's effectiveness scores (1–5, hands-on judgement of the shipped product):

| Run | Effectiveness | FE tokens | Weekly pts (best estimate) | Effectiveness / weekly pt | Total tokens | Effectiveness / 10 MTok |
|---|--:|--:|--:|--:|--:|--:|
| 01-control | 4.5 | 6.72M | 9.0 | 0.50 | 36.3M | 1.24 |
| 02-orchestrate | 2.0 | ≥ 6.8M + uncounted cloud | ≥ 14 | ≤ 0.14 | ≥ 36.6M | ≤ 0.55 |
| 03-new-orchestrate | 3.5 | 6.93M | 8–9.3 | 0.38–0.44 | 122.0M | 0.29 |
| **04-fable51-oob** | **4.5** | 5.83M | 7.8 | **0.58** | 22.4M | **2.01** |
| 05-orchestrate-v2 | 2.0 | 4.98M | 6.6 | 0.30 | 24.1M | 0.83 |
| 06-codex | 3.0 | n/a | n/a | n/a | 32.7M | 0.92 (raw tokens, separate quota) |
| 09-astra | **4.5** | 5.53M (quota-calibrated) | 7.4 ($100-normalized; 37 on $20) | **0.61** | 15.27M | **2.95** |

Weekly pts: observed delta for 01 and 03, FE prediction for 04 and 05 (snapshots polluted).

**Verdict.** 04 (Fable 5.1 out of box) wins outright: tied for best output with 01 at
13% less weekly usage and 38% fewer raw tokens. 01 is second. Every orchestration
approach lost on effectiveness per point: 03 delivered a 3.5 at the same weekly cost
as 01, and 05 was the cheapest run but produced a 2.0, so its 26% token saving bought
less than half the output. 02 is last on every axis. Codex sits mid-pack on raw
tokens with a 3.0, on a separate quota.

The pattern across both phases: a single strong model with a large context beats
splitting the work across cheaper models. The orchestration overhead (briefs,
integration, re-reads) is paid in Fable tokens either way, and the workers' output
was weaker than what Fable would have written itself.
