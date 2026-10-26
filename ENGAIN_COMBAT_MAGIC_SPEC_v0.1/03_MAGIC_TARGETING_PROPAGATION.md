# Magic Targeting, Routing and Reaction Semantics

## 1. Spell categories [AUTHOR RULE]

1. **Single-target**: a spell impacts one selected/rolled enemy pad/target; no implicit AoE. Damage, entity status and base-form terrain effects may have separate scopes.
2. **Directional chain propagation**: paths between local pads and eligible inter-enemy entry pads; randomized **among valid exits**, never through arbitrary consecutive integers.
3. **Area-of-effect (AoE)**: aim at a **world-grid location within caster range**; AoE geometry comes from the particular spell and covers its actual base-form cells, not its enemy pad numbers. Character may miss enemies completely. Optional fallback for early implementation: target/snap to cells/pads, without redefining spell laws.
4. **Elemental combo reaction**: a traveling spell contacts a qualifying existing spell/element state and yields a named interaction; propagation's continuation depends on **the elements/reaction**, not one general rule.
5. **Triple chain**: qualifying third element strikes a prepared double chain; author currently says third-chain interaction **terminates incoming Lightning path** while enhancing the triple effect. May be refined later.
6. **Physical weapon attacks**: initial scope basic strike/double/retaliate and visually compelling animations; must not bypass guard, health, existing physical damage surfaces or authoritative kernel.

## 2. Chain trigger, resolution ordering [AUTHOR RULE + OPEN]

- Earth spell at pad/base-form contact may establish Earth prime.
- Later Water aimed/landed at **that same qualifying contact** triggers Earth→Water **Mudstorm** instead of full standalone Tidal Surge. A different contact executes normal Water.
- Later Fire at that same valid Earth→Water chain triggers **Volcanic Eruption**.
- After triggering, chain output creates entity damage/status and **persistent spatial terrain changes on base forms** as defined.
- **Do not** apply full triggering base spell and full combo spell twice by default. Keep effects from previous turns according to their own duration unless explicitly consumed/transformed; exact stacking and consumption OPEN.
- Encountering a primed location is not always a forced stop. For Lightning specifically: Water may allow/strengthen continuation; Earth grounds/stops; Fire creates Plasma; triple-chain interaction currently stops incoming Lightning's regular traversal while the triple reaction resolves.
- Fallback from unlisted ordered combination to a reverse-ordered definition was proposed for Water→Lightning using Lightning+Water, **not** approved as universal commutativity. Direction/order of elements matters in source documents.

## 3. Lightning path rules [AUTHOR RULE]

- Lightning follows an explicit **directional local-pad network** on each enemy, plus valid spatial jumps between different enemy entities.
- At an internal pad choose left/right relative to incoming trajectory, **only among valid exits**. No backwards traversal, no illegal straight shortcut through the same enemy, and no hopping over required intermediate pads.
- Cross-enemy jumps can be straight or diagonal according to actual enemy layout. Destination pad number can be **lower** and need not be the next number. Different enemies can have identical local pad labels.
- If outward jump to another enemy is unavailable, Lightning continues along an available permitted local-pad path; if no path exists, it fizzles.
- Example four-pad local paths: `4→5→6`, `4→7→6`; not `4→6` directly. Pad 5 or 7 may exit to another enemy when eligible, otherwise proceed toward 6. At pad 6, try valid inter-enemy exit or fizzle.
- Example eight-pad: 15 must first go to 16 before seeking another enemy; 16 may continue toward 17 or exit, depending on layout. An authored illustrative path was `14→15→16` to reach a Water-prime at 16.
- Examples of inter-enemy jumps: `6→2`; `17→31` and `18→22` as diagonally preferred possibilities for particular enemy arrangements. These numbers belong to **different enemy instances**, not one creature.
- Pad 1 is a terminal for Lightning (no onward pad); Type 2 may traverse `2→3` and jump outward. Early enemy health is independent from route definition.
- Multiple enemies each with type 3 all use labels 4–7; use composite instance+label ID.

## 4. Target count vs pad hops [IMPORTANT OPEN CONFLICT]

Recovered **Thunder's Wrath** says basic Lightning may chain to **one additional nearby target for 50% base damage**. Author wants many pad *contacts* to form a route within one enemy; contacts do not automatically mean distinct damaged enemies.

Potential model [PROPOSAL]:
- `pad_contacts` for path traversal;
- `distinct_entity_hits` counts additional target allowance;
- `level/skill` governs how many distinct additional enemies can be hit;
- an elemental combo like Aqua Lightning may have its own hit allowance and propagation policy.

**Not established:** how many local pad hops a level-one Lightning cast may make, whether each contact damages the same enemy again, whether the full path is permitted when no secondary target is available, and how original 'nearest' language coexists with directed trajectory. Do not implement inferred answer as canon.

## 5. Elemental encounter routing [AUTHOR RULE; behavior table partly provisional]

| Incoming | Contact state | Outcome | Continue ordinary Lightning path? |
| --- | --- | --- | --- |
| Lightning | Water | Conductive interaction / Aqua Lightning (historical file: Lightning+Water) | Yes, may continue; exact additional hops/hits OPEN |
| Lightning | Earth | Grounding interaction | **No**, current authored rule |
| Lightning | Fire | Plasma transformation / Blazing Plasma | Reaction effect occurs; onward propagation OPEN |
| Lightning | Qualifying preexisting double | Triple-chain interaction | **No** for original Lightning route per latest summary; triple has independent effects |
| Any | Unrecognized element | Evaluate authored rule or explicitly unresolved | No guessed universal stop or conversion |

Author explicitly corrected assistant's earlier 'every combo stops Lightning' assumption.

## 6. AoE footprint families [DESIGN PROPOSAL, NOT LOCKED]

Author drawings illustrated radial/eruption, three-way branch, forward line/pierce and other directional effects. Pattern geometry is spell-specific and independent of the enemy pad topology.

- `single` — one grid cell/occupant
- `line` — world-grid trajectory with optional penetration
- `fork_3` — three-direction spread relative to cast orientation
- `cross_4` — center + orthogonal neighbors
- `radial` — authored blast radius/shape
- `chain_jumps` — **different mechanic**, graph traversal, not ordinary AoE

These strings are suggestions, not actual existing ZW opcodes. Accuracy/scatter, self-hit, friendly fire, cover, resistance and terrain conversion need explicit spell rules.

## 7. Randomness [AUTHOR RULE]

- Impact choice may be randomized within permitted pads, so chain priming is not guaranteed.
- Lightning left/right choices randomized when both options valid.
- Proficiency may tune hit probability and extent, but no functions/thresholds approved.
- Keep seed and roll trail in diagnostic output for deterministic replay; does not authorize simulation mutation from presentation.
