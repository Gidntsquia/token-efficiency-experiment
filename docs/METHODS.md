# Methods — 3 approaches, run manually by Jaxon

## Universal rules (all approaches)

- **The primary metric is /usage impact.** Bracket every run with snapshots:
  `./usage-snap.sh before:<run-id>` immediately before launching, and
  `./usage-snap.sh after:<run-id>` only when the run is TRULY finished (for
  02: after the last cloud fire lands and the routine is disabled, not when
  the orchestrator session closes). Optional `during:<run-id>` snaps on long
  runs capture 5-hour peaks. Limits are account-wide, so cloud fires are
  included automatically.
- **Zero other Claude usage between a run's before/after snapshots** — no
  claude.ai chats, no phone app, no other terminals, no unrelated routines.
  Anything else on the account pollutes that run's delta.
- Launch every session with the run dir as cwd. Everything in-session is
  tracked automatically: subagent workers (`<session>/subagents/*.jsonl`) and
  CronCreate cron ticks (they fire inside the same session transcript).
- **Cloud fires (RemoteTrigger routines) are allowed ONLY with the usage hook
  installed** (see approach 02). Cloud fires write no local transcripts; the
  hook makes each fire export its own exact usage into the repo
  (`.usage-log/`), which the tally ingests after `git pull`. A cloud fire
  without the hook is uncountable — never run one. Approach 01 stays purely
  local. In-session CronCreate ticks are always counted automatically.
- Nested `claude` processes (headless workers, sub-orchestrators) must be
  launched with cwd inside the run dir, or their tokens land in the wrong slug.
- Multiple sessions per run dir are fine — all counted. Never open unrelated
  sessions there.
- Same SPEC.md text given to each approach.

## 01-control — out-of-box Fable, xHigh effort

```bash
cd runs/01-control && claude --model fable --effort xhigh
```

Paste SPEC.md with: "Build this project in the current directory. Verify every
acceptance criterion yourself." No skills, no orchestration instructions.

## 02-orchestrate — Fable orchestrator → Sonnet workers (/orchestrate)

Skills restored from `~/.claude/skills-archive/` into
`runs/02-orchestrate/.claude/skills/` (orchestrate + _tick-orchestrate) —
project-scoped so they can't trigger in the other runs.

```bash
cd runs/02-orchestrate && claude --model fable
```

Invoke: `/orchestrate <spec>` and append: **"MANDATORY for token accounting:
before provisioning the routine (Phase 1.5), copy
`../../cloud-usage-hook/log-usage.sh` to `scripts/log-usage.sh` in the project
repo and merge `../../cloud-usage-hook/settings-snippet.json` into the
project's `.claude/settings.json` (keep the autoCompactWindow key), commit
both. The Phase 1.5 test fire must land a `usage-log:` commit in `.usage-log/`
— if it doesn't, hooks aren't running in the sandbox: STOP, disable the
routine, and report the problem instead of proceeding."** Routine mode and
CronCreate ticks are both fine; workers are Sonnet (skill/routine default).

## 03-new-orchestrate — Fable meta-orchestrator → Opus orchestrator → Sonnet workers

Skill written 2026-08-31 at
`runs/03-new-orchestrate/.claude/skills/new-orchestrate/` (SKILL.md = Fable
meta-orchestrator: translate + dispatch + relay only; references/orchestrator.md
= Opus playbook, Sonnet foreground waves; references/auditor.md = Opus
token-efficiency auditor fired at post-plan/mid-build checkpoints). Freeze it
before the run.

```bash
cd runs/03-new-orchestrate && claude --model fable
```

Invoke: `/new-orchestrate <spec>`. As of 2026-08-31 the orchestrator may use
in-session subagents, nested claude processes, or cloud fires/routines at its
discretion. The universal cloud-hook rule still applies and is self-enforced:
the skill's orchestrator playbook installs the usage hook and gates the
routine on the test fire landing a `usage-log:` commit, and its auditor
treats any fire without a matching usage-log file as a top-ranked finding —
so the token tiebreak stays complete.

---

## Amendment 2026-09-02 — phase 2: two more approaches

Added after the phase-1 analysis of 01–03 (see PROTOCOL.md amendment). Spec
unchanged. Universal rules above apply unchanged, including the cloud-hook rule.

## 04-fable51-oob — Fable 5.1 out of box

Run 01 resolved `--model fable` to `claude-fable-5`; the account default has
since moved to `claude-fable-5-1[1m]` with `effortLevel: xhigh` in
`~/.claude/settings.json`. "Out of box" = launch with no flags and let the
global settings decide. No skills, no `.claude/` dir in the run dir.

```bash
cd runs/04-fable51-oob && claude
```

Paste SPEC.md with the 01 wording: "Build this project in the current
directory. Verify every acceptance criterion yourself."

Differences from 01 you cannot separate afterwards: model (5 → 5.1) and
context window (`[1m]` if 01 was not launched with it). Note the resolved
model id from the tally's per-model table when scoring. Don't change
`~/.claude/settings.json` between the before/after snapshots.

## 05-orchestrate-v2 — Fable + Jaxon's revised orchestrate skill

Skill written by Jaxon at `runs/05-orchestrate-v2/.claude/skills/<name>/`
(project-scoped so it can't trigger in 04). Freeze it before launch; record
the skill name, model chain and any `.claude/settings.json` keys (e.g.
`autoCompactWindow`, as 03 used) here before the `before:` snapshot:

- skill name: `workflow-orchestrate`
- model chain: fable (top-level, judgment/brief/review only) → Workflow tool
  `build-waves` → sonnet-worker agents per packet (effort medium, 1h cache)
  → sonnet-integrator per wave (effort low, gate/commit/state.md); one
  sonnet auditor fired conditionally, background, independent of the
  build. Fallback chain if the Workflow tool is unavailable: Agent tool
  dispatch of `sonnet-worker` waves, then nested `claude -p --model sonnet`.
- settings.json keys: `autoCompactWindow: 120000`, `subagentPromptCacheTtl:
  "1h"` — both the run dir's and the project repo's `.claude/settings.json`

Frozen 2026-09-02 (6-pass review run first; findings and fixes noted in
git-free form here since this repo has no VCS: audit-trigger wording
corrected, build-waves.js worker-prompt sync note added, multi-project
resume disambiguation added, ~11 words of redundancy cut). No edits after
this point.

```bash
cd runs/05-orchestrate-v2 && claude --model fable    # then /workflow-orchestrate <spec>
```

Same discretion as 03: in-session subagents, nested claude processes with cwd
inside the run dir, or cloud fires with the usage hook installed and gated on
a `usage-log:` commit. Run 02 showed the hook not landing = uncountable run;
if the test fire doesn't land, stop and disable the routine.

## 06-codex — Codex CLI, out of box

Different product, not Claude Code — no skills/agents/workflow, no
`.claude/` dir, folded into phase 2 (see PROTOCOL.md amendment). Uses
whatever `~/.codex/config.toml` resolves by default (currently
`gpt-5.6-terra`, reasoning effort medium) — record the resolved model/effort
from the session transcript when scoring, don't change config.toml between
launch and scoring.

```bash
cd runs/06-codex && codex
```

Paste SPEC.md with the 01/04 wording: "Build this project in the current
directory. Verify every acceptance criterion yourself." No usage-snap.sh
brackets needed — Codex shares no quota with the Claude account, and its
session logs (`~/.codex/sessions/**/rollout-*.jsonl`) are self-contained per
`cwd`, so `codex-tally.py runs/06-codex` after the run reconstructs the
count exactly without a before/after delta. Fill in `PRICES` in
`codex-tally.py` for the resolved model before scoring — the script reports
tokens either way but cost comes back "unknown" until priced.

---

## Amendment 2026-09-04 — 07-fable51-low added (later corrected to 07-sonnet-low)

Added after phase-2 usage reporting (TOKEN-COMPARISON.md, 2026-09-03).
Question: does low effort trade quality for tokens on Fable 5.1, vs 04's
xhigh out-of-box run? Same spec, same model, effort forced low instead of
left to global settings (which now default to sonnet/xhigh per
`~/.claude/settings.json` — 04's "out of box" premise no longer holds for
Fable, so this run pins the model explicitly like 01 did).

**Correction (2026-09-04):** `--model fable` did not pin the model as
expected — the tally's per-model table showed the resolved model was
`claude-sonnet-5`, not Fable 5.1. Run dir and state.json id were renamed
`07-fable51-low` -> `07-sonnet-low` to match what actually ran. This run
does NOT isolate effort level against 04 (different model, not just
different effort) — it stands as a new datapoint: Sonnet 5, low effort,
solo, bare setup. A true Fable-5.1-low-effort run would need to be redone
separately if that comparison is still wanted.

## 07-sonnet-low — Sonnet 5, effort forced low

No skills, no `.claude/` dir in the run dir — same bare setup as 01/04.

```bash
cd runs/07-sonnet-low && claude --model fable --effort low
```

(`--model fable` resolved to `claude-sonnet-5` in practice, not Fable 5.1 —
see correction above.)

Paste SPEC.md with the 01/04 wording: "Build this project in the current
directory. Verify every acceptance criterion yourself." Record the resolved
model id from the tally's per-model table when scoring — 04 vs 07 only
isolates effort level if the resolved model matches; note it if it doesn't
(it didn't, here).

## Amendment 2026-09-04 — 08-fable51-low added (redo of 07's intent)

07 was meant to isolate effort level against 04 but resolved to
`claude-sonnet-5` instead of Fable 5.1 and was renamed `07-sonnet-low`
(see above). 08 redoes the original intent: same model as 04, effort
forced low.

## 08-fable51-low — Fable 5.1, effort forced low

No skills, no `.claude/` dir in the run dir — same bare setup as 01/04.

```bash
cd runs/08-fable51-low && claude --model fable --effort low
```

Paste SPEC.md with the 01/04 wording: "Build this project in the current
directory. Verify every acceptance criterion yourself." Before scoring,
check the resolved model id in `tally.py`'s per-model table — this run
only isolates effort level against 04 if it comes back
`claude-fable-5-1[1m]`. If it resolves to something else again, rename
the run dir/id to match reality (as done for 07) rather than leaving the
label wrong.

## Amendment 2026-09-05 — 09-astra added

Same tool/product as 06 (OpenAI Codex CLI) — not Claude Code, no
skills/agents/workflow, no `.claude/` dir. Folded into the same
tokens+cost comparability axis as 06, not the weekly-% metric (per
PROTOCOL.md amendment). Difference from 06: model pinned explicitly to
GPT Astra via `-m` instead of taking config.toml's default, so record the
resolved model id from the session transcript at scoring time the same
way — don't assume the flag took effect without checking.

## 09-astra — Codex CLI, model pinned to GPT Astra

No usage-snap.sh needed (different account/quota, same reasoning as 06).

```bash
cd runs/09-astra && codex -m astra
```

Paste SPEC.md with the 01/04 wording: "Build this project in the current
directory. Verify every acceptance criterion yourself." After the run,
`codex-tally.py runs/09-astra` reconstructs the token count from
`~/.codex/sessions/**/rollout-*.jsonl` the same way it does for 06 — fill
in `PRICES` for the resolved model before trusting the cost figure.
