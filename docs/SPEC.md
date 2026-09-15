# Project Spec — FROZEN (do not edit after run 1)

<!-- Every run gets this exact text. -->

## What to build

**Deadlock Build Optimizer** — a mobile-first React web app that generates
optimal item builds for any hero in the game Deadlock, using real
usage/win-rate data from the public Deadlock API. A hero picker selects the
hero; **Infernus** is the default and the focus of testing, tuning, and
validation. A build = the item
list, the order to buy the items in, and the ability level-up order. Each
recommended build is then validated against the actual item choices of top
player **Zergggy** (account_id `35187362`), with his experimental one-off
builds excluded. Zergggy's data is a held-out test set: the generator must
derive builds from aggregate data using its own methods, and similarity to
Zergggy's builds is the measure of whether those methods work — his data
must never feed the generator itself. Items in the build are interactive: tapping one opens a
detail card with its image, cost, and full stats — like the build browser in
the game and Statlocker's item library (https://statlocker.gg/items/items-library,
reference for UX only, do not scrape it).

No user input is available during the build. Make reasonable default
decisions yourself and record every judgment call in the README.

## Data sources (verified reachable 2026-08-31, free, no API key)

- `https://api.deadlock-api.com` — OpenAPI at `/openapi.json`. Relevant:
  - `/v1/analytics/item-stats`, `/v1/analytics/ability-order-stats`,
    `/v1/analytics/item-permutation-stats` (all filterable by `hero_id`)
  - `/v1/players/{account_id}/match-history` (Zergggy: 4,525 matches, 478 on
    Infernus; the user: account_id `267836488`)
  - `/v1/matches/{match_id}/metadata` (per-player item purchases with times)
- `https://assets.deadlock-api.com/v2/items/by-type/upgrade` — 251 items with
  `cost`, `item_tier`, `item_slot_type`, `properties`, `tooltip_sections`,
  `image_webp`. Also `/v2/heroes` (**Infernus = hero_id 1**, with base stats
  and stat growth).
- Statlocker profile URLs in this spec are ID references only; deadlock-api
  uses the same account_ids.

## Requirements

1. **Data pipeline**: a script (`npm run fetch-data`) that downloads and
   snapshots to local JSON: the item catalog, hero data for all active
   heroes, per-hero item-stats and ability-order-stats for all active
   heroes, Zergggy's Infernus match list, and item purchase data from his
   ~30 most recent real matchmaking Infernus matches (exclude private
   lobby / bot modes). The
   Zergggy files are for the validation step only. The app
   reads only these snapshots — after fetching once, everything works
   offline. Respect the API's rate limits (batch/sleep as needed).
2. **Build generator**: a documented, deterministic scoring function,
   parameterized by hero, that produces at least two named builds for any
   selected hero. Its only match-data inputs
   are the aggregate analytics snapshots (item-stats, ability-order-stats,
   permutation-stats); it must not read Zergggy's snapshot, directly or
   indirectly — no tuning weights to raise the agreement score. (e.g. a gun-damage build and a
   spirit/burn build). It must account for: item win rate and usage rate,
   stat value per soul spent, item tier/soul investment thresholds, active
   abilities and passives, synergy with the hero's kit and stat growth from
   the assets data (for Infernus: his afterburn/spirit and fire-rate
   scaling), and game phase. Output per build: ordered buy list of 12+
   items grouped early/mid/late game with running soul total, plus an
   ordered ability level-up sequence (unlock order and upgrade-tier order
   for the hero's 4 abilities, real names from the assets API).
3. **Zergggy validation (held-out)**: a separate step that runs after
   builds are generated. From his snapshot, compute his core Infernus item
   set — items appearing in ≥30% of his sampled matches, weighting wins;
   items below that frequency are his "experiments" and are excluded. Then
   score each generated build's similarity to the core set (item overlap,
   plus buy-order agreement for shared items). The app shows this as a
   validation report: per-item core/not-core badges and an overall agreement
   percentage per build, presented as "how well the generator did", not as
   a source of the build.
4. **Personalization touch**: use the user's match history (account_id
   `267836488`, standard mode) for at least one displayed insight that
   shapes or annotates the build (e.g. their median match length weighting
   the late-game item budget). Keep it light — this is not the core feature.
5. **Interactive build view**: tapping any item opens a detail card showing
   shop image, cost, tier, slot type (weapon/vitality/spirit), and its stat
   lines and passive/active descriptions rendered from the assets data.
6. **Mobile-first UI**: designed for a phone. Fully usable at 390×844;
   desktop just gets a centered column. Tap targets ≥ 40px.

## Constraints

- Stack: React 18+ with Vite and TypeScript. Static frontend + the Node data
  script only — no backend server, no database, no auth, no paid services.
- Must run locally: `npm install`, `npm run fetch-data`, `npm run dev`.
- All active heroes must work, but testing, tuning, and the Zergggy
  validation target Infernus only; other heroes just need to generate and
  render without errors.
- Live data changes daily, so exact recommended items may differ between
  runs; the acceptance criteria below test behavior and data shape, never
  specific item names.

## Acceptance criteria

- [ ] `npm run fetch-data` completes and writes JSON snapshots including an
      item catalog with ≥200 shopable items, per-hero analytics for every
      active hero, and ≥20 of Zergggy's Infernus matches with per-match item
      purchase data.
- [ ] With snapshots present and network disabled, `npm run build` succeeds
      and the served app renders with no console errors.
- [ ] The app opens on Infernus and shows ≥2 named builds; each has an
      ordered buy list of ≥12 items grouped early/mid/late with per-item
      cost and a running soul total, and each item shows its correct shop
      image.
- [ ] Selecting any 3 other heroes from the hero picker generates and
      renders their builds (buy list + ability order) without errors —
      deep Infernus-level tuning not required.
- [ ] Each build shows an ability level-up sequence using the 4 real Infernus
      ability names, covering both unlock order and upgrade tiers.
- [ ] Tapping any item in a build opens a detail card with image, cost, tier,
      slot type, and stat/ability text matching the assets API data for that
      item.
- [ ] Every recommended item carries a Zergggy core/not-core badge, each
      build displays an agreement percentage, and README states the ≥30%
      core-set rule (experiments excluded).
- [ ] The generator code imports only the aggregate analytics snapshots —
      grepping the generator module(s) for the Zergggy snapshot file shows
      no reference; only the validation module reads it.
- [ ] At a 390×844 viewport there is no horizontal scrolling on any screen
      and all interactive elements remain tappable.
- [ ] README documents the scoring function's inputs and weights, and
      rerunning the generator on the same snapshot yields identical builds.
