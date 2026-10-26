#!/usr/bin/env python3
"""
travel_sim.py - DISPOSABLE: magic that travels pad to pad, across several enemies.

Author direction (2026-10-24, experimental):
  - Spell level = pad-contact budget; a separate cap on how many enemies it may reach.
    L1 1 contact/1 enemy, L2 2/1, L3 3/2, L4 4/2; L5-L10 enemy caps 2,3,3,3,4,4.
  - Every contacted pad advances its OWN chain (chain_mr_sketch.advance, unchanged).
  - Travel is random among valid next pads; a blocker only matters if the path actually lands on it.
  - Enemy pad counts are independent of magic level.
  - Focused vs distributed targeting (like "All" in FF), compared on the same seeds.

EXPERIMENTAL (not authored):
  X1. L5-L10 contacts = level (only the enemy caps were given).
  X2. Neighbours: pads in label order as a ring (real layouts still OPEN).
  X3. Start: a random pad on the selected enemy (selection random). A spell never revisits a pad.
  X4. Next contact: random unvisited neighbour on this enemy; otherwise jump to a random pad of a
      random not-yet-reached enemy (if the enemy cap allows); otherwise the spell ends early.
  X5. Focused: stay on an enemy until stuck. Distributed: at most ceil(contacts / enemy cap)
      contacts per enemy, then jump.
  X6. Stops apply to Lightning only (propagation rule): a pad whose carried element is earth or
      shadow takes the contact, then the bolt stops. Lightning on a fire pad becomes Plasma and
      continues; later pads still receive "lightning" in their chains (Plasma's own chain rule is OPEN).
  X7. Enemy-level chain: only the first contact is primary (step_chain, one hit per cast).
  X8. 4 casts per battle, element uniform from water/fire/earth/lightning, all enemies in range.
"""

import math
import random
import sys
from collections import Counter

sys.path.insert(0, sys.argv[1] if len(sys.argv) > 1 else ".")
from chain_mr_sketch import Chain, Target, advance, step_chain  # noqa: E402

LEVELS = {1: (1, 1), 2: (2, 1), 3: (3, 2), 4: (4, 2), 5: (5, 2), 6: (6, 3),
          7: (7, 3), 8: (8, 3), 9: (9, 4), 10: (10, 4)}
GROUPS = {"early 1+2+4 pads": (1, 2, 4), "mid 4+6+6 pads": (4, 6, 6), "late 6+8+10 pads": (6, 8, 10)}
POOL = ("water", "fire", "earth", "lightning")
STOPS = {"earth", "shadow"}
CASTS, BATTLES = 4, 2000


def ring(i, n):
    return sorted({(i - 1) % n, (i + 1) % n} - {i}) if n > 1 else []


def cast(field, level, element, mode, rng, hp=None):
    """field: list of enemies, each a list of pad Chains (mutated). Returns a path record.
    hp: optional per-enemy health list (mutated): 1 damage per contact (EXPERIMENTAL); a dead enemy
    takes no more contacts, the spell travels on within its enemy cap (the dead enemy still counts)."""
    contacts, cap = LEVELS[level]
    per_enemy = math.ceil(contacts / cap) if mode == "distributed" else contacts
    e = rng.randrange(len(field))
    pad = rng.randrange(len(field[e]))
    reached, visited, used, path = [e], {(e, pad)}, Counter(), []
    form = element
    while True:
        before = field[e][pad]
        field[e][pad], _ = advance(before, element)
        used[e] += 1
        if hp is not None:
            hp[e] -= 1
        path.append((e, pad, form, before, field[e][pad]))
        carried = before.elements[-1] if before.elements else None
        if element == "lightning" and carried in STOPS:
            return path, "blocked"
        if element == "lightning" and carried == "fire":
            form = "plasma"
        if len(path) == contacts:
            return path, "budget"
        nxt = [p for p in ring(pad, len(field[e])) if (e, p) not in visited] if used[e] < per_enemy and (hp is None or hp[e] > 0) else []
        if nxt:
            pad = rng.choice(nxt)
        else:
            others = [x for x in range(len(field)) if x not in reached and (hp is None or hp[x] > 0)]
            if not others or len(reached) >= cap:
                return path, "stuck"
            e = rng.choice(others)
            reached.append(e)
            pad = rng.randrange(len(field[e]))
        visited.add((e, pad))


def kind(before, after, element):
    if before.closed or not before.elements:
        return "single"
    if element == before.elements[-1]:
        return "repeat"
    return "convert" if after.state else "unresolved"


def battle(sizes, level, mode, seed):
    rng = random.Random(f"{seed}:{level}:{sizes}")  # same seed -> same elements & starts per mode
    elements = [rng.choice(POOL) for _ in range(CASTS)]
    field = [[Chain() for _ in range(n)] for n in sizes]
    enemies = {f"e{i}": Target(1e9, {}) for i in range(len(sizes))}
    stats = Counter()
    for c, el in enumerate(elements):
        path, end = cast(field, level, el, mode, random.Random(f"{seed}:{level}:{sizes}:{c}:{mode}"))
        stats["casts"] += 1
        stats["contacts"] += len(path)
        stats["budget"] += LEVELS[level][0]
        stats[f"end_{end}"] += 1
        stats["enemies_reached"] += len({p[0] for p in path})
        stats["on_first_enemy"] += sum(p[0] == path[0][0] for p in path)
        stats["lightning_casts"] += el == "lightning"
        stats["plasma_contacts"] += sum(p[2] == "plasma" for p in path)
        for _, _, _, b, a in path:
            stats[kind(b, a, el)] += 1
        enemies, _, _ = step_chain(enemies, [{"id": f"c{c}", "target": f"e{path[0][0]}", "primary": True,
                                              "damage": {el: 100.0}}], seed)
    for pads in field:
        touched = [p for p in pads if p.elements]
        stats["pads"] += len(pads)
        stats["untouched"] += len(pads) - len(touched)
        shown = {p.state or p.elements[-1] for p in touched}
        stats["enemies_with_mixed_pads"] += len(shown) > 1
        stats["enemies"] += 1
    return stats


def main():
    for gname, sizes in GROUPS.items():
        print(f"\n## {gname} - focused | distributed (same seeds)\n")
        print("| lvl | contacts used / budget | enemies reached per cast | share on first enemy "
              "| ended early (stuck / Lightning blocked) | convert / unresolved per contact "
              "| untouched pads | enemies with mixed pads |")
        print("|---:|---|---|---|---|---|---|---|")
        for level in LEVELS:
            cells = []
            for mode in ("focused", "distributed"):
                t = Counter()
                for s in range(BATTLES):
                    t += battle(sizes, level, mode, s)
                cells.append(t)
            f = lambda fn: " \\| ".join(fn(t) for t in cells)
            print(f"| {level} | {f(lambda t: f'{t['contacts'] / t['budget']:.0%}')} "
                  f"| {f(lambda t: f'{t['enemies_reached'] / t['casts']:.2f}')} "
                  f"| {f(lambda t: f'{t['on_first_enemy'] / t['contacts']:.0%}')} "
                  f"| {f(lambda t: f'{t['end_stuck'] / t['casts']:.0%} / {t['end_blocked'] / max(1, t['lightning_casts']):.0%}')} "
                  f"| {f(lambda t: f'{t['convert'] / t['contacts']:.0%} / {t['unresolved'] / t['contacts']:.0%}')} "
                  f"| {f(lambda t: f'{t['untouched'] / t['pads']:.0%}')} "
                  f"| {f(lambda t: f'{t['enemies_with_mixed_pads'] / t['enemies']:.0%}')} |")


def self_check():
    rng = random.Random(1)
    for level, (contacts, cap) in LEVELS.items():
        for mode in ("focused", "distributed"):
            for s in range(200):
                field = [[Chain() for _ in range(n)] for n in (4, 6, 6)]
                path, end = cast(field, level, rng.choice(POOL), mode, random.Random(s))
                assert len(path) <= contacts and len({p[0] for p in path}) <= cap
                assert len({(p[0], p[1]) for p in path}) == len(path)  # no revisits
                if mode == "distributed":
                    assert max(Counter(p[0] for p in path).values()) <= math.ceil(contacts / cap)
                for a, b in zip(path, path[1:]):  # same-enemy moves go to a ring neighbour
                    assert a[0] != b[0] or b[1] in ring(a[1], len(field[a[0]]))
    print("self-check OK: budget, enemy cap, no revisits, per-enemy cap, neighbour moves")


if __name__ == "__main__":
    self_check()
    main()
