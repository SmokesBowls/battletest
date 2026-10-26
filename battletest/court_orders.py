#!/usr/bin/env python3
"""
court_orders.py - DISPOSABLE: court_sim's "ordered" plan (one shared party target per round) with
four different hero casting orders, on the same board and the same seeds (identical targets and
start pads; only the elements differ). Travel = travel_sim.cast unchanged.

Metrics (all EXPERIMENTAL readings, no damage/HP):
  ewf triple   = earth, water, fire consecutive on one pad in an unbroken chain (court_sim C3)
  3-run        = any contact that becomes the 3rd+ consecutive DISTINCT element of an unbroken pad chain
  closed       = pad chains ended this fight (repeat or terminal Char)
  open at end  = pads still holding an unbroken chain of 2+ elements (room for more chaining)
"""

import random
import sys
from collections import Counter

sys.path.insert(0, sys.argv[1] if len(sys.argv) > 1 else ".")
import court_sim  # noqa: E402
import travel_sim  # noqa: E402
from chain_mr_sketch import Chain  # noqa: E402

ORDERS = {
    "E>W>F>L": ("earth", "water", "fire", "lightning"),
    "L>E>W>F": ("lightning", "earth", "water", "fire"),
    "E>W>F>E": ("earth", "water", "fire", "earth"),
    "F>W>E>L": ("fire", "water", "earth", "lightning"),
}
SHOW = (1, 2, 3, 4, 6, 8, 10)


def fight(level, mode, order, seed):
    rng = random.Random(f"{seed}:ordered")  # court_sim's seed for the ordered plan
    board = [[Chain() for _ in range(n)] for n in court_sim.SIZES]
    s = Counter()
    for r in range(court_sim.ROUNDS):
        target = rng.randrange(len(board))
        rng.choice(travel_sim.POOL)  # keep court_sim's RNG stream (its round element draw)
        for h, el in enumerate(order):
            rng.choice(travel_sim.POOL)  # court_sim's per-hero draw (evaluated even when unused)
            path, end = travel_sim.cast(board, level, el, mode,
                                        court_sim.Pick(f"{seed}:ordered:{r}:{h}:{mode}", target))
            s["lightning"] += el == "lightning"
            s["l_contacts"] += len(path) if el == "lightning" else 0
            s["blocked"] += end == "blocked"
            s["plasma"] += sum(p[2] == "plasma" for p in path)
            for _, _, _, b, a in path:
                s[travel_sim.kind(b, a, el)] += 1
                s["closed"] += a.closed and not b.closed and bool(b.elements)
                s["triple"] += el == "fire" and not b.closed and b.elements[-2:] == ("earth", "water")
                s["run3"] += not b.closed and a.elements != b.elements and len(set(a.elements[-3:])) == 3
                s[f"state:{a.state}"] += bool(a.state) and a.state != b.state
    s["affected"] = sum(any(p.elements for p in e) for e in board)
    s["open"] = sum(len(p.elements) >= 2 and not p.closed for e in board for p in e)
    return s


def main():
    print(f"same board, same seeds, {court_sim.FIGHTS} fights x {court_sim.ROUNDS} rounds; "
          "means per fight, focused | distributed")
    for name, order in ORDERS.items():
        print(f"\n## {name}\n")
        print("| lvl | enemies /30 | ewf triples | 3-runs | conv / unres / repeat | closed | open at end "
              "| Lightning contacts per cast / blocked | top reactions formed (focused) |")
        print("|---:|---|---|---|---|---|---|---|---|")
        for level in SHOW:
            ts = []
            for mode in ("focused", "distributed"):
                t = Counter()
                for seed in range(court_sim.FIGHTS):
                    t += fight(level, mode, order, seed)
                ts.append({k: v / court_sim.FIGHTS for k, v in t.items()})
            f = lambda fn: " \\| ".join(fn(t) for t in ts)
            g = lambda k, p=1: f(lambda t: f"{t.get(k, 0):.{p}f}")
            lt = f(lambda t: f"{t['l_contacts'] / t['lightning']:.1f} / {t['blocked'] / t['lightning']:.0%}"
                   if t.get("lightning") else "-")
            top = sorted(((k[6:], v) for k, v in ts[0].items() if k.startswith("state:")), key=lambda x: -x[1])
            print(f"| {level} | {g('affected')} | {g('triple')} | {g('run3')} "
                  f"| {f(lambda t: f'{t.get('convert', 0):.0f} / {t.get('unresolved', 0):.0f} / {t.get('repeat', 0):.0f}')} "
                  f"| {g('closed', 0)} | {g('open', 0)} | {lt} "
                  f"| {', '.join(f'{k} {v:.0f}' for k, v in top[:4])} |")


def self_check():
    # The baseline order must reproduce court_sim's ordered plan exactly.
    for lvl, mode, seed in ((1, "focused", 0), (4, "distributed", 7), (10, "focused", 3)):
        a = court_sim.fight(lvl, mode, "ordered", seed)
        b = fight(lvl, mode, ORDERS["E>W>F>L"], seed)
        assert (a["triple"], a["affected"], a["convert"], a["blocked"]) == \
               (b["triple"], b["affected"], b["convert"], b["blocked"]), (lvl, mode, seed)
    print("self-check OK: E>W>F>L reproduces court_sim's ordered plan on the same seeds")


if __name__ == "__main__":
    self_check()
    main()
