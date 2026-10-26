#!/usr/bin/env python3
"""
delivery_sim.py - DISPOSABLE test of attack delivery patterns (author decisions 2026-10-25).
Originals (travel_sim, court_*, court3d/) are imported or left alone, never changed.

AUTHOR-APPROVED (2026-10-25):
  - Patterns: Single = 1 enemy, Double = 2 different enemies, Triple = 3, (maybe) Quad = 4,
    Mortar = every enemy inside the blast.
  - All hits are single hits: one hit per enemy per attack. Every hit is a full hit (full damage,
    applies its element, advances that enemy's ONE stack), follow-ups and Mortar victims included.
  - The player picks the first target; directional selection picks the follow-ups.
  - Magic is not carried across attacks: no Plasma form, no grounding stop between targets.
    Each hit is just its element on that enemy's stack (chain_mr_sketch.advance, unchanged).

AUTHOR (2026-10-26): fallback - a 2-hit attack must not hit only one when another enemy is available.
  When the rolled direction runs out, the attack tries the other side. Only if neither side has an
  eligible enemy do the remaining attacks fizzle; hits that already landed stand.
  S0 (sim assumption): the fallback switches ONCE, to the other side of the FIRST target, and continues
  from there, so it never crosses back over enemies it already hit.
  Run with --no-fallback for the earlier provisional rule (results_delivery_nofallback.md).

SIMULATION ASSUMPTIONS (not canon):
  S1. Direction: the attack rolls left/right of the first target (screen x, seen from the heroes) and hops
      to the nearest unhit enemy on that side, again and again, never crossing back past the first target.
      (Replaced 2026-10-26: "keep going ahead of the last jump" left scattered Quads short with enemies left.)
  S2. Eligible = not yet hit by this attack. No range limit for Double/Triple/Quad (author 2026-10-26:
      they reach across the battlefield); only Mortar is proximity-based.
  S3. Mortar lands on the first target's position, radius MORTAR_R.
  S4. Party plan: E>W>F>L, 3 rounds. TESTING SHORTCUTS, not combat rules. Opener (who each hero picks first):
      shared = one random enemy for the whole party per round (the main tables);
      independent = each hero picks its own first target (uniform random stands in for the player);
      spread = each hero picks a different enemy (a player deliberately splitting the party).
  S5. Full damage means every hit clears the 40% chain-start threshold, so it never blocks here.
"""

import math
import random
import sys
from collections import Counter

sys.path.insert(0, sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("-") else ".")
sys.path.insert(0, __file__.rsplit("/", 1)[0])
import court_orders  # noqa: E402
import travel_sim  # noqa: E402
from chain_mr_sketch import Chain, advance  # noqa: E402

ORDER = court_orders.ORDERS["E>W>F>L"]
ROUNDS = 3
MORTAR_R = 2.0  # placeholder until the battlefield scale is set
FALLBACK = "--no-fallback" not in sys.argv
PATTERNS = {"single": 1, "double": 2, "triple": 3, "quad": 4, "mortar": None}
# Enemy positions (x, z) on the battle plane; heroes stand at +z looking toward -z.
FIELDS = {
    "row4": [(-6, 0), (-2, 0), (2, 0), (6, 0)],
    "row6 tight": [(-5, 0), (-3, 0), (-1, 0), (1, 0), (3, 0), (5, 0)],
    "wedge7": [(0, 0), (-2, -1.5), (2, -1.5), (-4, -3), (0, -3), (4, -3), (-6, -4.5)],
    "scatter8": [(-5, 1), (-2.5, -2), (0, 0.5), (1.5, -3.5), (3, 1), (5.5, -1), (-4, -4), (7, 2)],
}


def dist(a, b): return math.hypot(a[0] - b[0], a[1] - b[1])


def blast(field, point):
    """Mortar: every enemy within MORTAR_R of the blast point."""
    return [e for e in range(len(field)) if dist(field[e], point) <= MORTAR_R]


def targets(field, first, pattern, rng, fallback=True):
    """Enemies one attack hits, in order, how many attacks fizzled, and each hit's side (+1/-1) of the first target."""
    n = PATTERNS[pattern]
    if n is None:  # S3
        return [first] + [e for e in blast(field, field[first]) if e != first], 0, []
    x0, side = field[first][0], rng.choice((-1, 1))
    hit, sides = [first], []
    for s in (side, -side) if fallback else (side,):  # S0: the rolled side, then the other side of the first target
        pool = [e for e in range(len(field)) if e != first and ((field[e][0] - x0) * s > 0 or (field[e][0] == x0 and s == side))]
        at = first
        while pool and len(hit) < n:
            at = min(pool, key=lambda e: dist(field[e], field[at]))
            pool.remove(at)
            hit.append(at)
            sides.append(s)
    return hit, n - len(hit), sides


def fight(field_name, pattern, seed, log=None, opener="shared"):
    field = FIELDS[field_name]
    rng = random.Random(f"{seed}:delivery:{field_name}")  # same stream for every pattern
    board = [Chain() for _ in field]
    s = Counter()
    for r in range(ROUNDS):
        first = rng.randrange(len(field))  # drawn in every mode so the shared stream never shifts
        spread = random.Random(f"{seed}:{r}:spread").sample(range(len(field)), len(ORDER))
        for h, el in enumerate(ORDER):
            if opener == "independent":
                first = random.Random(f"{seed}:{r}:{h}:open").randrange(len(field))
            elif opener == "spread":
                first = spread[h]
            hit, fizz, _ = targets(field, first, pattern, random.Random(f"{seed}:{r}:{h}"), FALLBACK)
            s["casts"] += 1
            s["hits"] += len(hit)
            s["fizzled"] += fizz
            s["short"] += fizz > 0
            for e in hit:
                before = board[e]
                board[e], _ = advance(before, el)
                k = travel_sim.kind(before, board[e], el)
                s[k] += 1
                if k == "convert":
                    s[f"r:{board[e].state}"] += 1
            s[f"seq:{tuple(hit)}"] = 1
            if log is not None:
                log.append((r + 1, h + 1, el, first, hit, fizz, [board[e] for e in hit]))
    s["touched"] += sum(c != Chain() for c in board)
    s["deep"] += sum(len(c.elements) >= 3 for c in board)  # stacks with 3+ elements (where a payoff could sit)
    stacks = Counter(c.elements for c in board if c.elements)
    s["twins"] += sum(n for n in stacks.values() if n > 1)  # enemies whose whole stack is identical to another's
    s["sequences"] += sum(k.startswith("seq:") for k in s)
    s["distinct stacks"] += len(stacks)
    for k in [k for k in s if k.startswith("seq:")]:
        del s[k]
    return s


def self_check():
    for name, field in FIELDS.items():
        for pattern, n in PATTERNS.items():
            for seed in range(200):
                for first in range(len(field)):
                    for fb in (True, False):
                        hit, fizz, src = targets(field, first, pattern, random.Random(seed), fb)
                        assert hit[0] == first and len(set(hit)) == len(hit), "an enemy hit twice by one attack"
                        if n is None:
                            assert set(hit) == {e for e in range(len(field)) if dist(field[e], field[first]) <= MORTAR_R}
                            continue
                        assert len(hit) + fizz == n
                        x0 = field[first][0]  # a branch never crosses to the other side of the first target
                        assert all((field[e][0] - x0) * sd >= 0 for e, sd in zip(hit[1:], src))
                        assert src == sorted(src, key=src.index), "returned to a side it had left"
                        if fb:
                            assert fizz == max(0, n - len(field)), "fallback: fell short while enemies were left"
    # Each hit is just advance() on that enemy: replaying the logged hits rebuilds the same stacks.
    for seed in range(50):
        log = []
        fight("scatter8", "triple", seed, log)
        board = [Chain() for _ in FIELDS["scatter8"]]
        for *_, el, _first, hit, _fz, after in log:
            for e, a in zip(hit, after):
                board[e], _ = advance(board[e], el)
                assert board[e] == a
    print("self-check OK: one hit per enemy per attack; counts + fizzles = pattern size; mortar = exactly the "
          "enemies in radius; fallback reaches the full count whenever enemies are left; branches never cross the first target; stacks = plain advance() per hit",
          file=sys.stderr)


def main(fights=500):
    print(f"# Delivery patterns: Single / Double / Triple / Quad / Mortar ({fights} fights x {ROUNDS} rounds x 4 casts, "
          "E>W>F>L, shared random first target per round, same seeds for every pattern)\n")
    print(f"Fallback: {'ON (author 2026-10-26)' if FALLBACK else 'OFF (earlier provisional no-reversal)'}. "
          f"Simulation assumptions (not canon): no jump range, MORTAR_R {MORTAR_R}, left/right roll then "
          "keep going; Mortar centred on the first target.\n")
    for name, field in FIELDS.items():
        print(f"\n## {name} ({len(field)} enemies)\n")
        print("| pattern | hits per cast | casts cut short | attacks fizzled per cast | enemies touched / fight "
              "| stacks with 3+ elements / fight | convert / unresolved / repeat / start | reactions (per fight) |")
        print("|---|---|---|---|---|---|---|---|")
        for pattern in PATTERNS:
            t = Counter()
            for seed in range(fights):
                t += fight(name, pattern, seed)
            n, h = t["casts"], max(1, t["hits"])
            rx = ", ".join(f"{k[2:]} {v / fights:.1f}" for k, v in sorted(t.items(), key=lambda kv: -kv[1]) if k.startswith("r:"))
            print(f"| {pattern} | {t['hits'] / n:.2f} | {t['short'] / n:.0%} | {t['fizzled'] / n:.2f} "
                  f"| {t['touched'] / fights:.1f} | {t['deep'] / fights:.1f} "
                  f"| {t['convert'] / h:.0%} / {t['unresolved'] / h:.0%} / {t['repeat'] / h:.0%} / {t['single'] / h:.0%} "
                  f"| {rx} |")
    print("\n## One fight, row4, triple, seed 0\n")
    log = []
    fight("row4", "triple", 0, log)
    for r, h, el, first, hit, fz, after in log:
        print(f"- R{r} Hero {h} {el:9} first E{first + 1} -> " + ", ".join(
            f"E{e + 1} [{' '.join(x[0].upper() for x in a.elements)}{' = ' + a.state if a.state else ''}{' closed' if a.closed else ''}]"
            for e, a in zip(hit, after)) + (f"  ({fz} fizzled)" if fz else ""))


def openers(fights=500):
    print("\n# Who picks the first target: shared vs independent vs spread (same layouts, seeds, E>W>F>L)\n")
    print("Same directional rule + fallback, no randomness added. Per fight (12 casts): distinct target sequences = "
          "how many different enemy orders the 12 casts produced; identical stacks = enemies whose whole element "
          "history matches another enemy's.\n")
    for pattern in ("single", "double", "triple", "quad"):
        print(f"\n## {pattern}\n")
        print("| layout | opener | distinct target sequences / 12 casts | enemies touched | distinct stacks "
              "| enemies with an identical stack | convert / unresolved / repeat / start | reactions (per fight) |")
        print("|---|---|---|---|---|---|---|---|")
        for name in FIELDS:
            for opener in ("shared", "independent", "spread"):
                t = Counter()
                for seed in range(fights):
                    t += fight(name, pattern, seed, opener=opener)
                h = max(1, t["hits"])
                rx = ", ".join(f"{k[2:]} {v / fights:.1f}" for k, v in sorted(t.items(), key=lambda kv: -kv[1]) if k.startswith("r:"))
                print(f"| {name} | {opener} | {t['sequences'] / fights:.1f} | {t['touched'] / fights:.1f} "
                      f"| {t['distinct stacks'] / fights:.1f} | {t['twins'] / fights:.1f} "
                      f"| {t['convert'] / h:.0%} / {t['unresolved'] / h:.0%} / {t['repeat'] / h:.0%} / {t['single'] / h:.0%} | {rx} |")


if __name__ == "__main__":
    self_check()
    if "--openers" in sys.argv:
        openers()
    else:
        main()
