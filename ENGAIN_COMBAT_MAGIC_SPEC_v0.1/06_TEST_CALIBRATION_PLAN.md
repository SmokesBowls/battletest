# Combat Test Harness & Balance Calibration

## Design goal

Build a **working test environment before fixing enemy HP**. Keep authored spell magnitudes and behavior; calibrate durability to observed damage, healing demand, action economy, combo frequency and desired encounter rounds.

## Harness rules [AUTHOR INTENT]

- Four player characters; one or more enemies on numbered platform types; environment base-form grid.
- First isolate basic physical attacks, Earth/Water/Fire; then add elemental chains, Lightning routing, AoE, combos.
- Target can be made **nonlethal for calibration** while retaining normal damage accounting. Do not let an 'unlimited HP' placeholder overflow counters or accidentally trigger death/health logic; record virtual damage in the harness without rewriting Combat3D law.
- After offensive baseline, **realistic combat** must have enemy counterattacks between player actions: healing, defending and movement may consume party actions that otherwise could deal damage.
- Use repeated simulations and deterministic seeds to compare random route outcomes.

## Two calibration modes

### A. Offensive ceiling

Enemy disabled from responding and cannot die. Four characters execute permitted actions. Measure per cast:
- normal hit, chain trigger, missed prime, combo attempt, random landing
- direct damage vs damage over time vs area splash vs propagated target damage
- status change, terrain effects, penetration, mitigations
- aggregate by party round and three-round cumulative total

### B. Realistic combat

Enemy actively attacks. Record for each party round:
- attacks used / heals / defenses / reposition / interrupts
- actual damage (including DoT only when tick occurs)
- enemy damage and survivability, actions diverted to healing
- chain windows missed because sequence interrupted
- combo availability and obstruction failure rate
- encounter completion rounds, remaining player HP/MP and deaths

## HP derivation

If party deals total **70 damage per full round**, an uninterrupted three rounds produce **210**. Choosing enemy HP **greater than 210** ensures survival through those three rounds **only for that measured scenario** (and ignoring same-time DoT/timing). The realistic three-round result may be lower due to healing, or higher when magic chains/procs apply. Therefore:

1. Record cumulative per-round damage distribution under many seeds/scenarios.
2. Pick desired earliest/typical survival round per enemy tier.
3. Choose HP against observed cumulative damage *and* combat survivability, rather than weakening original attacks to fit arbitrary HP=100.
4. Re-test with character mastery, terrain, enemy count, and spell upgrades.
5. Tune provisional penetration percentages (100/60/20/5, optional 90 for middle pad) if simulation shows the geometry produces bad outcomes.

## Suggested test milestones [PROPOSED]

- **M0 Contract audit:** inventory existing Combat3D, AP trust path, ZW data structures, entity surfaces, movement, spatial owners. No edits.
- **M1 Geometry:** spawn four party positions, one enemy with type 1–6 pad layout and fixed world base forms; deterministic coordinates.
- **M2 Basic hit:** physical attack, guard, stay/return, event inspection.
- **M3 Environmental singles:** Ground Tremor, Tidal Surge; entity vs base-form effects, movement out of mud.
- **M4 Double/triple:** Earth→Water→Fire, no double counting, AoE coverage, expiries.
- **M5 Lightning:** deterministic path + RNG branch + multi-enemy jump + Water/Fire/Earth reactions.
- **M6 Team locks:** dual/triple pad validation, learning, mastery, obstruction.
- **M7 Balance:** offensive-ceiling and realistic enemy-response runs, derive starting HP.
- **M8 Godot rendering:** show movement, spell footprint, target numbers and snapshots; render only after authoritative results.

Do not silently mutate repository, alter AP laws, promote archival spell drafts, or reorganize source tree while conducting design review.
