# Character Combos: Locks, Obstruction and Learning

## 1. Author-approved platform progression

- Types 1–3 (pads 1–7) are early enemies; no character combination availability is required.
- Type 4 (6 pads) introduces defined two-character locks.
- Type 5 (8 pads) adds paired pads along multiple sides.
- Type 6 (10 pads) supports pairs and dedicated three-along-side triples.
- **Combo availability is not identical to elemental chain magic**. Character team formations and spell-element progressions are separate mechanics that can interact.

## 2. Specified two-character combo pad locks [AUTHOR RULE]

| Type | Dual pad locks explicitly specified |
| --- | --- |
| 4 (8–13) | `{8,13}`, `{10,11}` |
| 5 (14–21) | `{14,21}`, `{15,16}`, `{17,18}`, `{19,20}` |
| 6 (22–31) | **OPEN** exact authored pairs. Prior assistant *proposed* `{22,31}`, `{26,27}`, `{23,24}`, `{24,25}`, `{28,29}`, `{29,30}`. Not yet author ratified. |

Here `{a,b}` denotes a **platform pair lock** for character combo eligibility, NOT a Lightning path or world-grid adjacency.

## 3. Three-character combos [AUTHOR RULE / INFERENCE]

- Author suggested **three along left side** and **three along right side** of the 10-pad configuration as basic positional triple locks.
- Based on numbered diagram, likely candidate groups are `{23,24,25}` and `{28,29,30}` **[DESIGN PROPOSAL; verify exact side assignments]**.
- Triple combination eligibility itself requires a learn/unlock condition; position alone doesn't grant skill.
- At **mastered triple** level, any *valid two-platform lock* may accept an eligible third platform in a permitted relation, even on the 6-pad enemy.

Author's concrete advanced examples:

| Existing dual lock | Eligible added single | Advanced triple |
| --- | --- | --- |
| 8+13 | 9 | 8+13+9 |
| 8+13 | 12 | 8+13+12 |
| 10+11 | 9 | 10+11+9 |
| 10+11 | 12 | 10+11+12 |

These are explicit examples, not proof that **any** third pad qualifies for **every** dual lock.

## 4. Obstruction [AUTHOR RULE]

- Multiple allies can stand on one enemy platform.
- An attempted combination using overcrowded/overlapping positions has an **extremely high chance of failure**, not automatic disqualification.
- Do not invent the exact failure chance; tuning is empirical.
- 'Cannot attempt' (no eligible lock/qualification) differs from 'valid attempted combo that fails' (obstruction/random result).

## 5. Learning progression [AUTHOR INTENT; implementation details PROPOSED]

Author: use combinations to improve them; a qualifying condition must exist to learn combos **at all**, and another to learn/perform triple combos.

Suggested separate facts:

- Known/unlocked ability for character(s)
- Qualified participants and required learned skills
- Pair/trio coordination progression through actual use
- Attack-specific proficiency
- Eligibility of current physical platform lock

Do not silently tie combo mastery to elemental chain mastery. Exact thresholds, experience awards, failed-attempt learning, and whether learning is per party/pair/trio are OPEN.

## 6. Action lifecycles

Character attacks enemy → chooses stay/return → formation occupancy updated → if eligible members occupy pads satisfying a lock, allow combo action when learned and other conditions hold → roll obstruction if overlapping → resolve combo's authored effects. Enemy response, timing and cooldowns remain OPEN.
