# Magic System Session Handoff — 2026-10-20

Start here next session. Everything below is either an **author decision** (canon), a **source** (recovered file, not ratified), or **open**.

## For the integrating agent (Dragon), 2026-10-22

- **What this is.** A hand-authored reference for this one magic system, built by the author outside the normal pipeline (where the book is processed and the Dragon derives the magic, or decides whether the story needs magic at all). Treat it as the behavioral spec and regression fixture for integration, not as the pipeline's design.
- **Canon vs. not.** Each sketch has an `AUTHOR-APPROVED` block and a `PROVISIONAL` block at the top. Only the first is canon. Demo numbers (100 per spell, 40/50 ongoing, 30 per hop, 200 HP, `JUMP_RANGE` 3.5) are placeholders; don't carry them into Combat3D as defaults.
- **Verify:** `python3 test_chain_mr_sketch.py` (30), `python3 test_chain_zw_bridge.py` (7), `python3 -I chain_mr_sketch.py`.
- **Integration traps found in review:**
  - The bonus roll is seeded by (seed, hit id). Hit ids must be unique within an encounter, or two hits get the same roll.
  - Plasma is a derived form, never a chain element. The primary hit of a bolt always lands as Lightning (fixed 2026-10-22); only jumps carry `plasma` damage. Resistance has no `plasma` entry, so Plasma ignores Fire/Lightning resistance (OPEN).
  - "Carries Fire/Earth/Shadow" = the last element of the target's chain, even if that chain is closed (e.g. after Char). OPEN whether a closed chain still carries its element.
  - Fire, Fire ends the chain; a third Fire then starts a new chain. The final infliction only applies when the incoming element differs from the outgoing one.
  - HP goes below 0 freely and there is no death here; Combat3D owns death.
  - `godot_demo/main.gd` keeps a local HP copy for playback only. Its visuals (Label3D, flashes, beams) are reusable; its state handling is not authority.
  - Generated files: `godot_demo/{encounter,field,battlefield}.json`, `shot.png`, `.godot/`.

## Files produced this session (all in `lore library/magic/`)

| File | What it is |
|---|---|
| `magic_library_manifest.json` | All 49 source files from the Drive export: sha256, family, subgroup, owner, duplicates, dependencies, open questions |
| `elemental_reaction_matrix_v0.1.md` | All 64 two-hit cells in time order (first → second), classified AUTHOR-CONFIRMED / SOURCE-RECOVERED / PHYSICS-PROPOSED / CONFLICT |
| `chain_mr_sketch.py` | Pure-functional chain kernel sketch: 6 confirmed cells, primary-only, dominant element, damage model (2026-10-22). Self-checks pass |
| `SESSION_HANDOFF_2026-10-20.md` | This file |

Run the sketch: `cd "lore library/magic" && python3 -I chain_mr_sketch.py`

## Author decisions (canon)

**Chain basics**
- A **chain** = one enemy, multiple elemental effects on it. ~~It always ends after the third hit.~~ **Superseded 2026-10-22:** no fixed hit limit; chains may span multiple full-party cycles. A configurable maximum exists but stays disabled.
- (2026-10-22) **Repeating the same element consecutively ends the chain.** The repeat deals its normal damage but doesn't advance or extend the chain.
- **Propagation** (Lightning jumping between enemies) is a separate system. Jumps are not chain hits.
- Reactions are physics and order-dependent, written in time order:
  - Water → Fire = **Boil** (fire can't put the water out)
  - Fire → Water = **Steam** (water puts the fire out)
  - Fire → Lightning = **Plasma**
  - Lightning → Fire = **Char** (ends the chain)
  - Earth → Water = **Mudstorm** (spec 04)
  - Earth → Lightning = **Grounding** (spec 03)
- Opposite orders are evaluated independently; they *may* give the same result.
- Accepted terminal states (provisional): Char, Ash, Grounding, Shatter, Stasis, Banish, Cleansing. Which pairs produce them is unconfirmed, except Char.
- The six reactions keep their names; their effects stay unresolved until authored.

**Chain damage**
- Every hit = standard hit + element modifier.
- 2nd hit: +2–4% over the standard modifier. 3rd hit: +3–5%.
- **Replacement, not stacking or nulling.** The outgoing element gives its remaining ongoing damage as a final infliction, then the incoming element replaces it.
  - Water → Fire (Boil): Water adds +1%.
  - Fire → Water (Steam): Fire adds +2%.
- (2026-10-22) The hit bonus is a **random roll** within the range, taken as a **% of the attacking spell's standard damage**.
- (2026-10-22) The final infliction = the outgoing element's **remaining ongoing damage × (1 + its %)**.
- (2026-10-22) A **pair with no authored reaction still replaces** the old element: final infliction applies, the hit counts toward the chain, and no reaction is named.

**Elements**
- Power order: Fire = Ice > Earth > Water.
- Water has less ongoing damage than Fire.
- Ice: rare but high crits. Earth: frequent but low crits.
- Lightning: random damage in a range per jump, random left/right per jump, no ongoing damage.
- Personal (user) spells are stronger than common spells.

**Propagation**
- Lightning reaching an enemy with Fire becomes Plasma and continues as Plasma ("1 L, 2 L, 3 L, 4 Plasma, 5 Plasma").
- Earth, Clay, Ash and Shadow stop Lightning. The stopping enemy still takes the hit ("1 L, 2 L, stop").
- (2026-10-22) Propagation stays separate from elemental chaining. **Grounding and Shadow absorption** let the current target receive the infliction but stop further propagation.
- (2026-10-22) **Clay and Ash aren't elements.** They're symbolic forms: Clay inherits Earth's Grounding, and Ash inherits Shadow's Lightning stop. They inherit **only that behavior**, not every Earth or Shadow interaction. The eight elements stay as they are.
- Stopping Lightning's path ≠ ending that enemy's chain.

**Thresholds and resistance**
- First-hit activation by strength relative to standard:
  - Under 40%: can't start a chain.
  - 40–80%: starts a chain.
  - 80–100%: starts a chain and affects terrain.
- Resistance: populations inherit a standard resistance by planet/region for select elements; the starting base is 5%.

**Pad layout orientation** (2026-10-23; settles the facing part of spec `07_OPEN_DECISIONS` item 1)
- Every enemy's pad layout is authored in one standard orientation: top-down, enemy facing forward toward the player at the bottom of the screen.
- Front pads are toward the bottom of the layout; rear pads are toward the top. Left and right are from the enemy's own perspective (so the enemy's left is on the screen's right).
- Each numbered pad stays fixed to its local position on the enemy. When the enemy turns in play, the whole layout rotates with it: no renumbering or reclassifying.
- This is the authoring standard, not a limit on how enemies move or face in combat.
- Still OPEN: each pad's local position across the six platform types (the numbering 1, 2–3, 4–7, 8–13, 14–21, 22–31 is already approved).

**Attack delivery patterns** (2026-10-25; the delivery pattern is separate from the element)
- **Single** = 1 enemy. **Double** = 2 different enemies. **Triple** = 3 different enemies. Maybe a 4-enemy pattern. **Mortar AoE** = a blast that hits every enemy inside its radius.
- **All hits are single hits.** An attack hits each affected enemy once, whatever the pattern, so one attack never applies its element to the same enemy twice. Each hit advances that enemy's own stack.
- **Directional pads choose the following targets** of a 2-, 3- (or 4-) enemy attack. The player picks the first target and doesn't necessarily decide where the later attacks go. Magic doesn't travel the pads on every spell. This answers the Lightning question: spec 03's directed pad network now selects targets for multi-target attacks; it isn't a route every spell must travel.
- (2026-10-26) **Fallback:** a multi-target attack shouldn't hit fewer enemies than its count when another enemy is available ("if player is using a 2hit attack it would not do to only hit one"). When the rolled direction runs out, it tries the other side. Only when no eligible enemy is left do the remaining attacks fizzle; hits that already landed stand. (Sim assumption, not authored: it switches once, to the other side of the first target, so it never re-crosses enemies it already hit.)
- (2026-10-26) **No jump range for Double/Triple/Quad:** they reach enemies anywhere on the battlefield, however far apart. With direction plus fallback, they hit their full count whenever enough enemies exist. Mortar is the proximity attack; its blast radius stays a placeholder until the battlefield scale is set.
- Every hit is a full hit with full damage, follow-ups and Mortar victims included. Magic doesn't carry across attacks: no Plasma, no grounding stop between targets. A later spell will deliberately merge effects across enemies.
- The enemy owns one elemental stack. Pads aren't separate stacks; the body-part pads in the scratchpad 3D sims were experimental and are off-spec.
- OPEN: whether every spell gets every pattern or only some spells get Triple or Mortar; the directional selection rules; the Mortar radius.
- OPEN (proposed by another assistant, not ratified): an "Elemental Buster" payoff when a combination completes. Its trigger must not bring back the superseded third-hit limit. Hit regions (leg, torso, head) as a damage modifier.

**Other systems**
- **Dual-element spells:** each element deals its own damage; only the element with the most damage after resistance advances the chain. Non-damaging dual-element spells create no chain hit.
- **Cleansing (Option A):** it removes conditions from friend or foe alike. Healing is a separate operation that goes only to eligible recipients.
- **Moon** = "local shadow of self"; **Shadow** = "ethereal portal of all shadow". They're distinct, they don't inherently cancel, and their reaction is open. Moon's expression is governed by Keen's Queen/Maiden choice, character attributes and planetary conditions.
- **Vale:** his magic is a proposal for how he interacts with the world.
  - Keep the core reasoning: modifiers and buffers, not direct combat. He changes whether, when and how long consequences hold.
  - His influence never advances chains.
  - Implementation comes after the other magic systems.
- **Personal abilities** follow their own definitions. They join a chain only when they produce a condition the elemental physics recognizes.

## Provisional implementation choices (not authored; sketch only)

Listed in the `PROVISIONAL` block at the top of `chain_mr_sketch.py` and `propagation_mr_sketch.py`:
- Hits 4+ use the 3rd-hit bonus band (3–5%).
- Hits 3+ look up a state-based follow-up (`FOLLOW_UP`, empty) first, then the pair (previous, new).
- Elements other than Water/Fire give their final infliction at +0%.
- A repeat hit gets no bonus and no final infliction, and it leaves the stored ongoing damage unchanged.
- 40% start threshold (in `chain_mr_sketch.py` 2026-10-22): measured before resistance, using an optional `strength` field on each hit (default 1.0). Exactly 40% starts a chain. It applies only to starting a chain (including after one closes), not to continuing one. The 80% terrain band isn't modeled.
- Resistance applies to the hit bonus and to stored ongoing damage on entry; the final infliction isn't resisted again.
- Propagation: the element an enemy carries = the last element of its chain. Clay/Ash are read from `Target.conditions` (what creates them isn't modeled). Plasma damage is keyed `plasma`.
- Party cycle (`party_cycle_sketch.py`): a cycle advances once every member has taken one turn; a double turn or an outsider's turn is rejected; a turn with no hits still counts; ongoing damage doesn't tick on advance yet; damage never reads the cycle.

## Open questions (answer these first)

1–3. **Answered 2026-10-22** (see Chain damage above).
4. **Plasma:** does it travel on Lightning's remaining jumps or with its own rules? Does Plasma landing on enemy 5 count in enemy 5's chain?
5. **Propagation vs primary-only.** `vale magic.txt` says jumps are secondary and can't add elements to a chain, but Plasma at enemy 4 comes from a jump. Is that an allowed exception?
6. **Shadow stopping Lightning** contradicts `gptelements.txt` (Shadow → Lightning = Shadow Storm) and `lightning.txt` (Lightning reveals Shadow).
7. **The 40% / 80% boundaries:** which band does each exact value belong to? Can a low-rolled Lightning jump start a chain?
8. **The 5% base resistance:** every element, or only the region's selected element?
9. **Dual-element ties:** recommendation is the spell's declared affinity.
10. **Fire base damage:** `fire.txt` has two drafts of the same common level 1 attack (95 vs 100 with splash). Which one?
11. **"Users stronger"** vs Bronze Flames / Dragon's Roar / Tail Sweep at 75% of Fire base: are AoE spells allowed to be lower, or do they need raising?
12. **Grounding:** stops Lightning's path, but does it end the chain?
13. **Is the Graviton Keeper Vale?** Does `vale magic.txt` replace the Keeper's direct attacks in `graviton magic.txt`?
14. **Library families:** does faction magic (Graviton / Nephoretti / Igigi) become a fourth family? Should `extra spells.txt` get an owner? Do Geralt's rune abilities belong to Geralt or the rune? Does `claude.txt` belong in the library?

## Live kernel facts

- Live kernel: `EngAIn/tier2/godotsim/kernels/combat3d_mr.py`. It only subtracts HP and raises death/low-health alerts. `damage_type` is ignored, and time is in seconds, not turns.
- **Four copies of combat3d_mr.py exist**: `tier1/engainos/core`, `tier2/godotsim/`, `tier2/godotsim/kernels/`, and "EngAIn before dragon". Only `kernels/` is live. Retire the others before adding magic code.
- `test_gateway_combat_rules.py` asserts the payload is exactly `{source, target, amount}`. New damage fields must be optional, and `command_dispatcher.combat_damage_payload`, `runtime_client.py`, the AP rules and the tests must change together.
- Not yet read: `combat3d_integration.py`, `runtime_core.py`, the AP rules, the other combat tests.

## Kernel build order (after questions 1–3)

0. Sketch verified standalone 2026-10-22: `python3 test_chain_mr_sketch.py` (28: damage model, repeats, 40% threshold, boss chain across two party cycles, encounter, Lightning field), `python3 test_chain_zw_bridge.py` (7), `python3 -I chain_mr_sketch.py`. The ZW bridge now accepts optional `{ongoing N}` / `{standard N}` per hit and returns `ongoing` per target. The live kernel hasn't been touched.
0b. **Godot playback (2026-10-22):** `godot_demo/` is a standalone Godot 4.6 project, not in the EngAIn repo. Python writes the log with `python3 encounter_demo.py --json godot_demo/encounter.json`; Godot only displays it (`godot --path godot_demo`; `-- --check` prints the final state headless; `-- --shot` saves `shot.png`). This is a file hand-off, not runtime HTTP.
0c. **30-enemy Lightning field (2026-10-22):** Godot owns positions, Python owns elemental results. `godot --headless --path godot_demo -- --export-field` → `battlefield.json`; `python3 lightning_field.py [--seed N]` → `field.json`; `godot --path godot_demo -- --field`. The walk is provisional: placeholder `JUMP_RANGE` 3.5, a seeded left/right roll, nearest enemy on that side, no obstruction. Playback draws a beam per hop, coloured by the form that arrives.
1. ~~Update `chain_mr_sketch.py` to the damage model~~ done 2026-10-22 (seeded roll per (seed, hit id); FINAL_INFLICTION for other elements = +0% shortcut; the ZW bridge's `ongoing` was added the same day).
2. Extend the live kernel's damage event (element→amount map, primary flag, affinity, recipient policy) and the entity (resistances, statuses, chain), keeping single-element damage as the default.
3. Add turn advancement and statuses.
4. Add a seeded random stream per subsystem (Lightning, reactions, obstruction) and event alerts (`reaction_triggered`, `chain_closed`, `status_applied`).
5. Lightning propagation as its own kernel: a pad-contact budget separate from the entity-damage budget (from research/Gemini).

## Research takeaways (`research/`)

- **Keep:**
  - Lightning's separate pad and entity budgets.
  - Per-spell friendly-fire policy (`HOSTILE_ONLY` / `ALL_COMBATANTS` / `ALLIES_EXCLUDED`).
  - Terrain on world cells, not enemies.
  - One random stream per subsystem.
  - The four replay tests: same seed, save/load, AI, stream stability.
  - Fixed-point math before porting.
  - `IGNORE` / `AMPLIFY` / `APPLY_DAMAGE_REPEATED` for repeated contacts.
  - Nested tags (`Status.Burning`).
- **Drop:**
  - Genshin gauge theory.
  - Fighting-game frame data.
  - Granblue damage caps.
  - Mudstorm as pre-placed map geometry.
  - Reaction suppressing base damage (superseded by the author's damage model).
- **Gemini's invented values:** obstruction rate 0.75–0.90 and 2-per-pad cap (spec 01 has no number). Its code bugs: Volcanic Eruption scales off the Fire spell's power, and its Earth+Water check uses OR.
