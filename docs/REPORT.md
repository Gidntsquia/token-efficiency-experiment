# Token Report — token-efficiency

Generated 2026-09-04 by tally.py. Exact counts from local
transcripts (sessions + subagents + in-session cron ticks) plus cloud-fire
usage logs (.usage-log/, written by each fire's Stop hook), deduped by
message id.

## Run 09 — Astra update (2026-09-06)

| Run | Status | Effectiveness (Jaxon) | Notes |
|---|---|--:|---|
| 09-astra | Complete; 15,274,096 recorded tokens | **4.5/5** | Hit the usage cap **2 times** during the run. |

This manually added result supplements the generated tables below. See
[TOKEN-COMPARISON.md](TOKEN-COMPARISON.md#run-09--astra-added-2026-09-06)
for the run summary. Token snapshot: 2026-09-06 21:19:03 UTC, one GPT-6 Astra
session, including report/accounting work through that point. Input: 15,185,824
(14,553,600 cached); output: 88,272 (15,198 reasoning). Cached input is included
in input, and reasoning is included in output; neither is added again.
Total = input + output = 15,274,096. Cost remains unknown.
Weekly quota rose 33% to 70% (37 points on the $20 Codex plan). Per Jaxon's
price-normalization convention, this is **7.4 points on a $100 plan** and
**0.61 effectiveness per normalized point**. Run 01 calibration gives **29.84M
raw Fable-token equivalents**, or **5.53M weighted FE**; actual tokens are unchanged.
This assumes linear price scaling and uses rounded account-wide readings,
including report work, with an earliest-in-session baseline and no weekly reset.
The two cap hits remain recorded separately, not counted as two weekly caps.
Evidence: [token-usage.json](runs/09-astra/verification/token-usage.json).

## Limit impact — the headline (/usage, account-scoped: cloud fires included)

| Run | Weekly before | Weekly after | Δ weekly pts | 5h max seen | Notes |
|---|--:|--:|--:|--:|---|
| 01-control | 10.0% | 19.0% | +9.0 | 64.0% | 5h reset crossed (expected on long runs) |
| 02-orchestrate | 19.0% | 7.0% | ? | 63.0% | weekly reset crossed mid-run — delta invalid; 5h reset crossed (expected on long runs) |
| 03-new-orchestrate | 7.0% | 15.0% | +8.0 | 66.0% | 5h reset crossed (expected on long runs) |
| 04-fable51-oob | 18.0% | 28.0% | +10.0 | 69.0% | 5h reset crossed (expected on long runs) |
| 05-orchestrate-v2 | 29.0% | 42.0% | +13.0 | 81.0% | 5h reset crossed (expected on long runs) |
| 06-codex | — | — | no snapshots | — | run usage-snap.sh before/after |
| 07-sonnet-low | 43.0% | 43.0% | +0.0 | 7.0% |  |
| 08-fable51-low | 44.0% | 47.0% | +3.0 | 45.0% |  |

Utilization is reported in whole percent — a run under ~1% of the weekly
cap can read as 0; use the token tables below to break ties.

## Totals per approach

| Run | Status | API calls | Cloud calls | Cloud fires | Sessions | Input | Output | Cache read | Cache write | Total tokens | Est. cost* |
|---|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| 01-control | done | 299 | 0 | 0 | 1 | 596 | 358,362 | 35,226,971 | 704,552 | 36,290,481 | ? |
| 02-orchestrate | done | 325 | 0 | 0 | 2 | 650 | 274,920 | 35,409,676 | 878,959 | 36,564,205 | $66.74 |
| 03-new-orchestrate | done | 1106 | 0 | 0 | 4 | 2,212 | 81,811 | 116,113,329 | 5,843,219 | 122,040,571 | $64.65 |
| 04-fable51-oob | done: usage tallied, quality unscored | 219 | 0 | 0 | 9 | 35,618 | 412,438 | 20,926,045 | 1,048,500 | 22,422,601 | $58.35 |
| 05-orchestrate-v2 | done: usage tallied, quality unscored | 524 | 0 | 0 | 7 | 115,961 | 422,736 | 21,421,792 | 2,105,368 | 24,065,857 | ? |
| 06-codex | done: usage tallied, quality unscored | — | — | — | — | — | — | — | — | no data | — |
| 07-sonnet-low | done: usage tallied, quality unscored | 352 | 0 | 0 | 2 | 704 | 112,326 | 32,110,827 | 446,741 | 32,670,598 | $9.14 |
| 08-fable51-low | pending | 157 | 0 | 0 | 1 | 4,634 | 151,561 | 13,812,107 | 368,745 | 14,337,047 | $28.81 |

## Per-model breakdown (orchestration split)

| Run | Model | Input | Output | Cache read | Cache write | Est. cost* |
|---|---|--:|--:|--:|--:|--:|
| 01-control | <synthetic> | 0 | 0 | 0 | 0 | ? |
| 01-control | claude-fable-5 | 596 | 358,362 | 35,226,971 | 704,552 | $67.24 |
| 02-orchestrate | claude-fable-5 | 650 | 274,920 | 35,409,676 | 878,959 | $66.74 |
| 03-new-orchestrate | claude-fable-5 | 84 | 22,845 | 2,550,711 | 173,245 | $7.16 |
| 03-new-orchestrate | claude-fable-5-1 | 2 | 308 | 26,339 | 11,567 | $0.27 |
| 03-new-orchestrate | claude-opus-5 | 410 | 37,561 | 25,345,258 | 3,089,786 | $32.92 |
| 03-new-orchestrate | claude-sonnet-5 | 1,716 | 21,097 | 88,191,021 | 2,568,621 | $24.29 |
| 04-fable51-oob | claude-fable-5-1 | 35,542 | 408,496 | 19,540,243 | 855,914 | $57.44 |
| 04-fable51-oob | claude-sonnet-5 | 76 | 3,942 | 1,385,802 | 192,586 | $0.91 |
| 05-orchestrate-v2 | <synthetic> | 0 | 0 | 0 | 0 | ? |
| 05-orchestrate-v2 | claude-fable-5-1 | 115,171 | 288,242 | 7,524,296 | 886,687 | $40.82 |
| 05-orchestrate-v2 | claude-sonnet-5 | 790 | 134,494 | 13,897,496 | 1,218,681 | $9.00 |
| 07-sonnet-low | claude-sonnet-5 | 704 | 112,326 | 32,110,827 | 446,741 | $9.14 |
| 08-fable51-low | claude-fable-5-1 | 4,634 | 151,561 | 13,812,107 | 368,745 | $28.81 |

## Efficiency

| Run | Criteria met | Δ weekly pts | Criteria / weekly pt | Total tokens | Criteria / MTok |
|---|--:|--:|--:|--:|--:|
| 01-control | 9 | +9.0 | 1.00 | 36,290,481 | 0.25 |
| 02-orchestrate | 7 | ? | ? | 36,564,205 | 0.19 |
| 03-new-orchestrate | 9 | +8.0 | 1.12 | 122,040,571 | 0.07 |

## Timing

- 01-control: 2026-09-01T03:44:59.083Z → 2026-09-01T06:48:58.976Z
- 02-orchestrate: 2026-09-01T06:59:35.036Z → 2026-09-01T21:51:45.899Z
- 03-new-orchestrate: 2026-09-01T21:58:12.723Z → 2026-09-02T02:58:48.447Z
- 04-fable51-oob: 2026-09-02T04:06:50.430Z → 2026-09-02T18:08:26.408Z
- 05-orchestrate-v2: 2026-09-02T18:39:26.710Z → 2026-09-03T09:56:01.601Z
- 07-sonnet-low: 2026-09-04T12:09:37.968Z → 2026-09-04T13:53:41.222Z
- 08-fable51-low: 2026-09-04T13:59:00.988Z → 2026-09-04T15:57:00.652Z

\* Est. cost weights tokens by API list price ($/MTok: fable 10/50,
opus 5/25, sonnet 2/10; cache read 0.1x input, cache write 1.25x/2x for
5m/1h TTL). A comparison proxy across mixed-model approaches, not a bill.
