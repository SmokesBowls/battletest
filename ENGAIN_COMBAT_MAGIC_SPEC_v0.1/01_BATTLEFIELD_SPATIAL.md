# Battlefield, Platform Topology and Base Forms

## 1. Battle presentation [AUTHOR RULE]

- Old-school Final Fantasy-style battle screen, modified: **four party characters stacked vertically on one side**, enemies and larger combat space on the remainder.
- An attacking character runs toward the target instead of the old bounce-forward-three-times convention.
- After attacking, the character chooses **Stay** near the enemy or **Return** to party formation.
- Stay: defense advantage against the enemy whose platform the character occupies; rear attack exposure reduces guard. Front/side incoming attacks have **no added directional guard modifier** (the enemy-specific stay bonus is its own condition).
- Return: temporarily lowered guard while back-turned during return. Timing and precise modifiers OPEN.
- Two characters may occupy the same platform. This is allowed, but creates **very high combo obstruction/failure risk**; no numerical failure probability selected.
- On-object platforms (body/back/shoulder etc.) are **boss/special encounters only** and must be explicitly authored. Regular battle pads surround enemy footprint.

## 2. Six platform *types* [AUTHOR RULE]

The author drew and numbered six types; platform numbers are **configuration-local labels** reused by any enemy of that type. They are not global unique instance IDs.

| Type | Count | Labels | Initial access |
| --- | ---: | --- | --- |
| 1 | 1 | 1 | Introductory enemies |
| 2 | 2 | 2–3 | Introductory enemies |
| 3 | 4 | 4–7 | Introductory enemies |
| 4 | 6 | 8–13 | Combo-capable encounters |
| 5 | 8 | 14–21 | Combo-capable encounters |
| 6 | 10 | 22–31 | Larger/later encounters |

Total **31 type-specific labels** across the six layouts, **not** 31 pads concurrently on one enemy.

The author's final screenshot/diagram is the geometric reference. An earlier assistant transcription placed type 4 and later pads by top/bottom, but the author also discussed attack-facing orientation; **do not infer global front/back from screenshot page orientation alone.** Preserve the numbering and verify placement vectors from author drawings before writing coordinates.

### Address identity

Correct: `(battle_id, enemy_instance_id, platform_label)` e.g. `(b_017, wolf_b, 6)`.

Incorrect: `platform_6` as a battlefield-global primary key: three enemies can each have a pad 6 simultaneously.

## 3. Three spatial concepts [AUTHOR RULE]

1. **Enemy footprint**: actual space occupied by entity; potentially spans several terrain cells; influences collision/position and directional attack propagation.
2. **Launch / landing pads (numbered platform positions)**: relative to enemy; where characters stand after attacks, where magic contacts a configured enemy, and where local chain routes or combo locks apply.
3. **Base forms (environmental grid)**: fixed terrain cells beneath and extending beyond the enemy footprint and landing pads. Same grid scale as pads in the author's diagrams, but **not** the same state object.

Effects to distinguish:
- Direct entity effect (HP, slow, burning etc.) attached to entity for declared lifetime.
- Spatial/environmental effect (unstable ground, mud, lava, steam) attached to **base-form cells**; remains at world location if enemies move away.
- Pad route/occupancy/numbering is spatial interface, **not persistent terrain storage**.
- AoE footprint may cover pink standing locations. Any eligible occupant of affected cells can be hit, including allies if that spell's friendly-fire policy permits it. Source of AoE is not constrained to pad network.

**OPEN:** How to preserve a spell's *chain qualification* at an attack contact when enemy pads follow moving enemies but terrain conditions remain fixed. Candidate: resolve current pad's world-overlapped base-form cells at moment of contact; no automatic attachment of old terrain condition to moving enemy.

## 4. Geometry and connections [AUTHOR RULE / OPEN]

- A platform geometry template may be proportionally placed around enemy physical dimensions, not around arbitrary HP levels.
- **Combination-lock connections**, **Lightning traversal connections**, and **terrain-cell adjacency** are distinct graphs. They must not be silently assumed identical.
- Actual physical proximity is not sufficient to make a character combo valid; authored lock relationships decide.
- The field has a broader environmental grid on which enemies can reposition and attacks can pass through.
- A 10-pad arrangement has side middle pads 24 and 29; author floated **90% rather than 100%** effect for them. Not finalized.
- Attack-direction penetration percentages **100%, 60%, 20%, 5%** were proposed as test settings, not canonical damage constants. They indicate first/front-facing hit, rear-facing hit, further/behind hit, far rear hit in examples. Exact relationship to facing, actual targets and damage math OPEN.

## 5. Spatial declaration sketch [DESIGN PROPOSAL ONLY]

```text
Battle:
  entities: [<instance ids>]
  base_forms: world_grid[<cell ids and persistent effects>]
  enemy_instances:
    <enemy_instance_id>:
      platform_type: 4
      footprint: <authored or derived extent>
      orientation: <facing>
      platforms:
        8: {local_position: ?, occupants: []}
        9: {local_position: ?, occupants: []}
        ...
      combo_locks: <authored references>
      lightning_paths: <authored local edges>
```

Positions/edges shown with `?` are intentionally missing rather than invented.
