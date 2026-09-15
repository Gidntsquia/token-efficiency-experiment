# How much does orchestration actually cost?

I built the same small app 11 times. Same spec, same acceptance
criteria, different approach each time: a single high-effort model
working solo, the same model at low effort, three different
orchestration structures (a Fable orchestrator dispatching Sonnet
workers via Cloud Routines, the same via a Workflow, and a three-layer
Fable→Opus→Sonnet chain), two runs on OpenAI's Codex CLI, and two
attempts with a local 9B model. The question was simple: for a fixed
task, how much does approach change the tokens spent and the quality
delivered? The honest answer turned out to be more useful than a clean
one — the biggest single caveat (that the primary cost metric is a
list-price proxy, not a bill) matters as much as the headline result
(orchestration cost nothing and lost quality; low-effort solo runs
scored just as well for a fraction of the cost).

**Why this is hard to measure.** The obvious metric — Anthropic's weekly
usage percentage — turned out to be almost unusable. It's reported in
whole percent, so anything under about a point of a run reads as zero.
Three of nine Claude runs crossed a weekly reset mid-measurement,
invalidating the delta outright. Two more ran on an account with other,
unrelated sessions active during the measurement window, so their
observed deltas are upper bounds at best. And two runs used OpenAI's
Codex CLI, a completely separate quota with no Anthropic dollar
figure at all. None of this was foreseeable before running — it only
showed up as the runs actually happened, one snapshot pollution and one
missed hook at a time.

**Method.** Given that, the real metric became Fable-equivalent (FE)
tokens: every token type from every run, weighted to Fable list price
(Fable input 1.0/output 5.0, Opus 0.5/2.5, Sonnet 0.2/1.0, with cache
reads at 0.1× and cache writes at 1.25×/2× for 5-minute/1-hour TTL). This
puts mixed-model orchestration runs and single-model runs on one scale,
calibrated so 1 weekly point ≈ 0.75M FE (fixed from run 01's clean
before/after snapshot). For the two Codex runs, there's no native FE
weight at all — a different provider means a different pricing model —
so their FE figures are instead each run's own $100-normalized
weekly-quota delta, converted through the same 0.75M FE/point
calibration. That's a real, load-bearing difference: those two numbers
measure quota contribution, not token cost, and treating them as
directly comparable to the other nine would be wrong. Effectiveness was
scored 1–5 by hand against the spec's acceptance criteria, by one rater,
after each build. Full method, protocol, and spec are in this repo's
`docs/`.

**Results.** Solo runs at high effort landed within noise of each other
regardless of orchestration: Fable 5 solo (01) cost 6.72M FE and scored
4.5/5; the three-layer Fable→Opus→Sonnet orchestration (03) cost 6.47M
FE — nearly identical — and scored only 3.5/5. Both orchestration
structures that used worker dispatch scored worse still: Cloud Routines
orchestration (02) and Workflow orchestration (05) both scored 2/5, at
6.67M and 4.98M FE respectively. Orchestration, in other words, didn't
buy efficiency on this task, and in three of three orchestrated runs it
cost quality. The best result by a wide margin came from turning effort
down, not adding structure: Sonnet at low effort (07) scored a full 5/5
at 0.91M FE — about an eighth of the solo-high-effort cost — and Fable
5.1 at low effort (08) also scored 5/5, at 2.88M FE. Fable 5.1 at high
effort out of the box (04) matched 01's quality at 5.84M FE, a modest
13% saving over the older Fable 5. On the Codex side, gpt-6-astra at
high effort (09) scored 4.5/5 at an estimated 5.53M FE-equivalent quota
contribution — competitive with the best Claude runs, though that
number isn't directly comparable to a token price. gpt-5.6-sol at low
effort (06) scored lower (3/5) despite using more than double Astra's
raw tokens (32.68M vs 15.27M), because it consumed roughly 6.6× less
weekly quota per token — a reminder that raw token counts and quota
consumption aren't the same axis. The two local-model runs (10, 11), a
9B model run through Claude Code and through OpenCode, never produced a
workable app at all. That's reported as a real 0/5 result rather than
dropped as missing data: for this task and this model size, local
inference wasn't viable through either tool.

**What it doesn't show.** Every run built the same app from the same
spec exactly once. That means there's no variance estimate for any
number here — a single effectiveness score or token count could be
specific to that one run rather than a property of the approach, and
I have no way to tell the difference from this data alone. It also means
familiarity may have crept in: by run 11 I'd read the spec ten times
already, which could bias later runs toward higher or lower quality
independent of the approach being tested. The weekly-point column,
despite being the platform's own headline usage metric, is the least
trustworthy number in the whole table — three runs have an invalid or
unmeasurable delta, two more are upper bounds, and the Codex runs aren't
on the same axis at all. FE tokens carry the actual ranking, and even
those are a comparison proxy pegged to one company's list prices, not an
absolute cost. And the cloud-usage hook that was supposed to catch
run 02's dispatched Sonnet workers didn't land in time, so that run's
true cost is understated by an unknown amount that was waived rather
than backfilled.

**What I'd do next.** Snapshot `/usage` immediately before and after
every run with nothing else touching the account in between, so no
future run has a polluted or invalid delta. Run each approach at least
twice to get a variance estimate before trusting a single score. Land
every measurement hook before run 1, not mid-experiment. Blind the run
ID during effectiveness scoring to remove rater bias. And run a second,
different spec through the same set of approaches — the strongest claim
this experiment can't make is that these rankings generalize past one
app and one person's judgment of "good."

Full results table, caveat register, and reproduction instructions:
see this repo's [README](../README.md).
