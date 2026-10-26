#!/usr/bin/env python3
"""
court_sim.py - DISPOSABLE full-court stress test: 30 enemies (5 each of 1/2/4/6/8/10 pads,
155 pads), 4 heroes, the same fresh board replayed at hero levels 1-10.

Travel rules come from travel_sim.cast unchanged (X1-X7 there). Stress-test exception: all six
enemy sizes on one board is NOT a progression decision.

EXPERIMENTAL here:
  C1. ROUNDS full party rounds per fight; FIGHTS seeded fights per (level, mode, plan).
  C2. Plans: same   = all four heroes cast one element per round (random each round),
                      all starting on one party-chosen enemy;
             ordered = earth, water, fire, lightning in hero order, one party-chosen enemy;
             ordered-split = same order, each hero picks its own enemy;
             random  = each hero a random element and its own enemy.
  C3. Triple = earth, water, fire landing on the SAME pad consecutively in one unbroken pad chain
      (counted from pad history; independent of whether Volcanic Eruption is ratified).
  C4. "Affected" enemy = at least one pad touched. No damage or HP (no authored values).
"""

import random
import sys
from collections import Counter

sys.path.insert(0, sys.argv[1] if len(sys.argv) > 1 else ".")
import travel_sim  # noqa: E402
from chain_mr_sketch import Chain  # noqa: E402

SIZES = tuple(n for n in (1, 2, 4, 6, 8, 10) for _ in range(5))
ROUNDS, FIGHTS = 6, 400
ORDER = ("earth", "water", "fire", "lightning")
PLANS = ("same", "ordered", "ordered-split", "random")


class Pick(random.Random):
    """Start the cast on a chosen enemy: travel_sim.cast's first randrange picks the enemy."""
    def __init__(self, seed, enemy):
        super().__init__(seed)
        self._enemy = enemy

    def randrange(self, *a, **k):
        if self._enemy is not None:
            e, self._enemy = self._enemy, None
            return e
        return super().randrange(*a, **k)


def fight(level, mode, plan, seed):
    rng = random.Random(f"{seed}:{plan}")  # shared by both modes: same elements and targets
    board = [[Chain() for _ in range(n)] for n in SIZES]
    s = Counter()
    for r in range(ROUNDS):
        party_target = rng.randrange(len(board))
        round_el = rng.choice(travel_sim.POOL)
        for h in range(4):
            el = {"same": round_el, "random": rng.choice(travel_sim.POOL)}.get(plan, ORDER[h])
            target = party_target if plan in ("same", "ordered") else rng.randrange(len(board))
            path, end = travel_sim.cast(board, level, el, mode, Pick(f"{seed}:{plan}:{r}:{h}:{mode}", target))
            s["casts"] += 1
            s["contacts"] += len(path)
            s["budget"] += travel_sim.LEVELS[level][0]
            s["stuck"] += end == "stuck"
            s["stuck_on_1pad"] += end == "stuck" and SIZES[path[-1][0]] == 1
            s["lightning"] += el == "lightning"
            s["blocked"] += end == "blocked"
            for _, _, _, b, a in path:
                k = travel_sim.kind(b, a, el)
                s[k] += 1
                s["triple"] += el == "fire" and not b.closed and b.elements[-2:] == ("earth", "water")
    s["affected"] = sum(any(p.elements for p in e) for e in board)
    s["untouched"] = sum(not p.elements for e in board for p in e)
    s["conditions"] = len({p.state or p.elements[-1] for e in board for p in e if p.elements})
    return s


def main():
    for plan in PLANS:
        print(f"\n## plan={plan} - focused | distributed ({FIGHTS} fights x {ROUNDS} rounds, means per fight)\n")
        print("| lvl | enemies affected /30 | pads untouched /155 | triples | conversions / unresolved "
              "| budget used | casts stuck (on 1-pad) | Lightning blocked |")
        print("|---:|---|---|---|---|---|---|---|")
        for level in range(1, 11):
            ts = []
            for mode in ("focused", "distributed"):
                t = Counter()
                for seed in range(FIGHTS):
                    t += fight(level, mode, plan, seed)
                ts.append(t)
            f = lambda fn: " \\| ".join(fn(t) for t in ts)
            print(f"| {level} | {f(lambda t: f'{t['affected'] / FIGHTS:.1f}')} "
                  f"| {f(lambda t: f'{t['untouched'] / FIGHTS:.0f}')} "
                  f"| {f(lambda t: f'{t['triple'] / FIGHTS:.2f}')} "
                  f"| {f(lambda t: f'{t['convert'] / FIGHTS:.1f} / {t['unresolved'] / FIGHTS:.1f}')} "
                  f"| {f(lambda t: f'{t['contacts'] / t['budget']:.0%}')} "
                  f"| {f(lambda t: f'{t['stuck'] / t['casts']:.0%} ({t['stuck_on_1pad'] / t['casts']:.0%})')} "
                  f"| {f(lambda t: f'{t['blocked'] / max(1, t['lightning']):.0%}')} |")


def self_check():
    b = [[Chain() for _ in range(n)] for n in SIZES]
    assert len(b) == 30 and sum(SIZES) == 155
    for e in range(30):  # Pick really starts the cast on the chosen enemy
        path, _ = travel_sim.cast(b, 3, "water", "focused", Pick(e, e))
        assert path[0][0] == e
    # same seed, both modes: identical elements and party targets (only travel differs)
    assert fight(1, "focused", "same", 3)["contacts"] == fight(1, "distributed", "same", 3)["contacts"]
    print("self-check OK: 30 enemies / 155 pads, chosen start enemy honoured, modes share seeds")


if __name__ == "__main__":
    self_check()
    main()
