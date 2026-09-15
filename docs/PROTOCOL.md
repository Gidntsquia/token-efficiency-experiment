# Token-Efficiency Experiment

Build the same project 3-5 times with different methods. Measure exact tokens per
run and score output quality. Goal: which method gives the best output per token.

## How tracking works

Claude Code writes a transcript per working directory to
`~/.claude/projects/<dir-slug>/`. Each run lives in its own directory under
`runs/`, so its transcripts (including subagents) are isolated and countable.

Count tokens any time with:

    python3 tally.py --all

## Rules (these keep the numbers valid)

1. **Freeze SPEC.md before run 1.** Never edit it after. Every run gets the
   identical spec.
2. **One directory per run, one purpose per directory.** Start each run with
   `cd runs/<id> && claude` (fresh session, no `--resume`, no `--continue`).
   Never open a session in a run directory for anything else — tally, chat,
   and review sessions happen from `ai-sandbox/` or `token-experiment/`.
3. **Per-approach model configs are fixed in METHODS.md.** The top-level
   session is always Fable; worker/orchestrator models differ by design.
   Don't toggle fast mode / output styles mid-experiment.
4. **A run ends when you'd ship it.** Stop when the acceptance criteria in
   SPEC.md pass, or when you give up. Multiple sessions in the same run dir
   are fine — they're all counted.
5. **Every token source must be counted.** Local sessions, subagents, and
   in-session CronCreate ticks are counted automatically (same transcript
   slug). Cloud RemoteTrigger fires write no local transcripts — allowed only
   with the Stop-hook usage exporter installed in the project repo
   (cloud-usage-hook/), which commits each fire's exact per-message usage to
   `.usage-log/`. Web sessions and any other unhooked cloud work stay banned.
6. **One run per day.** Spreads the weekly usage cap and keeps you fresh for
   quality scoring.
7. **No mid-experiment analysis.** The top level touches the numbers exactly
   once, after all runs finish: one tally pass, quality scoring (rubric
   below — scored together so early runs aren't judged more harshly), then
   the report.

## The methods

Defined by the user in METHODS.md (frozen before run 1, like the spec). Each
method is a run id plus an ordered list of messages built from the RUNBOOK
patterns. Execution commands live in RUNBOOK.md.

Known bias you can't remove: by run 3 you know the spec's rough edges. The
frozen spec and fixed method scripts limit how much that leaks into the runs.
Note anything you learned mid-experiment in RESULTS.md.

## Quality rubric (score after all runs complete)

Per run, from a fresh session in `token-experiment/` (not the run dir):

- **Criteria met** — n of N acceptance criteria from SPEC.md pass (the big one).
- **Defects** — bugs found in a 15-minute inspection/manual test.
- **Code quality 1-5** — structure, naming, no dead code, reasonable size.

Headline metric: **criteria met per weekly /usage percentage point** (from
usage-snap.sh before/after deltas — the account-scoped subscription limit is
the scarce resource, and it's the only measure that weights Fable vs Opus vs
Sonnet and cloud fires the way the plan actually charges them). Utilization
is whole-percent granularity, so token totals (criteria per MTok) break ties
on small runs; defects and code quality break remaining ties.

## Amendment 2026-09-02 — phase 2 (runs 04–05)

Two runs added after the phase-1 analysis: 04 (Fable 5.1 out of box) and 05
(revised orchestrate skill). Rule 7 now reads: one analysis pass per phase.
Known extra bias: the person launching and scoring 04/05 has read RESULTS.md
for 01–03 (where each run fell short, which steering messages helped), and the
05 skill is written with that knowledge — that is the point of 05, but it
means 04/05 are not blind. Keep the spec paste and steering behaviour as close
to 01–03 as you can and note deviations in RESULTS.md.

## Amendment 2026-09-02 — 06-codex folded into phase 2

06 (Codex CLI, out of box) added same day, folded into the phase-2 analysis
pass rather than its own phase — 04, 05, and 06 are scored together once all
three close. Same spec paste as 01/04. Different product entirely: 06 shares
no quota with the Claude weekly `/usage` cap the headline metric ("criteria
met per weekly /usage percentage point") is denominated in, so that metric
does not apply to 06's row — its comparability axis is token totals + est. $
cost (`codex-tally.py`, filtered by session `cwd`, no before/after snapshot
needed). Report 06 alongside 01–05 in REPORT.md but do not rank it on the
headline metric; rank it against the others only on criteria-met-per-MTok
and criteria-met-per-dollar, noted as a separate, non-commensurable
comparison. Extra bias, same shape as the 04/05 note above: 06 is not blind
to phase-1 results either.
